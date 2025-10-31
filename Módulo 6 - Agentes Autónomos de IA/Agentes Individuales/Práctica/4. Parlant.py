import asyncio
import parlant.sdk as p
from datetime import datetime

# pip install parlant
# Deberemos hacer un export del OPENAI_API_KEY (único proveedor)

@p.tool
async def get_available_slots(context: p.ToolContext) -> p.ToolResult:
    # Simula obtener la información de una API
    return p.ToolResult(data=["Lunes 10 AM", "Martes 2 PM", "Miércoles 1 PM"])


@p.tool
async def schedule_appointment(context: p.ToolContext, datetime: datetime) -> p.ToolResult:
    # Simula realizar la reserva
    return p.ToolResult(data=f"Reservar hora para {datetime}")


@p.tool
async def get_agreement_details(context: p.ToolContext) -> p.ToolResult:
    # Obtiene la información del convenio

    # Podemos simular la obtención del texto necesario para responder la pregunta
    convenio = {
        "seccion" : "Política de vacaciones",
        "texto" : "Todo empleado deberá disfrutar las vacaciones en manga corta..."
    }

    return p.ToolResult(
        data={
            "seccion": convenio["seccion"],
            "texto": convenio["texto"],
        }
    )

# Glosario para la conversación
async def add_domain_glossary(agent: p.Agent) -> None:
    await agent.create_term(
        name="Número de atención",
        description="El número de atención a empleado es +34 666 666 666",
    )

    await agent.create_term(
        name="Horario oficina",
        description="La oficina estará abierto de 9 AM a 5 PM, con pausa para el café a las 10 AM",
    )

    # Podemos añadir toda información del dominio que sea relevante


# Los journeys definen una estructura de conversación tipo donde dentro del margen habitual,
# esta deberá versar sobre un contexto con acciones fijas
async def create_holiday_journey(server: p.Server, agent: p.Agent) -> p.Journey:
    # Create the journey
    journey = await agent.create_journey(
        title="Realizar consultas sobre el convenio",
        description="Ayuda al empleado a aclarar sus dudas sobre el convenio",
        conditions=["El empleado quiere aclarar una duda"],
    )

    # Primero, determinamos el motivo
    t0 = await journey.initial_state.transition_to(chat_state="Determina el motivo de la duda")

    # Quiere consultar las condiciones de sus vacaciones
    t1 = await t0.target.transition_to(tool_state=get_agreement_details)

    # No está interesado en consultas sobre vacaciones
    t2 = await t1.target.transition_to(
        chat_state="Lista horas de atención presencial"
    )

    # Podemos seguir indicando acciones en base a los caminos que queramos considerar
    # Para este tipos de peticiones en concreto...

    return journey


async def main() -> None:
    async with p.Server() as server:
        agent = await server.create_agent(
            name="Agente de convenio",
            description="Es un agente con mucha paciencia y da explicaciones claras",
        )

        await add_domain_glossary(agent)
        holiday_journey = await create_holiday_journey(server, agent)

        status_inquiry = await agent.create_observation(
            "El empleado tiene dudas sobre el convenio pero no tiene claro sobre qué",
        )

        # Podemos incluir varios journeys dependiendo de lo que hable
        #await status_inquiry.disambiguate([holiday_journey, ...])

        await agent.create_guideline(
            condition="Dice que quiere hablar con una persona",
            action="Dile el horario de oficina",
        )

        await agent.create_guideline(
            condition="El empleado pregunta sobre otros temas que no sean vacaciones",
            action="Dile que solo estás programado para atender esas peticiones",
        )


if __name__ == "__main__":
    asyncio.run(main())
