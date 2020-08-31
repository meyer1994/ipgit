import io
import os
import gzip
import shlex
import subprocess
import mimetypes
import tempfile
from subprocess import PIPE

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import StreamingResponse

tempdir = tempfile.TemporaryDirectory()
subprocess.run(['git', 'init', '--bare', tempdir.name])


app = FastAPI()


@app.get('/info/refs')
async def info(service: str, req: Request):
    args = shlex.quote(service)
    args = f'{args} --stateless-rpc --advertise-refs {tempdir.name}'
    args = shlex.split(args)

    result = subprocess.run(args, stdout=PIPE, check=True)

    data = b'# service=' + service.encode() + b'\n'
    datalen = len(data) + 4
    datalen = b'%04x' % datalen
    data = datalen + data + b'0000' + result.stdout
    data = io.BytesIO(data)

    media = f'application/x-{service}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/{service}')
async def receive(service: str, req: Request):
    args = shlex.quote(service)
    args = f'{args} --stateless-rpc {tempdir.name}'
    args = shlex.split(args)

    proc = subprocess.Popen(args, stdin=PIPE, stdout=PIPE)
    async for data in req.stream():
        proc.stdin.write(data)
    proc.stdin.close()
    proc.wait()

    media = f'application/x-{service}-result'
    return StreamingResponse(proc.stdout, media_type=media)
