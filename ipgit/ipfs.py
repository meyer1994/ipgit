import shlex
import logging
import subprocess
from subprocess import PIPE, DEVNULL


logger = logging.getLogger('ipfs')
logger.setLevel(logging.INFO)


def get(qmhash: str, target: str) -> str:
    qmhash, target = shlex.quote(qmhash), shlex.quote(target)

    cmd = f'ipfs get {qmhash} --output {target}'
    cmd = shlex.split(cmd)

    logger.info('Executing: %s', cmd)
    subprocess.run(cmd, stderr=DEVNULL, check=True)

    return target
