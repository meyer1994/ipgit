import io
import stat
from typing import IO
from subprocess import PIPE
from pathlib import Path

from pfluent import Runner


class Git(object):
    def __init__(self, path: str):
        super(Git, self).__init__()
        self.path = Path(path)

    @staticmethod
    def init(path: str) -> 'Git':
        Runner('git')\
            .arg('init')\
            .arg('--bare')\
            .arg(path)\
            .run(check=True)
        return Git(path)

    def add_hook(self, name: str, hook: str) -> str:
        path = Path(self.path, 'hooks', name)
        path.write_text(hook)
        st = path.stat()
        path.chmod(st.st_mode | stat.S_IEXEC)
        return str(path)

    def inforefs(self, service: str) -> IO:
        result = Runner(service)\
            .arg('--stateless-rpc')\
            .arg('--advertise-refs')\
            .arg(self.path)\
            .run(check=True, capture_output=True)

        # Adapted from:
        #   https://github.com/schacon/grack/blob/master/lib/grack.rb
        data = b'# service=' + service.encode()
        datalen = len(data) + 4
        datalen = b'%04x' % datalen
        data = datalen + data + b'0000' + result.stdout

        return io.BytesIO(data)

    def service(self, service: str, data: bytes) -> IO:
        proc = Runner(service)\
            .arg('--stateless-rpc')\
            .arg(self.path)\
            .popen(stdin=PIPE, stdout=PIPE)

        try:
            data, _ = proc.communicate(data)
        finally:
            proc.wait()

        return io.BytesIO(data)
