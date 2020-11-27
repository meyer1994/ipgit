import io
import os
import logging
import tempfile
from enum import Enum
from pathlib import Path

from pfluent import Runner
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import StreamingResponse

from ipgit.git import Git

TEMPDIR = tempfile.TemporaryDirectory()

app = FastAPI()


logger = logging.getLogger('App')
logger.setLevel(logging.INFO)


class Service(Enum):
    receive = 'git-receive-pack'
    upload = 'git-upload-pack'


@app.get('/Qm{qmhash}/info/refs')
async def ipfsinforefs(qmhash: str, service: Service):
    qmhash = f'Qm{qmhash}'
    path = os.path.join(TEMPDIR.name, qmhash)

    Runner('ipfs')\
        .arg('get', qmhash)\
        .arg('--output', path)\
        .run(check=True)

    data = Git(path).inforefs(service.value)
    media = f'application/x-{service.value}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.get('/{path}/info/refs')
async def inforefs(path: str, service: Service):
    path = Path(TEMPDIR.name, path)
    repo = Git(path) if path.exists() else Git.init(path)

    hook = r'''
        #!/bin/sh
        echo "IPFS hash:"
        ipfs add --recursive --quieter --pin $PWD
    '''
    repo.add_hook('post-receive', hook)

    data = repo.inforefs(service.value)
    media = f'application/x-{service.value}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/{path}/{service}')
async def service(path: str, service: Service, req: Request):
    stream = req.stream()
    data = [data async for data in stream]
    data = b''.join(data)

    path = Path(TEMPDIR.name, path)
    repo = Git(path)

    data = repo.service(service.value, data)
    media = f'application/x-{service.value}-result'
    return StreamingResponse(data, media_type=media)
