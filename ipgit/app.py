import io
import os
import logging
import tempfile
from enum import Enum

import ipfshttpclient
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import StreamingResponse

import ipgit.git as git
import ipgit.ipfs as ipfs

TEMPDIR = tempfile.TemporaryDirectory()

app = FastAPI()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('App')
logger.setLevel(logging.INFO)


class Service(str, Enum):
    receive = 'git-receive-pack'
    upload = 'git-upload-pack'


@app.get('/Qm{qmhash}/info/refs')
async def ipfsinforefs(qmhash: str, service: Service):
    qmhash = f'Qm{qmhash}'
    path = os.path.join(TEMPDIR.name, qmhash)

    target = os.path.join(TEMPDIR.name, qmhash)
    ipfs.get(qmhash, target=target)

    data, media = git.inforefs(path, service)
    return StreamingResponse(data, media_type=media)


@app.get('/{path}/info/refs')
async def inforefs(path: str, service: Service):
    path = os.path.join(TEMPDIR.name, path)

    if not os.path.exists(path):
        git.init(path)

    data, media = git.inforefs(path, service)
    return StreamingResponse(data, media_type=media)


@app.post('/{path}/{service}')
async def service(path: str, service: Service, req: Request):
    path = os.path.join(TEMPDIR.name, path)

    stream = req.stream()
    data = [data async for data in stream]
    data = b''.join(data)
    data = io.BytesIO(data)

    data, media = git.service(path, service, data)
    return StreamingResponse(data, media_type=media)
