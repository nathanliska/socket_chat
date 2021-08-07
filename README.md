# socket_chat
A basic python socket chat contained in the terminal

This repository contains two python files:
- ```server.py```
- ```client.py```

```server.py``` contains four editable constants:
- ```SERVER_HOST_ADDRESS``` - The IP address the server is hosted on
- ```SERVER_PORT``` - The port the server is hosted on
- ```REQUESTS``` - The max number of concurrent connection requests
- ```MESSAGE_SIZE``` - The max message size in bytes (*recommend* to keep the same as client)

> This is run by executing the python script ```server.py```


```client.py``` contains four editable constants:
- ```SERVER_ADDRESS``` - The IP address of the server to connect to
- ```SERVER_PORT``` - The port of the server to connect to
- ```REQUESTS``` - The max number of concurrent ongoing threads
- ```MESSAGE_SIZE``` - The max message size in bytes (*recomment* to keep the same as server)

> This is run by executing the python script ```client.py```
