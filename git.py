import io
import os
import stat
import shlex
import subprocess
from typing import IO
from subprocess import PIPE


async def bare(path: str, hook: bool = False) -> None:
    path = shlex.quote(path)
    args = f'git init --bare {path}'
    args = shlex.split(args)
    subprocess.run(args, check=True)

    if hook is False:
        return

    hook = '''
    #!/bin/sh
    echo "Root IPFS hash:"
    ipfs add --recursive --quieter --pin $PWD
    '''

    path = os.path.join(path, 'hooks/post-update')
    with open(path, 'wt') as file:
        file.write(hook)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)


async def info(service: str, path: str) -> IO:
    path = shlex.quote(path)
    args = f'{service} --stateless-rpc --advertise-refs {path}'
    args = shlex.split(args)

    result = subprocess.run(args, stdout=PIPE, check=True)

    data = b'# service=' + service.encode()
    datalen = len(data) + 4
    datalen = b'%04x' % datalen
    data = datalen + data + b'0000' + result.stdout
    return io.BytesIO(data)


async def service(service: str, path: str, stream: IO) -> IO:
    path = shlex.quote(path)
    args = f'{service} --stateless-rpc {path}'
    args = shlex.split(args)

    proc = subprocess.Popen(args, stdin=PIPE, stdout=PIPE)
    async for data in stream:
        proc.stdin.write(data)
    proc.stdin.close()
    proc.wait()

    data = proc.stdout.read()
    return io.BytesIO(data)
