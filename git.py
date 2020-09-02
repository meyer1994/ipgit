import io
import os
import stat
import shlex
import subprocess
from typing import IO
from subprocess import PIPE


async def bare(path: str, hook: bool = False) -> None:
    """
    Creates a bare git repository on the passed path

    If the hook argument is True, the function will add the IPFS add command
    to the update hook fo the repo

    Args:
        path: String with path where to create the repository
        hook: Boolean wether or not to create the update hook. Defaults to
        False
    """
    path = shlex.quote(path)
    args = f'git init --bare {path}'
    args = shlex.split(args)
    subprocess.run(args, check=True)

    if hook is False:
        return

    hook = '''
    #!/bin/sh
    echo "IPFS hash:"
    ipfs add --recursive --quieter --pin $PWD
    '''

    path = os.path.join(path, 'hooks/post-update')
    with open(path, 'wt') as file:
        file.write(hook)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)


async def info(service: str, path: str) -> IO:
    """ Returns repository information for smart HTTP backend as a stream """
    path = shlex.quote(path)
    args = f'{service} --stateless-rpc --advertise-refs {path}'
    args = shlex.split(args)

    result = subprocess.run(args, stdout=PIPE, check=True)

    # Adapted from:
    #   https://github.com/schacon/grack/blob/master/lib/grack.rb
    data = b'# service=' + service.encode()
    datalen = len(data) + 4
    datalen = b'%04x' % datalen
    data = datalen + data + b'0000' + result.stdout

    return io.BytesIO(data)


async def service(service: str, path: str, stream: IO) -> IO:
    """ Used by `git-upload-pack` and `git-receive-pack` when updating refs """
    path = shlex.quote(path)
    args = f'{service} --stateless-rpc {path}'
    args = shlex.split(args)

    # We pass the stream bit by bit to avoid loading
    # everything into memory at once
    proc = subprocess.Popen(args, stdin=PIPE, stdout=PIPE)
    async for data in stream:
        proc.stdin.write(data)
    proc.stdin.close()
    proc.wait()

    data = proc.stdout.read()
    return io.BytesIO(data)
