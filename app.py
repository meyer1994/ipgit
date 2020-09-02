import io
import os
import tempfile
from enum import Enum

import ipfshttpclient
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import StreamingResponse

import git

TEMPDIR = tempfile.TemporaryDirectory()


class Service(str, Enum):
    receive = 'git-receive-pack'
    upload = 'git-upload-pack'


app = FastAPI()
ipfs = ipfshttpclient.connect()


@app.get('/Qm{qmhash}/info/refs')
async def info(qmhash: str, service: Service):
    qmhash = 'Qm' + qmhash
    ipfs.get(qmhash, target=TEMPDIR.name)
    path = os.path.join(TEMPDIR.name, qmhash)
    data = await git.info(service, path)
    media = f'application/x-{service}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/Qm{qmhash}/{service}')
async def service(qmhash: str, service: Service, req: Request):
    stream = req.stream()
    qmhash = 'Qm' + qmhash
    path = os.path.join(TEMPDIR.name, qmhash)
    data = await git.service(service, path, stream)
    media = f'application/x-{service}-result'
    return StreamingResponse(data, media_type=media)


@app.get('/info/refs')
async def info(service: Service):
    with tempfile.TemporaryDirectory() as tempdir:
        await git.bare(tempdir)
        data = await git.info(service, tempdir)
    media = f'application/x-{service}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/{service}')
async def service(service: Service, req: Request):
    stream = req.stream()
    with tempfile.TemporaryDirectory() as tempdir:
        await git.bare(tempdir, hook=True)
        data = await git.service(service, tempdir, stream)
    media = f'application/x-{service}-result'
    return StreamingResponse(data, media_type=media)
