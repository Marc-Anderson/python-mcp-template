#
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)

# #
# uv init
# uv add "mcp[cli]"
# # you can download the mcp inspector to test it with
# source .venv/bin/activate
# mcp dev server.py
#
# to connect to the server you need to use an `mcp client` using the same mcp package used to create the server
# if you are using stdio, the client will start the server, so they can communicate on stdio
# you can also use (streamable-)http, but you will still need to use the mcp package so the client can understand how to use the server
#
# this is just for understanding how it works, you should just pick one in a real application
USE_STDIO_MCP_COMMUNICATION = True
#
#


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """include lifespan context for the server so the same objects can be used across all requests without opening/closing them on every request. this also allows you to set up the context, such as loading a dataframe or connecting to a database and then shut them down when the server is stopped."""

    # setup the things you want to share across the server's lifespan
    try:
        yield {
            "test": "this is a test value from lifespan context",
            "query": lambda x: "you queried " + x + "!",
            "df": "this could be a dataframe",
        }
    finally:
        # no cleanup needed because we arent using a database or anything that would required closing or disconnecting
        pass
    #
    # you can use the context within a function or tool like this:
    # ctx = mcp.get_context()
    # df = ctx.request_context.lifespan_context["df"]


####
# there are multiple ways to serve the FastMCP server
####

if USE_STDIO_MCP_COMMUNICATION:

    # stdio: create a named server with the lifespan context
    mcp = FastMCP("FastMCP Server Template", version="1.0.0", lifespan=app_lifespan)

else:

    # stateless server (no session persistence, no sse stream with supported client)
    mcp = FastMCP(
        "FastMCP Server Template",
        version="1.0.0",
        lifespan=app_lifespan,
        stateless_http=True,
        json_response=True,
    )

    # you could also use the normal
    # stateless server (no session persistence)
    # mcp = FastMCP(
    #     "FastMCP Server Template",
    #     version="1.0.0",
    #     lifespan=app_lifespan,
    #     stateless_http=True,
    # )

#  region tools


# simple tool example
@mcp.tool()
def add(a: int, b: int) -> int:
    """add two numbers"""
    return a + b


# tool that uses the lifespan context
@mcp.tool()
async def test_tool(input_value: str):
    """
    A test tool to check if the server is running
    """
    # get the context from the request
    ctx = mcp.get_context()
    # log a message to the server logs
    await ctx.info("Test tool called with value: " + input_value)
    # get a value from the lifespan context
    test_value = ctx.request_context.lifespan_context["test"]

    return f"Hello, {test_value}!"


@mcp.tool()
def query_db() -> str:
    """Tool that uses initialized resources"""
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context["db"]
    return db.query(table="example_table", limit=5)


# endregion tools

# region prompts


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


# endregion prompts

# region resources


@mcp.resource("config://app")
def get_config() -> str:
    """static configuration data"""
    return "App configuration here"


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """dynamic user data"""
    return f"Profile data for user {user_id}"


# endregion resources


if __name__ == "__main__":

    if USE_STDIO_MCP_COMMUNICATION:

        mcp.run()

    else:

        mcp.run(transport="streamable-http")


# if you are using streamable-http, you can run the server and poke around with curl, but you will need the mcp package for a real integration
# uv run server.py --log-level DEBUG
# curl POST http://127.0.0.1:8000/mcp/ -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc": "2.0","id": 1,"method": "tools/list","params": {"cursor": "optional-cursor-value"}}' --verbose

# example_output = {
#     "jsonrpc": "2.0",
#     "id": 1,
#     "result": {
#         "tools": [
#             {
#                 "name": "add",
#                 "description": "add two numbers",
#                 "inputSchema": {
#                     "properties": {
#                         "a": {"title": "A", "type": "integer"},
#                         "b": {"title": "B", "type": "integer"},
#                     },
#                     "required": ["a", "b"],
#                     "title": "addArguments",
#                     "type": "object",
#                 },
#             },
#             {
#                 "name": "test_tool",
#                 "description": "\nA test tool to check if the server is running\n",
#                 "inputSchema": {
#                     "properties": {
#                         "input_value": {"title": "Input Value", "type": "string"}
#                     },
#                     "required": ["input_value"],
#                     "title": "test_toolArguments",
#                     "type": "object",
#                 },
#             },
#             {
#                 "name": "query_db",
#                 "description": "Tool that uses initialized resources",
#                 "inputSchema": {
#                     "properties": {},
#                     "title": "query_dbArguments",
#                     "type": "object",
#                 },
#             },
#         ]
#     },
# }
