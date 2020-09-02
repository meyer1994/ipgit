import io
import os
import shutil
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
async def qminfo(qmhash: str, service: Service):
    """
    Used when cloning repositories based on their hashes

    It will download the repository represented by the hash into the temporary
    directory before starting. Yes, it will probably break if someone passes
    a big dataset's hash. The repository is downloaded and will continue
    downloaded until it's data is fetched in the next request made by git.

    Args:
        qmhash: String with the hash, without `Qm` at the start. This is done
            in order to make fastapi's routing get it more easily
        service: Which service from git smart http backend to use

    Returns:
        A streaming response with the data from the repository
    """
    qmhash = 'Qm' + qmhash
    ipfs.get(qmhash, target=TEMPDIR.name)
    path = os.path.join(TEMPDIR.name, qmhash)
    data = await git.info(service, path)
    media = f'application/x-{service}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/Qm{qmhash}/{service}')
async def qmservice(qmhash: str, service: Service, req: Request):
    """
    Returns repo main data, files, objects, etc. to caller

    This function is usually called just after the function `qminfo`. It
    assumes that the repository was already downloaded by the `qminfo`
    function. It will try to delete it from disk afterwards.

    Args:
        qmhash: String with the hash, without `Qm` at the start. This is done
            in order to make fastapi's routing get it more easily
        service: Which service from git smart http backend to use
        req: Starlette request for this request

    Returns:
        A streaming response with the objects of the repository
    """
    stream = req.stream()
    qmhash = 'Qm' + qmhash
    path = os.path.join(TEMPDIR.name, qmhash)
    data = await git.service(service, path, stream)
    shutil.rmtree(path, ignore_errors=True)
    media = f'application/x-{service}-result'
    return StreamingResponse(data, media_type=media)


@app.get('/info/refs')
async def info(service: Service):
    """
    Main entry point of the service

    When using `git push` this endpoint will be called by git to check some
    things about the repository. However, it will have the same effect every
    time it is called. That is because this endpoint creates an empty, bare,
    repository to represent the remote state. This way, all times you push your
    code to this repository, it will go to the next step, the upload.

    Args:
        service: Which service from git smart http backend to use

    Returns:
        A streaming response with the objects of the repository
    """
    with tempfile.TemporaryDirectory() as tempdir:
        await git.bare(tempdir)
        data = await git.info(service, tempdir)
    media = f'application/x-{service}-advertisement'
    return StreamingResponse(data, media_type=media)


@app.post('/{service}')
async def service(service: Service, req: Request):
    """
    Called after `info` function by git

    It will receive all files from your repository, save them in a directory
    and upload all of them to a local IPFS node. The upload is performed via a
    `post-update` hook. This way the IPFS hash is returned to the caller in the
    terminal.

    Args:
        service: Which service from git smart http backend to use
        req: Starlette request for this request

    Returns:
        A streaming response with the objects of the repository
    """
    stream = req.stream()
    with tempfile.TemporaryDirectory() as tempdir:
        await git.bare(tempdir, hook=True)
        data = await git.service(service, tempdir, stream)
    media = f'application/x-{service}-result'
    return StreamingResponse(data, media_type=media)
