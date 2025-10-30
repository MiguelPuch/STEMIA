"""
This example demonstrates how to use multiple MCP servers in a single agent.

Prerequisites:
- Set the environment variable "ACCUWEATHER_API_KEY" for the weather MCP tools.
- BRAVE_API_KEY also from https://brave.com/search/api/
- You can get the API key from the AccuWeather website: https://developer.accuweather.com/
"""

import asyncio
from os import getenv

from agno.agent import Agent
from agno.tools.mcp import MultiMCPTools
from agno.models.google import Gemini

from dotenv import load_dotenv

# Variables de entorno
load_dotenv(override=True)

async def run_agent(message: str) -> None:
    # Initialize the MCP tools
    mcp_tools = MultiMCPTools(
        [
            "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt",
            "npx -y @modelcontextprotocol/server-brave-search",
            #"npx -y @timlukahorstmann/mcp-weather"
        ],
        env={
            "BRAVE_API_KEY": getenv("BRAVE_API_KEY"),
            "ACCUWEATHER_API_KEY" : getenv("ACCUWEATHER_API_KEY"),
        },
        timeout_seconds=30,
    )

    # Connect to the MCP servers
    await mcp_tools.connect()

    # Use the MCP tools with an Agent
    agent = Agent(
        model=Gemini(id="gemini-2.5-flash", temperature=0),
        tools=[mcp_tools],
        markdown=True,
        show_tool_calls=True,
    )
    await agent.aprint_response(message)

    # Close the MCP connection
    await mcp_tools.close()


# Example usage
if __name__ == "__main__":
    asyncio.run(run_agent("¿Hay algún alojamiento disponible hoy 5 de Septiembre del 2025 en Barcelona para dos personas?"))
    asyncio.run(run_agent("¿Cual es la forma más rápida de llegar a Barcelona desde Santander?"))
    #asyncio.run(run_agent("¿Lloverá en Barcelona?"))
