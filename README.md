**Operating Systems Virtualization project**


Distributed File System across containerized nodes, and scripts with monitoring this system.


**Includes:**

-Name meta server (HTTP)

-Storage nodes for files (there are 3 by default)

-User commands (get, put, list and delete)

-Resource monitor

-Script for checking file consistency across the nodes


**Setup**
1. Clone the repo

2. Start all containers with `docker compose up --build`

3. Create test files (or try files that are already in your memory)

4. Run the terminal commands within the root folder for storing files

`````bash
python3 client/client.py put <filename>

python3 client/client.py delete <filename>

python3 client/client.py get <filename> 

python3 client/client.py get <filename> --peak #For looking at files contents if it's a text file

python3 client/client.py list
`````

5. Run bash scripts for monitoring (in the other terminal)

6. Report folder is for logs 


It is the project for University of Messina for the Module B of Operating Systems course
