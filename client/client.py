import urllib.request
import urllib.error
import sys
import json
import os

NAMESERVER_HOST = os.environ.get('NAMESERVER_HOST', 'localhost')
NAMESERVER_PORT = int(os.environ.get('NAMESERVER_PORT', 5000))
NODE_PORT = int(os.environ.get('NODE_PORT', 5001))

NODE_HOST_MAP = {
    'node-a': f'localhost:5001',
    'node-b': f'localhost:5002',
    'node-c': f'localhost:5003',
}

NAMESERVER = f'http://{NAMESERVER_HOST}:{NAMESERVER_PORT}'

def put(filename):
    if not os.path.exists(filename):
        print(f'ERROR: file {filename} does not exist locally')
        return
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f'Registering {filename} in the name server')
    try:
        req = urllib.request.Request(
            f'{NAMESERVER}/register/{filename}',
            method='POST',
            data=b'',
        )
        with urllib.request.urlopen(req) as res:
            response = json.loads(res.read())
            nodes = response['nodes']
            status = response['status']
        if status != 'registered':
            print(f'{filename} already exists, try deleting first')
            return
    except urllib.error.URLError as e:
        print(f'ERROR:Could not reach name server - {e}')
        return
    print(f'Nodes assigned are: {nodes}')

    for node in nodes:
        try:
            req = urllib.request.Request(
                f'http://{get_node_address(node)}/store/{filename}',
                method='POST',
                data=data,
            )
            with urllib.request.urlopen(req) as res:
                result = res.read().decode()
                print(f'{node} -> {result}')
        except urllib.error.URLError as e:
            print(f'Could not reach {node} - {e}')

def get(filename, peek=False):
    try:
        with urllib.request.urlopen(f'{NAMESERVER}/lookup/{filename}') as res:
            response = json.loads(res.read())
            nodes = response['nodes']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f'ERROR: "{filename}" not found')
        else:
            print(f'ERROR: nameserver returned {e.code}')
        return
    except urllib.error.URLError as e:
        print(f'Could not reach server - {e}')
        return

    for node in nodes:
        print("Fetching")
        try:
            with urllib.request.urlopen(
                f'http://{get_node_address(node)}/fetch/{filename}'
            ) as res:
                data = res.read()
            
            if peek:
                try:
                    print(f'\n--{filename} from {node}--')
                    print(data.decode('utf-8'))
                    print(f'\n--end of the file--')
                except UnicodeDecodeError:
                    print(f'Binary file - {len(data)} bytes')
            else:
                with open(filename, 'wb') as f:
                    f.write(data)
                print(f'{filename} was retrieved from {node}')
            return
        except urllib.error.URLError as e:
            print(f'Could not reach {node} - {e}')
    print(f'All nodes failed, file unavailable!')

def list_files():
    try:
        with urllib.request.urlopen(f'{NAMESERVER}/list') as res:
            file_map = json.loads(res.read())
        
        if not file_map:
            print("DFS is empty")
            return
        
        print("Files in DFS:")
        print("-" * 30)
        for filename, nodes in file_map.items():
            print(f'{filename}: {",".join(nodes)}')
        print("-" * 30)
    except urllib.error.URLError as e:
        print(f'Could not reach server - {e}')

def delete(filename):
    try:
        with urllib.request.urlopen(f'{NAMESERVER}/lookup/{filename}') as res:
            response = json.loads(res.read())
            nodes = response['nodes']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f'ERROR: "{filename}" not found')
        else:
            print(f'ERROR: nameserver returned {e.code}')
        return
    except urllib.error.URLError as e:
        print(f'Could not reach server - {e}')
        return
    
    for node in nodes:
        print("Deleting")
        try:
            req = urllib.request.Request(
                f'http://{get_node_address(node)}/delete/{filename}',
                method='DELETE',
            )
            with urllib.request.urlopen(req) as res:
                result = res.read().decode()
                print(f'{node} -> {result}')
        except urllib.error.URLError as e:
            print(f'Could not reach {node} - {e}')
    
    try:
        req = urllib.request.Request(
            f'{NAMESERVER}/delete/{filename}',
            method='DELETE',
        )
        with urllib.request.urlopen(req) as res:
            print(f'{res.read().decode()}')
    except urllib.error.URLError as e:
        print(f'Could not reach server - {e}')

def print_usage():
    print("Usage")
    print(" python3 client.py put <filename>")
    print(" python3 client.py get <filename>")
    print(" python3 client.py delete <filename>")
    print(" python3 client.py list")

def get_node_address(node):
    return NODE_HOST_MAP.get(node, f'{node}:{NODE_PORT}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]

    if command == 'put' and len(sys.argv) == 3:
        put(sys.argv[2])
    elif command == 'get' and len(sys.argv) == 3:
        get(sys.argv[2])
    elif command == 'get' and len(sys.argv) == 4 and sys.argv[3] == '--peak':
        get(sys.argv[2], True)
    elif command == 'list':
        list_files()
    elif command == 'delete' and len(sys.argv) == 3:
        delete(sys.argv[2])
    else:
        print_usage()
        sys.exit(1)