# mcp template

# setup

## run the mcp server and test it in the mcp inspector

mcp doesnt do anything unless you have a client & server, the inspector acts like a client so you can test. if you just start the server listening on stdio with something like `uv run server.py --log-level DEBUG` nothing will happen.

```sh
uv init
uv add "mcp[cli]"
source .venv/bin/activate
# this will download the mcp inspector to test your server
mcp dev server.py
```

## start the full mcp application(server and client)

you can start the mcp client, which will spin up the mcp server and communicate via stdio

```sh
python3 stdio_client.py
```


## start the mcp server and communicate via http

this isnt included here, but you can run the mcp server to listen on http instead of stdio, then you would create an mcp client. i have setup a test so you can see how that works. if you set `USE_STDIO_MCP_COMMUNICATION` to `False` in the server, and run `uv run server.py --log-level DEBUG`, it will start the server listening on http. then you can mess around with it using curl. 

```sh
curl POST http://127.0.0.1:8000/mcp/ -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc": "2.0","id": 1,"method": "tools/list","params": {"cursor": "optional-cursor-value"}}' --verbose
```


# resources

- [mcp python sdk](https://github.com/modelcontextprotocol/python-sdk)