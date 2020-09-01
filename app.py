import os
import tempfile

import ipfshttpclient
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import StreamingResponse

import git

TEMPDIR = tempfile.TemporaryDirectory()

app = FastAPI()
ipfs = ipfshttpclient.connect('/dns/ipfs.io/tcp/443/https')


@app.get('/Qm{path}/info/refs')
async def mhash(path: str, service: git.Service):
    mhash = 'Qm' + path
    ipfs.get(mhash, target=TEMPDIR.name)
    path = os.path.join(TEMPDIR.name, mhash)
    return await info(path, service)


@app.get('/{path}/info/refs')
async def info(path: str, service: git.Service):
    path = os.path.join(TEMPDIR.name, path)
    await git.bare(path)
    data = await git.info(service, path)
    media = f'application/x-{service}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/{path}/{service}')
async def service(path: str, service: git.Service, req: Request):
    stream = req.stream()
    path = os.path.join(TEMPDIR.name, path)
    data = await git.service(service, path, stream)
    ipfs.add(path, recursive=True, pin=True)
    media = f'application/x-{service}-result'
    return StreamingResponse(data, media_type=media)
