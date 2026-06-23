from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
import random

PORT = int(os.environ.get('NAMESERVER_PORT', 5000))
NODES = os.environ.get('NODES', 'node-a,node-b,node-c').split(',')
REPLICATION_FACTOR = 2
METADATA_FILE = '/app/metadata.json'

file_map = {}

def load_metadata():
    global file_map
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            file_map = json.loads(f)
        print(f'Loaded {len(file_map)} file(s) from metadata store')
    else:
        print('Starting fresh, no files detected in the metadata')

def save_metadata():
    with open(METADATA_FILE, 'w') as f:
        json.dump(file_map, f)

class NameServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/register/'):
            self._handle_register()
        else:
            self._respond(404, 'NOT FOUND')
    
    def do_GET(self):
        if self.path.startswith('/lookup/'):
            self._handle_lookup()
        elif self.path == '/list':
            self._handle_list()
        else:
            self._respond(404, 'NOT FOUND')
    
    def do_DELETE(self):
        if self.path.startswith('/delete/'):
            self._handle_delete()
        else:
            self._respond(404, 'NOT FOUND')

    def _handle_register(self):
        filename = self.path[len('/register/'):]
        response = None
        if filename in file_map:
            response = json.dumps({
                'nodes': file_map[filename],
                'status': 'exists'
            })
            self._respond(200, response)
            return
        chosen_nodes = random.sample(NODES, REPLICATION_FACTOR)
        file_map[filename] = chosen_nodes
        save_metadata()
        response = json.dumps({
            'nodes': chosen_nodes,
            'status': 'registered'
            })
        self._respond(200, response)

    def _handle_lookup(self):
        filename = self.path[len('/lookup/'):]
        if filename in file_map:
            response = json.dumps({'nodes': file_map[filename]})
            self._respond(200, response)
        else:
            self._respond(404, 'FILE NOT FOUND')

    def _handle_list(self):
        response = json.dumps(file_map)
        self._respond(200, response)

    def _handle_delete(self):
        filename = self.path[len('/delete/'):]
        if filename in file_map:
            del file_map[filename]
            save_metadata()
            self._respond(200, 'DELETED')
        else:
            self._respond(404, 'FILE NOT FOUND')

    def _respond(self, code, body):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f'[nameserver] {args[0]}')

if __name__ == '__main__':
    load_metadata()
    print(f'Name server is running on {PORT} port')
    print(f'Storage nodes are {NODES}')
    server = HTTPServer(('0.0.0.0', PORT), NameServerHandler)
    server.serve_forever()