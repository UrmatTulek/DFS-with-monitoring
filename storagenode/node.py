from http.server import BaseHTTPRequestHandler, HTTPServer
import os

STORAGE_DIR = '/app/storage'
PORT = int(os.environ.get('NODE_PORT', 5001))

class StorageHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/store/'):
            self._handle_store()
        else:
            self._respond(404, 'NOT FOUND')

    def do_GET(self):
        if self.path.startswith('/fetch/'):
            self._handle_fetch()
        elif self.path == '/list':
            self._handle_list()
        else:
            self._respond(404, 'NOT FOUND')

    def do_DELETE(self):
        if self.path.startswith('/delete/'):
            self._handle_delete()
        else:
            self._respond(404, 'NOT FOUND')

    def _handle_store(self):
        filename = self.path[len('/store/'):]
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        self._respond(200, 'STORED')

    def _handle_fetch(self):
        filename = self.path[len('/fetch/'):]
        filepath = os.path.join(STORAGE_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = f.read()
            self._respond(200, data)
        else:
            self._respond(404, 'FILE NOT FOUND')
    
    def _handle_list(self):
        files = os.listdir(STORAGE_DIR)
        response = '\n'.join(files) if files else 'EMPTY'
        self._respond(200, response)

    def _handle_delete(self):
        filename = self.path[len('/delete/'):]
        filepath = os.path.join(STORAGE_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            self._respond(200, 'DELETED')
        else:
            self._respond(404, 'FILE NOT FOUND')

    def _respond(self, code, body):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def log_message(self, format, *args):
        print(f'[{self.server.server_address[1]}] {args[0]}')

if __name__ == '__main__':
    os.makedirs(STORAGE_DIR, exist_ok=True)
    server = HTTPServer(('0.0.0.0', PORT), StorageHandler)
    print(f'Server is running on port {PORT}')
    server.serve_forever()