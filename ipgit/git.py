import io
import os
import stat
import shlex
import logging
import functools
import subprocess
from typing import IO
from subprocess import PIPE


logger = logging.getLogger('git')
logger.setLevel(logging.INFO)


def init(path: str) -> str:
    path = shlex.quote(path)

    cmd = f'git init --bare {path}'
    cmd = shlex.split(cmd)

    logger.info('Excuting: %s', cmd)
    subprocess.run(cmd, check=True)

    data = r'''
        #!/bin/sh
        pwd
        echo "IPFS hash:"
        ipfs add --recursive --quieter --pin $PWD
    '''
    data = io.StringIO(data)

    reader = functools.partial(data.read, 2**20)
    reader = iter(reader, '')

    hook = os.path.join(path, 'hooks', 'post-receive')
    logger.info('Copying `post-receive` hook to: %s', hook)

    with open(hook, 'wt') as file:
        for chunk in reader:
            file.write(chunk)

    st = os.stat(hook)
    os.chmod(hook, st.st_mode | stat.S_IEXEC)

    return path


def inforefs(path: str, service: str) -> (IO, str):
    path, service = shlex.quote(path), shlex.quote(service)

    cmd = f'{service} --stateless-rpc --advertise-refs {path}'
    cmd = shlex.split(cmd)

    logger.info('Excuting: %s', cmd)
    result = subprocess.run(cmd, stdout=PIPE, check=True)

    # Adapted from:
    #   https://github.com/schacon/grack/blob/master/lib/grack.rb
    data = b'# service=' + service.encode()
    datalen = len(data) + 4
    datalen = b'%04x' % datalen
    data = datalen + data + b'0000' + result.stdout

    return io.BytesIO(data), f'application/x-{service}-advertisement'


def service(path: str, service: str, data: IO) -> (IO, str):
    path, service = shlex.quote(path), shlex.quote(service)

    cmd = f'{service} --stateless-rpc {path}'
    cmd = shlex.split(cmd)

    data = data.read()

    logger.info('Excuting: %s', cmd)
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE)
    data, _ = proc.communicate(data)
    proc.wait()

    data = io.BytesIO(data)
    return data, f'application/x-{service}-result'
