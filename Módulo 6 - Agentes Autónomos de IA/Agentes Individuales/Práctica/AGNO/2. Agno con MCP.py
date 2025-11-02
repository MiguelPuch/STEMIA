import asyncio
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIModel  
from agno.tools.mcp import MCPTools

from dotenv import load_dotenv

# Variables de entorno
load_dotenv(override=True)

async def run_mcp_agent(message: str) -> None:
    """Explorador del sistema de ficheros"""

    file_path = str(Path(__file__).parent.parent.parent.parent)

    # Inicializa las herramientas MCP
    mcp_tools = MCPTools(f"npx -y @modelcontextprotocol/server-filesystem {file_path}")

    # Conexión con el servidor MCP
    await mcp_tools.connect()

    # Usa las herramientas MCP con un agente OpenAI
    agent = Agent(
        model=OpenAIModel(id="gpt-4.1", temperature=0),  
        tools=[mcp_tools],
        instructions=dedent("""\
            Eres un asistente para el sistema de ficheros:

            - Navega el sistema de ficheros en profundidad para responder preguntas
            - Utiliza la herramienta list_allowed_directories para encontrar directorios con acceso y poder investigar más
            - Provee contexto sobre los ficheros a explorar
            - Utiliza títulos y markdown para realzar el contenido de respuesta
            - Sé conciso y solo muestra información relevante\
        """),
        markdown=True,
        show_tool_calls=True,
    )

    # Ejecuta el agente
    await agent.aprint_response(message, stream=True)

    # Cierra la conexión con MCP
    await mcp_tools.close()


# Ejemplo de uso
if __name__ == "__main__":
    asyncio.run(run_mcp_agent("¿Qué licencia tiene este proyecto?"))
