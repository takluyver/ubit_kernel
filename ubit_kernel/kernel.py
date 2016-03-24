import time

from ipykernel.kernelbase import Kernel
from .ubit import connect

__version__ = '0.2'

class MicrobitKernel(Kernel):
    implementation = 'ubit_kernel'
    implementation_version = __version__

    language_info = {'name': 'python',
                     'version': '3',
                     'mimetype': 'text/x-python',
                     'file_extension': '.py',
                     'codemirror_mode': {'name': 'python',
                                         'version': 3},
                     'pygments_lexer': 'python3',
                    }

    help_links = [
        {'text': 'micro:bit MicroPython',
         'url': 'http://microbit-micropython.readthedocs.org/en/latest/index.html'
        },
    ]

    banner = "Welcome to MicroPython on the BBC micro:bit"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial = connect()

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        self.serial.write(code.encode('utf-8') + b'\x04')
        result = bytearray()
        while not result.endswith(b'\x04>'):
            time.sleep(0.1)
            result.extend(self.serial.read_all())
        import sys
        print('Read', repr(result), file=sys.__stderr__)

        assert result.startswith(b'OK')
        out, err = result[2:-2].split(b'\x04', 1)
        if out:
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stdout',
                'text': out.decode('utf-8', 'replace')
            })
        if err:
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stderr',
                'text': err.decode('utf-8', 'replace')
            })

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}
