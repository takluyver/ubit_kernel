import ast
import re
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

    def run_code(self, code):
        '''Run a string of code, return strings for stdout and stderr'''
        self.serial.write(code.encode('utf-8') + b'\x04')
        result = bytearray()
        while not result.endswith(b'\x04>'):
            time.sleep(0.1)
            result.extend(self.serial.read_all())
        import sys
        print('Read', repr(result), file=sys.__stderr__)

        assert result.startswith(b'OK')
        out, err = result[2:-2].split(b'\x04', 1)
        return out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        out, err = self.run_code(code)
        if out:
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stdout',
                'text': out
            })
        if err:
            self.send_response(self.iopub_socket, 'stream', {
                'name': 'stderr',
                'text': err
            })

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}

    def _eval(self, expr):
        out, err = self.run_code('print({})'.format(expr))
        return ast.literal_eval(out)

    def do_complete(self, code, cursor_pos):
        import sys
        print('completing on', repr(code), file=sys.__stderr__)
        code = code[:cursor_pos]
        m = re.search(r'(\w+\.)*(\w+)?$', code)
        if m:
            prefix = m.group()
            print('prefix', repr(prefix), file=sys.__stderr__)
            if '.' in prefix:
                obj, prefix = prefix.rsplit('.')
                names = self._eval('dir({})'.format(obj))
            else:
                names = self._eval('dir()')
            print('names', names, file=sys.__stderr__)
            matches = [n for n in names if n.startswith(prefix)]
            return {'matches': matches,
                    'cursor_start': cursor_pos - len(prefix), 'cursor_end': cursor_pos,
                    'metadata': {}, 'status': 'ok'}
        else:
            return {'matches': [],
                    'cursor_start': cursor_pos, 'cursor_end': cursor_pos,
                    'metadata': {}, 'status': 'ok'}
