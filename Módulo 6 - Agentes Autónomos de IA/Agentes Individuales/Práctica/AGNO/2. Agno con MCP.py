import asyncio
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.mcp import MCPTools

from dotenv import load_dotenv

# Variables de entorno
load_dotenv(override=True)

async def run_mcp_agent(message: str) -> None:
    """Explorador del sistema de ficheros"""

    file_path = str(Path(__file__).parent.parent.parent.parent)

    # Initialize the MCP tools
    mcp_tools = MCPTools(f"npx -y @modelcontextprotocol/server-filesystem {file_path}")

    # Connect to the MCP server
    await mcp_tools.connect()

    # Use the MCP tools with an Agent
    agent = Agent(
        model=Gemini(id="gemini-2.5-flash", temperature=0),
        tools=[mcp_tools],
        instructions=dedent("""\
            Eres un asistente para el sistema de ficheros:

            - Navega el sistema de ficheros en profundidad para responder preguntas
            - Utiliza la herramienta list_allowed_directories para encontrar directorios con acceso y poder investigar más
            - Provee contexto sobre los ficheros a explorar
            - Utiliza títulos y markdown para realzar el contenido de respuesta
            - Se conciso y solo muestra información relevante\
        """),
        markdown=True,
        show_tool_calls=True,
    )

    # Run the agent
    await agent.aprint_response(message, stream=True)

    # Close the MCP connection
    await mcp_tools.close()


# Example usage
if __name__ == "__main__":
    # Basic example - exploring project license
    asyncio.run(run_mcp_agent("¿Qué licencia tiene este proyecto?"))
