from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import logging

logging.basicConfig(level=logging.INFO)

#
# if you are building an application and you want your app to communicate with you mcp server, you will need a `client`
# to connect to the server you need to use an `mcp client` using the same mcp package used to create the server
# if you are using stdio, youll include `StdioServerParameters` which will start the server, so they can communicate on stdio
# you can also use (streamable-)http, but you will still need to use the mcp package so the client can understand how to use the server
#
# this is just a demo, for building an application, use this link as a starting point as it has a perfect example of how to use the mcp client
# https://modelcontextprotocol.io/quickstart/client#python
#

# create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python3",  # Executable
    args=["server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)


# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()

            # Get a prompt
            prompt = await session.get_prompt(
                "review_code", arguments={"code": "print('Hello, world!')"}
            )
            with open("output.txt", "a") as f:
                f.write("PROMPTS:\n" + str(prompt) + "\n")

            # List available resources
            resources = await session.list_resources()
            with open("output.txt", "a") as f:
                f.write("RESOURCES:\n" + str(resources) + "\n")

            # List available tools
            tools = await session.list_tools()
            with open("output.txt", "a") as f:
                f.write("TOOLS:\n" + str(tools) + "\n")

            # Read a resource
            content, mime_type = await session.read_resource("config://app")
            with open("output.txt", "a") as f:
                f.write("CONFIG:\n" + str(content) + "\n")

            # Call a tool
            result = await session.call_tool(
                "test_tool", arguments={"input_value": "nice friend"}
            )

            with open("output.txt", "a") as f:
                f.write("RESULT:\n" + str(result) + "\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
