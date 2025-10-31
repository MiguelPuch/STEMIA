# Cargamos librerías

import chainlit as cl
import asyncio
import random
import datetime
from datetime import datetime
import os
from collections import defaultdict
import statistics
from langchain.memory import ConversationBufferMemory



# Cargamos funciones

from chatbot.prompt import generar_prompt_para_formacion
from utils.utils import cargar_pdf_texto
from chatbot.chatbot import ChatbotPreguntas
import os
from dotenv import load_dotenv
from chatbot.prompt import generar_prompt_para_formacion
from utils.utils import calcular_puntuacion, cargar_pdf_texto, calcular_pesos_reales, crear_pdf_informe_completo_1
from utils.historial import cargar_historial_usuario
from utils.historial_objetivos import cargar_historial_usuario_objetivos
from chainlit.server import app
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# Sirve archivos estáticos desde /public
app.mount("/public", StaticFiles(directory="public"), name="public")

# Sirve la página HTML en la raíz /
@app.get("/")
def serve_landing_page():
    return FileResponse("web/index.html")


import logging
logger = logging.getLogger(__name__)
load_dotenv()
chatbot = ChatbotPreguntas(api_key=os.getenv("GOOGLE_API_KEY"), model_name="gemini-2.0-flash")


PDF_PATH = r"./Classic_Fit.pdf"
TEXTO_PDF = cargar_pdf_texto(PDF_PATH)
SECCIONES_FORMACION = chatbot.extraer_secciones_pdf()


#######################
##### USUARIOS  #######
#######################

@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    if (username, password) == ("scala", "salascala123"):
        return cl.User(
            identifier="admin",
            display_name="Scala",
            metadata={"role": "admin", "provider": "credentials"},
        )
    elif (username, password) == ("c.datos17@salascala.com", "Anna"):
        return cl.User(
            identifier="anna123", 
            display_name="Anna",
            metadata={"role": "user", "provider": "credentials"},
        )
        
    elif (username, password) == ("ntorredi@ull.edu.es", "ntorredi_123"):
        return cl.User(
            identifier="Néstor", 
            display_name="Néstor",
            metadata={"role": "user", "provider": "credentials"},
        )
    elif (username, password) == ("test.ull", "test.ull_681"):
        return cl.User(
            identifier="test.ull", 
            display_name="Usuario de prueba ULL",
            metadata={"role": "user", "provider": "credentials"},
        )


    
    else:
        return None



#######################
##### FUNCIONES #######
#######################


SUBMODULOS_MODULOS = {
    "nivel1": ["El Centro"],
    "nivel2": ["Servicios y Actividades"],
    "nivel3": ["Tarifas y Formas de Pago"],
    "nivel4": ["Normas de Uso"],
    "nivel5": ["Trámites"],
    "nivel6": ["Preguntas Frecuentes"],
    "nivel7": ["Atención al Cliente"]
}


async def iniciar_temporizador_objetivo(user_key):
    total_time = 600  # 10 minutos por módulo 
    msg = await cl.Message(content="⏳ Iniciando el cronómetro para este objetivo...").send()

    for remaining in range(total_time - 1, -1, -1):
        await asyncio.sleep(1)
        minutos = remaining // 60
        segundos = remaining % 60
        msg.content = f"⏳ Tiempo restante para este objetivo: {minutos:02d}:{segundos:02d}"
        await msg.update()

    await cl.Message(content="⏰ ¡Se acabó el tiempo para este objetivo!").send()
    temporizadores_objetivos.pop(user_key, None)

async def iniciar_temporizador(user_key):
    total_time = 1800 
    msg = await cl.Message(content="⏳ Iniciando el cronómetro...").send()

    for remaining in range(total_time - 1, -1, -1):
        await asyncio.sleep(1)
        minutos = remaining // 60
        segundos = remaining % 60
        msg.content = f"⏳ Tiempo restante: {minutos:02d}:{segundos:02d}"
        await msg.update()

    await cl.Message(content="⏰ ¡Se acabó el tiempo! Finalizando evaluación...").send()
    await mostrar_resultado_final()
    temporizadores_activos.pop(user_key, None)



ENCABEZADOS = {
    "nivel1": "📘 OBJETIVO 1 - El centro",
    "nivel2": "📗 OBJETIVO 2 - Servicios, Suscripciones, Modalidades de Abonos y Actividades",
    "nivel3": "📙 OBJETIVO 3 - Tarifas y formas de pago",
    "nivel4": "📕 OBJETIVO 4 - Normas y Políticas de uso de las instalaciones",
    "nivel5": "📒 OBJETIVO 5 - Trámites",
    "nivel6": "📓 OBJETIVO 6 - Preguntas Frecuentes (FAQs)",
    "nivel7": "📔 OBJETIVO 7 - Atención al Cliente"
}



#######################
##### INICIO ##########
#######################

@cl.on_chat_start
async def start():
    user = cl.user_session.get("user")
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    nombre_usuario = user.display_name if user else "usuario"
    print(user)
    actions = [
        cl.Action(name="Preguntas sobre el gimnasio", label="🤖 Preguntas sobre el gimnasio", value="Preguntas sobre el gimnasio", payload={}),
        cl.Action(name="Formación para tu puesto de trabajo", label="📚 Formación para tu puesto de trabajo", value="Formación para tu puesto de trabajo", payload={}),
        cl.Action(name="Entrenamiento personal", label="📝 Entrenamiento personal", value="Entrenamiento personal", payload={}),
        cl.Action(name="Evaluación personal", label="🎯 Evaluación personal", value="Evaluación personal", payload={})

    ]


    await cl.Message(
        content=(
            f"👋 ¡Bienvenido/a, **{nombre_usuario}**!\n\n"
            "Estoy aquí para acompañarte en tu desarrollo como profesional en nuestro gimnasio. "
            "Puedes resolver dudas, acceder a formación específica o evaluar tu progreso. Elige una de las siguientes opciones para comenzar:\n\n"

            " **1. Preguntas sobre el gimnasio**\n"
            "¿Tienes dudas sobre las instalaciones, servicios, horarios u otros aspectos? Estoy aquí para ayudarte con la información que necesites.\n\n"

            "**2. Formación para tu puesto de trabajo**\n"
            "Accede a contenidos diseñados para mejorar tus habilidades y conocimientos según tu rol. Aprende a tu ritmo y fortalece tu desempeño profesional.\n\n"

            "**3. Entrenamiento personal**\n"
            "Pon a prueba tus conocimientos de forma flexible. Puedes entrenar por objetivos específicos o hacer un repaso general con ejercicios globales. "
            "Ideal para practicar y mejorar antes de una evaluación final.\n\n"

            "**4. Evaluación personal**\n"
            "Realiza una evaluación completa sobre todos los contenidos formativos. Los resultados se registrarán y se enviará un informe para valorar tu progreso profesional.\n\n"

            "Selecciona la opción que más se ajuste a lo que necesitas y empecemos a trabajar juntos en tu crecimiento."
        ),
        actions=actions,
    ).send()

@cl.on_chat_end
def on_chat_end():
    cl.context.session.delete()
    print("The user disconnected!")



#######################
##### ASESOR ##########
#######################

@cl.action_callback("Preguntas sobre el gimnasio")
async def asesor_callback(action):
    cl.user_session.set("modo", "Preguntas sobre el gimnasio")
    await cl.Message(
        content="Estás en la sección de **Preguntas sobre el gimnasio**.\n\n Escribe cualquier pregunta relacionada con el centro y te ayudaré."
    ).send()
    

##########################
##### FORMACIÓN ##########
##########################


SECCIONES_FORMACION = chatbot.extraer_secciones_pdf()


@cl.action_callback("Formación para tu puesto de trabajo")
async def formacion_callback(action):
    await cl.Message(
        content="**¡Bienvenido a la Formación de Classic Fit!**\n\n Tenemos los siguiente objetivos de formación, puedes formarte en cualquiera de ellos. Elige uno y te mostraré los contenidos asociados:",
        actions=[
            cl.Action(name="formacion_nivel1", label="📘 OBJETIVO 1 - El Centro", value="nivel1", payload={}),
            cl.Action(name="formacion_nivel2", label="📗 OBJETIVO 2 - Servicios y Actividades", value="nivel2", payload={}),
            cl.Action(name="formacion_nivel3", label="📙 OBJETIVO 3 - Tarifas y Formas de Pago", value="nivel3", payload={}),
            cl.Action(name="formacion_nivel4", label="📕 OBJETIVO 4 - Normas de Uso", value="nivel4", payload={}),
            cl.Action(name="formacion_nivel5", label="📒 OBJETIVO 5 - Trámites", value="nivel5", payload={}),
            cl.Action(name="formacion_nivel6", label="📓 OBJETIVO 6 - Preguntas Frecuentes", value="nivel6", payload={}),
            cl.Action(name="formacion_nivel7", label="📔 OBJETIVO 7 - Atención al Cliente", value="nivel7", payload={}),
        ]
    ).send()

MODULO_ACTUAL = {}


@cl.action_callback("formacion_nivel1")
@cl.action_callback("formacion_nivel2")
@cl.action_callback("formacion_nivel3")
@cl.action_callback("formacion_nivel4")
@cl.action_callback("formacion_nivel5")
@cl.action_callback("formacion_nivel6")
@cl.action_callback("formacion_nivel7")

async def mostrar_contenido_formacion(action):
    modulo = action.name.split("_")[-1]
    encabezado = ENCABEZADOS.get(modulo, "Contenido")
    contenido = SECCIONES_FORMACION.get(modulo, "No se encontró información para este módulo.")

    cl.user_session.set("modulo_formacion_actual", modulo)
    cl.user_session.set("modo", "Formación para tu puesto de trabajo")

    prompt = generar_prompt_para_formacion()
    mensaje_modelo = f"{prompt}\n\n{contenido}"

    try:
        respuesta = chatbot.chat.send_message(mensaje_modelo)
        contenido_formateado = respuesta.text
    except Exception as e:
        contenido_formateado = f"Ocurrió un error al generar el contenido formateado: {str(e)}"

    await cl.Message(
        content=f"**{encabezado}**\n\n{contenido_formateado}\n\n---\n\n**¿Tienes alguna duda sobre este objetivo? Pregunta lo que quieras y te ayudaré.**"
    ).send()


###########################
##### EVALUACIÓN ##########
###########################

@cl.action_callback("Entrenamiento personal")
async def evaluacion_callback(action):
    await cl.Message(
              content=(
            "**¡Bienvenido/a al área de Entrenamiento!**\n\n"
            "Te damos la bienvenida a nuestro espacio de aprendizaje, diseñado para adaptarse a tus necesidades y objetivos. "
            "Aquí encontrarás dos rutas formativas distintas para avanzar a tu ritmo y con un enfoque personalizado, además podrás acceder a tu historial de evaluaciones para hacer seguimiento de tu progreso, retomar contenidos pendientes y celebrar tus logros.\n\n"
            
            "📘 **Entrenamiento por Objetivos**\n\n"
            "*Enfócate. Profundiza. Avanza.*\n"
            "Accede a contenidos estructurados por competencias específicas. Aquí podrás elegir los temas que deseas trabajar y avanzar paso a paso en cada uno. "
            "Ideal para reforzar áreas concretas, superar retos puntuales o especializarte progresivamente.\n\n"
            
            "🌐 **Entrenamiento Global**\n\n"
            "*Evalúa tu conocimiento integral.*\n"
            "Reúne todos los objetivos formativos en una única evaluación. Ideal si quieres poner a prueba tus conocimientos de forma completa y desafiante, con una visión transversal del aprendizaje.\n\n"
            "Accede si buscas una experiencia formativa completa y desafiante.\n\n"
    

            "📊 **Historial de Entrenamientos**\n\n"
            "*Consulta tu progreso.*\n"
            "Accede al resumen de todos tus exámenes realizados, tanto por objetivos como globales. "
            "Revisa tus resultados, identifica tus avances y retoma fácilmente donde lo dejaste.\n\n"

            "**¿Qué tipo de evaluación deseas comenzar?**"
        ),
        actions=[
            cl.Action(name="evaluacion_por_objetivos", label="Entrenamiento por objetivos", payload={}),
            cl.Action(name="evaluacion_global", label="Entrenamiento Global", payload={}),
            cl.Action(name="historial_evaluaciones", label="Historial de Entrenamientos", value="historial", payload={})
        ]
    ).send()


temporizadores_activos = {}
temporizadores_objetivos = {}



#-------------- EVALUACIÓN POR OBJETIVOS -----------------------


TEXTO_BLOQUES = chatbot.extraer_secciones_pdf()

@cl.action_callback("evaluacion_por_objetivos")
async def evaluacion_por_objetivos_callback(action):
    await cl.Message(
        content="**¿Por qué objetivo desea empezar?**",
        actions=[
            cl.Action(name="evaluacion_nivel1", label="📘 OBJETIVO 1 - El Centro", value="nivel1", payload={}),
            cl.Action(name="evaluacion_nivel2", label="📗 OBJETIVO 2 - Servicios y Actividades", value="nivel2", payload={}),
            cl.Action(name="evaluacion_nivel3", label="📙 OBJETIVO 3 - Tarifas y Formas de Pago", value="nivel3", payload={}),
            cl.Action(name="evaluacion_nivel4", label="📕 OBJETIVO 4 - Normas de Uso", value="nivel4", payload={}),
            cl.Action(name="evaluacion_nivel5", label="📒 OBJETIVO 5 - Trámites", value="nivel5", payload={}),
            cl.Action(name="evaluacion_nivel6", label="📓 OBJETIVO 6 - Preguntas Frecuentes", value="nivel6", payload={}),
            cl.Action(name="evaluacion_nivel7", label="📔 OBJETIVO 7 - Atención al Cliente", value="nivel7", payload={}),
        ]
    ).send()


@cl.action_callback("evaluacion_nivel1")
@cl.action_callback("evaluacion_nivel2")
@cl.action_callback("evaluacion_nivel3")
@cl.action_callback("evaluacion_nivel4")
@cl.action_callback("evaluacion_nivel5")
@cl.action_callback("evaluacion_nivel6")
@cl.action_callback("evaluacion_nivel7")

async def modulo_callback(action):
    modulo = action.name.split("_")[-1]

    cl.user_session.set("objetivo", modulo)
    cl.user_session.set("objetivo_idx", 0)
    cl.user_session.set("pregunta_idx_eval", 0)
    cl.user_session.set("modo", "objetivo")
    cl.user_session.set("respuestas_usuario", [])
    cl.user_session.set("aciertos_eval", 0)
    cl.user_session.set("fallos_eval", 0)

    bloque_texto = TEXTO_BLOQUES.get(modulo, "")

    if modulo == "nivel1":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel1(bloque_texto)
    elif modulo == "nivel2":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel2(bloque_texto)
    elif modulo == "nivel3":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel3(bloque_texto)
    elif modulo == "nivel4":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel4(bloque_texto)
    elif modulo == "nivel5":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel5(bloque_texto)
    elif modulo == "nivel6":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel6(bloque_texto)
    elif modulo == "nivel7":
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo_nivel7(bloque_texto)
    else:
        preguntas_lote = chatbot.generar_lote_preguntas_por_objetivo(bloque_texto)

    cl.user_session.set("preguntas_objetivo", preguntas_lote)

    user_key = str(id(cl.user_session))
    if user_key in temporizadores_objetivos:
        temporizadores_objetivos[user_key].cancel()

    temporizadores_objetivos[user_key] = asyncio.create_task(iniciar_temporizador_objetivo(user_key))

    await cl.Message(content="**¡Mucha suerte!**\n\n").send()
    await enviar_pregunta_evaluacion_1()


async def enviar_pregunta_evaluacion_1():
    pregunta_idx = cl.user_session.get("pregunta_idx_eval") or 0
    if pregunta_idx >= 10:  # Solo 10 preguntas por bloque
        await resumen()
        return

    preguntas_lote = cl.user_session.get("preguntas_objetivo", [])
    tipo, pregunta, opciones, correcta = preguntas_lote[pregunta_idx]



    cl.user_session.set("respuesta_correcta_eval", correcta)
    cl.user_session.set("tipo_pregunta_eval", tipo)
    cl.user_session.set("pregunta_eval", pregunta)
    cl.user_session.set("opciones_eval", opciones)

    preguntas_usuario = cl.user_session.get("respuestas_usuario")
    preguntas_usuario.append({
        "pregunta_numero": pregunta_idx + 1,
        "pregunta": pregunta,
        "tipo": tipo,
        "opciones": opciones,
        "respuesta_correcta": correcta,
        "respuesta_usuario": None
    })
    cl.user_session.set("respuestas_usuario", preguntas_usuario)

    if tipo == "abierta":
        await cl.Message(content=f"**Pregunta {pregunta_idx + 1}: Abierta**\n\n{pregunta}").send()
    elif tipo == "situacion":
        await cl.Message(content=f"**Pregunta {pregunta_idx + 1}: Situación**\n\n{pregunta}\n\nDescribe cómo actuarías:").send()
    else:
        label_tipo = "**Verdadero/Falso**" if tipo == "vf" else "**Opción múltiple**"
        await cl.Message(
            content=f"**Pregunta {pregunta_idx + 1}: {label_tipo}**\n\n{pregunta}",
            actions=[
                cl.Action(name=f"obj_respuesta_{i}", label=op, value=str(i), payload={})
                for i, op in enumerate(opciones)
            ]
        ).send()


        
async def siguiente_pregunta_evaluacion_1():
    idx = cl.user_session.get("pregunta_idx_eval") + 1
    cl.user_session.set("pregunta_idx_eval", idx)

    if idx >= 10:
        await cl.Message(
            content="**Has terminado todas las preguntas del objetivo seleccionado. Haz clic en el botón para enviar tus respuestas.**",
            actions=[
                cl.Action(name="enviar_resultado_final_1", label="Enviar resultados", value="enviar", payload={})
            ]
        ).send()
    else:
        await enviar_pregunta_evaluacion_1()


@cl.action_callback("obj_respuesta_0")
@cl.action_callback("obj_respuesta_1")
@cl.action_callback("obj_respuesta_2")
@cl.action_callback("obj_respuesta_3")


async def respuesta_objetivo(action):
    seleccion = int(action.name.split("_")[2])
    opciones = cl.user_session.get("opciones_eval")
    respuesta_usuario = opciones[seleccion]
    correcta = cl.user_session.get("respuesta_correcta_eval")

    preguntas_usuario = cl.user_session.get("respuestas_usuario")

    if preguntas_usuario:
        preguntas_usuario[-1]["respuesta_usuario"] = respuesta_usuario
    
    cl.user_session.set("respuestas_usuario", preguntas_usuario)

    if respuesta_usuario.strip().lower() == correcta.strip().lower():
        aciertos = cl.user_session.get("aciertos_eval", 0) + 1
        cl.user_session.set("aciertos_eval", aciertos)
    else:
        fallos = cl.user_session.get("fallos_eval", 0) + 1
        cl.user_session.set("fallos_eval", fallos)

    await siguiente_pregunta_evaluacion_1()


@cl.action_callback("enviar_resultado_final_1")
async def enviar_resultado_final_callback(action):
    await resumen()

async def resumen():
    user_key = str(id(cl.user_session))
    tarea = temporizadores_objetivos.pop(user_key, None)
    if tarea and not tarea.done():
        tarea.cancel()

    respuestas_usuario = cl.user_session.get("respuestas_usuario")
    nivel_actual = cl.user_session.get("objetivo", "nivel1")  
    tipos_respuestas = [(item["tipo"],) for item in respuestas_usuario]
    pesos = calcular_pesos_reales(tipos_respuestas, nivel=nivel_actual)

    print(f"📌 Nivel actual usado para los pesos: {nivel_actual}") 
    print("🧮 Pesos reales por tipo:", pesos)  

    total_puntos = 0.0
    total_maximo = 0.0
    detalle_resultado = ""

    resumen_tipos = {
        "vf": {"nombre": "Verdadero y Falso", "acertadas": [], "puntos": 0.0},
        "opciones": {"nombre": "Opciones", "acertadas": [], "puntos": 0.0},
        "abierta": {"nombre": "Abierta", "acertadas": [], "puntos": 0.0},
        "situacion": {"nombre": "Situaciones", "acertadas": [], "puntos": 0.0}
    }

    for idx, item in enumerate(respuestas_usuario, 1):
        pregunta = item["pregunta"]
        respuesta_usuario = item["respuesta_usuario"]
        respuesta_correcta = item.get("respuesta_correcta", "")
        tipo = item["tipo"].strip().lower()
        puntos = 0.0
        feedback = ""

        if tipo == "abierta":
            if len(respuesta_usuario.strip()) < 5 or respuesta_usuario.lower().strip() in {"a", "x", "no sé", "nose", "ns"}:
                evaluacion = "no"
            else:
                prompt = (
                    f"Eres un tutor evaluador. Analiza la calidad de la respuesta del estudiante.\n\n"
                    f"Pregunta: {pregunta}\n"
                    f"Respuesta del estudiante: {respuesta_usuario}\n"
                    f"Respuesta esperada: {respuesta_correcta}\n\n"
                    f"¿La respuesta es válida o parcialmente correcta? Responde solo con 'Sí' o 'No'."
                )
                evaluacion = chatbot.chat.send_message(prompt).text.strip().lower()

            if evaluacion.startswith("sí") or evaluacion.startswith("si"):
                puntos = pesos[tipo]
                feedback = "✅ ¡Buena respuesta!"
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos
            else:
                feedback = f"❌ No es exacta. La correcta sería: **{respuesta_correcta}**."
                puntos = 0  

            item["puntos"] = puntos


        elif tipo == "situacion":
            feedback_texto, puntuacion_original = chatbot.generar_feedback_situacion(pregunta, respuesta_usuario)
            puntuacion = max(0.0, min(1.0, puntuacion_original))  
            puntos = puntuacion * pesos[tipo]
            item["puntos"] = puntos
            feedback = feedback_texto
            if puntos > 0:
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos

        elif tipo in ["vf", "opciones"]:
            if respuesta_usuario.strip().lower() == respuesta_correcta.strip().lower():
                puntos = pesos.get(tipo, 0.0)
                feedback = "✅ Respuesta correcta."
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos
            else:
                feedback = f"❌ Incorrecta. La correcta era: {respuesta_correcta}."
            item["puntos"] = puntos

        total_puntos += puntos
        total_maximo += pesos.get(tipo, 1.0)

        tipo_legible = resumen_tipos.get(tipo, {"nombre": tipo.capitalize()})["nombre"]

        detalle_resultado += (
            f"---\n"
            f"**Pregunta {idx} - {tipo_legible}:** \n{pregunta} \n\n"
            f"**Respuesta del usuario:** {respuesta_usuario}\n"
            f"**Puntos obtenidos:** {round(puntos, 2)}/{pesos.get(tipo, 1.0)}\n"
            f"**Corrección:** {feedback}\n\n"
        )

    nota_final = calcular_puntuacion(respuestas_usuario, nivel=nivel_actual)

    print(f"Pregunta {idx}: {pregunta}")
    print(f"Tipo: {tipo}")
    print(f"Respuesta usuario: {respuesta_usuario}")
    print(f"Respuesta correcta: {respuesta_correcta}")
    print(f"Puntos asignados: {puntos}")
    print(f"Feedback: {feedback}")
    print("---")

    prompt_feedback = (
            "Eres un tutor evaluador. A continuación tienes el resumen de respuestas del estudiante.\n"
            "Escribe un comentario general breve (3-5 frases) destacando fortalezas, mejoras posibles y motivación.\n"
            "Luego incluye una tabla visual clara con resultados de los tipos de pregunta usados y respuestas correctas.\n\n"
            "Tabla con tres columnas:\n"
            "- Tipo de pregunta (usa nombres legibles)\n"
            "- Preguntas acertadas (número)\n"
            "- Puntuación sumada (ej. +1.0, +1.5)\n\n"
            "Resumen de respuestas:\n"
        )



    for idx, r in enumerate(respuestas_usuario, 1):
        prompt_feedback += f"{idx}. ({r['tipo']}) {r['pregunta']}\n   Respuesta: {r['respuesta_usuario']} – Puntos: {r.get('puntos', 0)}\n\n"


    orden_tipos = ["vf", "opciones", "abierta", "situacion"]
    tabla_resultados = ""
    for tipo in orden_tipos:
        info = resumen_tipos[tipo]
        if info["acertadas"]:
            preguntas_str = ", ".join(map(str, info["acertadas"]))
            puntos_str = f"+{round(info['puntos'], 2)}"
            tabla_resultados += f"{info['nombre']} | {preguntas_str} | {puntos_str}\n"

    prompt_feedback += "\nTabla:\n" + tabla_resultados

    comentario_general = chatbot.chat.send_message(prompt_feedback).text.strip()

    resultado_final_objetivos_evaluacion = (
        f"\U0001F3C1 **Evaluación final completada**\n\n"
        f"{comentario_general}\n\n"
        f"{detalle_resultado}"
        f"---\n"
        f"**NOTA FINAL: {nota_final}/10**"
    )

    resultado_final_objetivos = (
        f"\U0001F3C1 **TU ÚLTIMA EVALUACIÓN:**\n\n"
        f"{comentario_general}\n\n"
        f"---\n"
        f"**NOTA FINAL: {nota_final}/10**"
    )



    cl.user_session.set("resultado_final_objetivos", resultado_final_objetivos)


    await cl.Message(content=resultado_final_objetivos_evaluacion).send()










#-------------- EVALUACIÓN FINAL -----------------------


@cl.action_callback("evaluacion_global")
async def comenzar_evaluacion_callback(action):
    num_preguntas = 20 

    cl.user_session.set("modo", "evaluacion")
    cl.user_session.set("pregunta_idx_eval", 0)
    cl.user_session.set("aciertos_eval", 0)
    cl.user_session.set("fallos_eval", 0)
    cl.user_session.set("respuestas_usuario", [])

    preguntas_final = []

    niveles = [
        "nivel1", "nivel2", "nivel3", "nivel4", 
        "nivel5", "nivel6", "nivel7"
    ]

    for nivel in niveles:
        texto_nivel = TEXTO_BLOQUES.get(nivel, "")
        if not texto_nivel:
            print(f"⚠️ No hay texto para el {nivel}")
            continue

        try:
            if nivel == "nivel1":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel1_final(texto_nivel)
            elif nivel == "nivel2":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel2_final(texto_nivel)
            elif nivel == "nivel3":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel3_final(texto_nivel)
            elif nivel == "nivel4":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel4_final(texto_nivel)
            elif nivel == "nivel5":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel5_final(texto_nivel)
            elif nivel == "nivel6":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel6_final(texto_nivel)
            elif nivel == "nivel7":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel7_final(texto_nivel)
            else:
                lote = []
        except Exception as e:
            print(f"❌ Error generando preguntas para {nivel}: {e}")
            lote = []

        print(f"Nivel: {nivel} - Preguntas generadas: {len(lote)}")

        preguntas_validas = []
        for p in lote:
            if isinstance(p, tuple) and len(p) == 4:
                preguntas_validas.append(p + (nivel,))
            else:
                print(f"⚠️ Pregunta inválida descartada en {nivel}: {p}")

        preguntas_final.extend(preguntas_validas)

    random.shuffle(preguntas_final)
    preguntas_final = preguntas_final[:num_preguntas]

    cl.user_session.set("preguntas_final", preguntas_final)
    cl.user_session.set("max_preguntas", len(preguntas_final))

    user_key = str(id(cl.user_session))
    temporizadores_activos[user_key] = asyncio.create_task(iniciar_temporizador(user_key))

    await cl.Message(content=f"**¡Comenzamos la evaluación global!**\n\n A continuación, se te mostrarán una serie de preguntas sobre todos los objetivos que has estudiado previamente. Cada pregunta cuenta con una puntuación diferente. \n\n **MUCHA SUERTE!**").send()
    await enviar_pregunta_evaluacion()



async def enviar_pregunta_evaluacion():
    pregunta_idx = cl.user_session.get("pregunta_idx_eval", 0)
    max_preguntas = cl.user_session.get("max_preguntas", 20)

    if pregunta_idx >= max_preguntas:
        await mostrar_resultado_final()
        return

    preguntas_final = cl.user_session.get("preguntas_final", [])
    tipo, pregunta, opciones, correcta, nivel = preguntas_final[pregunta_idx]

    cl.user_session.set("respuesta_correcta_eval", correcta)
    cl.user_session.set("tipo_pregunta_eval", tipo)
    cl.user_session.set("pregunta_eval", pregunta)
    cl.user_session.set("opciones_eval", opciones)

    preguntas_usuario = cl.user_session.get("respuestas_usuario", [])
    preguntas_usuario.append({
        "pregunta_numero": pregunta_idx + 1,
        "pregunta": pregunta,
        "tipo": tipo,
        "opciones": opciones,
        "respuesta_correcta": correcta,
        "respuesta_usuario": None
    })
    cl.user_session.set("respuestas_usuario", preguntas_usuario)

    if tipo == "abierta":
        await cl.Message(content=f"**Pregunta {pregunta_idx + 1}: Abierta**\n\n{pregunta}").send()
        await cl.Message(content="Escribe tu respuesta abajo:").send()

    elif tipo == "situacion":
        await cl.Message(content=f"**Pregunta {pregunta_idx + 1}: Situación**\n\n{pregunta}\n\nDescribe cómo actuarías:").send()

    else:
        label_tipo = "**Verdadero/Falso**" if tipo == "vf" else "**Opción múltiple**"
        await cl.Message(
            content=f"**Pregunta {pregunta_idx + 1}: {label_tipo}**\n\n{pregunta}",
            actions=[
                cl.Action(name=f"eval_respuesta_{i}", label=op, value=str(i), payload={})
                for i, op in enumerate(opciones)
            ]
        ).send()


async def siguiente_pregunta_evaluacion():
    idx = cl.user_session.get("pregunta_idx_eval", 0) + 1
    cl.user_session.set("pregunta_idx_eval", idx)

    max_preguntas = cl.user_session.get("max_preguntas", 20)

    if idx >= max_preguntas:
        await cl.Message(
            content="**Has terminado todas las preguntas. Haz clic en el botón para enviar tus respuestas.**",
            actions=[
                cl.Action(name="enviar_resultado_final", label="Enviar resultados", value="enviar", payload={})
            ]
        ).send()
    else:
        await enviar_pregunta_evaluacion()



@cl.action_callback("eval_respuesta_0")
@cl.action_callback("eval_respuesta_1")
@cl.action_callback("eval_respuesta_2")
@cl.action_callback("eval_respuesta_3")

async def respuesta_evaluacion_callback(action):
    seleccion = int(action.name.split("_")[2])
    opciones = cl.user_session.get("opciones_eval")
    respuesta_usuario = opciones[seleccion]
    correcta = cl.user_session.get("respuesta_correcta_eval")


    preguntas_usuario = cl.user_session.get("respuestas_usuario")
    preguntas_usuario[-1]["respuesta_usuario"] = respuesta_usuario
    cl.user_session.set("respuestas_usuario", preguntas_usuario)

    if respuesta_usuario.strip().lower() == correcta.strip().lower():
        cl.user_session.set("aciertos_eval", cl.user_session.get("aciertos_eval") + 1)
    else:
        cl.user_session.set("fallos_eval", cl.user_session.get("fallos_eval") + 1)

    await siguiente_pregunta_evaluacion()

def guardar_respuesta(pregunta, respuesta_usuario, respuesta_correcta, tipo, nivel):
    respuestas_usuario = cl.user_session.get("respuestas_usuario", [])

    respuesta = {
        "pregunta": pregunta,
        "respuesta_usuario": respuesta_usuario,
        "respuesta_correcta": respuesta_correcta,
        "tipo": tipo,
        "nivel": nivel,
    }
    respuestas_usuario.append(respuesta)
    cl.user_session.set("respuestas_usuario", respuestas_usuario)



@cl.action_callback("enviar_resultado_final")
async def enviar_resultado_final_callback(action):
    await mostrar_resultado_final()


async def mostrar_resultado_final():
    user_key = str(id(cl.user_session))
    tarea = temporizadores_activos.pop(user_key, None)
    if tarea and not tarea.done():
        tarea.cancel()

    respuestas_usuario = cl.user_session.get("respuestas_usuario", [])
    print(f"📝 Número total de preguntas: {len(respuestas_usuario)}")

    PESOS_GLOBAL = {
        "vf": 0.25,
        "opciones": 0.5,
        "abierta": 1.0,
        "situacion": 1.5
    }

    nombres_tipos = {
        "vf": "Verdadero y Falso",
        "opciones": "Opciones",
        "abierta": "Abierta",
        "situacion": "Situaciones"
    }

    total_puntos = 0.0
    total_maximo = 0.0
    detalle_resultado = ""


    resumen_tipos = {
        "vf": {"nombre": "Verdadero y Falso", "acertadas": [], "puntos": 0.0},
        "opciones": {"nombre": "Opciones", "acertadas": [], "puntos": 0.0},
        "abierta": {"nombre": "Abierta", "acertadas": [], "puntos": 0.0},
        "situacion": {"nombre": "Situaciones", "acertadas": [], "puntos": 0.0}
    }

    for idx, item in enumerate(respuestas_usuario, 1):
        pregunta = item["pregunta"]
        respuesta_usuario = item["respuesta_usuario"]
        respuesta_correcta = item.get("respuesta_correcta", "")
        tipo = item["tipo"].strip().lower()
        peso_tipo = PESOS_GLOBAL.get(tipo, 1.0)

        puntos = 0.0
        feedback = ""

        if tipo == "abierta":
            if len(respuesta_usuario.strip()) < 5 or respuesta_usuario.lower().strip() in {"a", "x", "no sé", "nose", "ns"}:
                evaluacion = "no"
            else:
                prompt = (
                    f"Eres un asistente evaluador. Compara la respuesta del usuario con la esperada.\n\n"
                    f"Pregunta: {pregunta}\n"
                    f"Respuesta del usuario: {respuesta_usuario}\n"
                    f"Respuesta correcta esperada: {respuesta_correcta}\n\n"
                    f"¿La respuesta del usuario es correcta o aceptable aunque no sea idéntica? "
                    f"Ten en cuenta si la respuesta es suficientemente informativa, coherente y relacionada con la pregunta.\n"
                    f"Responde únicamente con 'Sí' o 'No'."
                )
                evaluacion = chatbot.chat.send_message(prompt).text.strip().lower()

            if evaluacion.startswith("sí") or evaluacion.startswith("si"):
                puntos = peso_tipo
                feedback = "✅ ¡Buena respuesta!"
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos
            else:
                feedback = f"❌ No es exacta. La correcta sería: **{respuesta_correcta}**."

        elif tipo == "situacion":
            feedback_texto, puntuacion_original = chatbot.generar_feedback_situacion(pregunta, respuesta_usuario)
            puntuacion = max(0.0, min(1.0, puntuacion_original))
            puntos = puntuacion * peso_tipo
            feedback = feedback_texto or ""
            if puntos > 0:
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos

        elif tipo in ["vf", "opciones"]:
            if respuesta_usuario.strip().lower() == respuesta_correcta.strip().lower():
                puntos = peso_tipo
                feedback = "✅ Respuesta correcta."
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos
            else:
                feedback = f"❌ Incorrecta. La correcta era: {respuesta_correcta}."

        else:
            feedback = f"⚠️ Tipo de pregunta desconocido: {tipo}. No se asignaron puntos."

        item["puntos"] = puntos
        total_puntos += puntos
        total_maximo += peso_tipo

        tipo_legible = nombres_tipos.get(tipo, tipo.capitalize())
        detalle_resultado += (
            f"---\n"
            f"**Pregunta {idx} - {tipo_legible}:** \n{pregunta}\n\n"
            f"**Respuesta del usuario:** {respuesta_usuario}\n"
            f"**Puntos obtenidos:** {round(puntos, 2)}/{peso_tipo}\n"
            f"**Corrección:** {feedback}\n\n"
        )

    nota_final = round((total_puntos / total_maximo) * 15, 2) if total_maximo > 0 else 0.0

 
    prompt_feedback = (
        "Eres un tutor evaluador. A continuación tienes el resumen de respuestas del estudiante.\n"
        "Escribe un comentario general breve (3-5 frases) destacando fortalezas, mejoras posibles y motivación.\n"
        "Luego incluye una tabla visual clara con resultados de los tipos de pregunta usados y respuestas correctas.\n\n"
        "Tabla con tres columnas:\n"
        "- Tipo de pregunta (usa nombres legibles)\n"
        "- Preguntas acertadas (número)\n"
        "- Puntuación sumada (ej. +1.0, +1.5)\n\n"
        "Resumen de respuestas:\n"
    )

    for idx, r in enumerate(respuestas_usuario, 1):
        prompt_feedback += f"{idx}. ({r['tipo']}) {r['pregunta']}\n   Respuesta: {r['respuesta_usuario']} – Puntos: {r.get('puntos', 0)}\n\n"

    orden_tipos = ["vf", "opciones", "abierta", "situacion"]
    tabla_resultados = ""
    for tipo in orden_tipos:
        info = resumen_tipos[tipo]
        if info["acertadas"]:
            preguntas_str = ", ".join(map(str, info["acertadas"]))
            puntos_str = f"+{round(info['puntos'], 2)}"
            tabla_resultados += f"{info['nombre']} | {preguntas_str} | {puntos_str}\n"

    prompt_feedback += "\nTabla:\n" + tabla_resultados

    comentario_general = chatbot.chat.send_message(prompt_feedback).text.strip()

    resultado_final = (
        f"\U0001F3C1 **Evaluación final completada**\n\n"
        f"{comentario_general}\n\n"
        f"{detalle_resultado}"
        f"---\n"
        f"**NOTA FINAL: {nota_final}/15**"
    )

    
    resultado_final_evolucion = (
        f"\U0001F3C1 **TU ÚLTIMA EVALUACIÓN:**\n\n"
        f"{comentario_general}\n\n"
        f"---\n"
        f"**NOTA FINAL: {nota_final}/15**"
    )
    user = cl.user_session.get("user")
    user_id = user.identifier if user else "anonimo"

    #guardar_evaluacion_usuario(
        #user_id=user_id,
        #nota=nota_final,
        #comentario=comentario_general,
        #resumen=resultado_final_evolucion
    #)


    cl.user_session.set("resultado_final_evolucion", resultado_final_evolucion)


    await cl.Message(content=resultado_final).send()




# -------------- HISTORIAL DE EVALUACIONES --------------------------------------


@cl.action_callback("historial_evaluaciones")
async def historial_evaluaciones(action):
    user = cl.user_session.get("user")
    if not user:
        await cl.Message(content="No se pudo identificar al usuario. Por favor, inicia sesión.").send()
        return
    
    await cl.Message(
                content=(
            "**📈 Historial de Entrenamiento**\n\n"
            "En esta sección podrás consultar todos los resultados de los exámenes que has realizado hasta la fecha. "
            "Podrás hacer un seguimiento de tu evolución, identificar tus progresos y detectar áreas que aún puedes reforzar.\n\n"
            "Selecciona el tipo de resultados que deseas revisar:"
        ),
        actions=[
            cl.Action(name="mostrar_global", label="📊 Resultados Entrenamiento Global", value="global", payload={}),
            cl.Action(name="mostrar_objetivos", label="🎯 Resultados Entrenamiento por Objetivos", value="objetivos", payload={}),
        ]
    ).send()


@cl.action_callback("mostrar_global")
async def mostrar_global(action):

    user = cl.user_session.get("user")
    nombre_usuario = user.display_name
    user_id = user.identifier

    historial = cargar_historial_usuario(user_id)

    if not historial:
        await cl.Message(content=f"Hola {nombre_usuario}, no hay evaluaciones anteriores registradas.").send()
        return

    historial = historial[::-1]

    try:
        fechas = [datetime.strptime(e["fecha"], "%Y-%m-%d") for e in historial]
        notas = [e["nota"] for e in historial]
    except Exception as e:
        print(f"[ERROR] Procesando fechas o notas: {e}")
        await cl.Message(content="⚠️ Error procesando datos del historial.").send()
        return


    # Crear tabla
    tabla = "| Examen | Fecha  | Nota | Comentarios |\n"
    tabla += "|--------|--------|------|-------------|\n"
    comentarios = []

    for idx, e in enumerate(historial):
        examen = f"Examen {idx + 1}"
        fecha = e.get("fecha", "—")
        nota = f"{e.get('nota', '—')}/15"
        comentario = e.get("comentario", "—").replace("\n", " ")
        comentarios.append(comentario)
        tabla += f"| {examen} | {fecha} | {nota} | {comentario} |\n"

    print(f"[DEBUG] Tabla generada con {len(historial)} filas")

    # Resumen con IA
    todos_los_comentarios = "\n".join(comentarios)
    prompt_resumen = f"""
    A continuación te proporciono una serie de comentarios realizados tras diferentes evaluaciones de un empleado. 
    Tu tarea es sintetizar esta información y generar un comentario general sobre la evolución profesional del empleado, 
    identificando fortalezas, áreas de mejora y cualquier tendencia observable en su rendimiento.

    Comentarios:
    {todos_los_comentarios}

    Por favor, redacta un análisis global constructivo en un párrafo. Siempre en español.
    """

    try:
        resumen_general = chatbot.chat.send_message(prompt_resumen).text.strip()
        print("[DEBUG] Resumen recibido correctamente")
    except Exception as e:
        resumen_general = "No se pudo generar el resumen."
        print(f"[ERROR] Generando resumen con chatbot: {e}")

    await cl.Message(content=f"🧠 **Resumen General de tu Evolución Profesional:**\n\n{resumen_general}").send()
    await cl.Message(content=f"📋 **Resumen de todos los exámenes que has realizado:**\n\n{tabla}").send()









@cl.action_callback("mostrar_objetivos")
async def mostrar_objetivos(action):
    user = cl.user_session.get("user")
    nombre_usuario = user.display_name
    user_id = user.identifier

    historial_dict = cargar_historial_usuario_objetivos(user_id)

    if not isinstance(historial_dict, dict):
        await cl.Message(content=f" Error: El historial no tiene el formato esperado.").send()
        return

    historial = []
    for objetivo, evaluaciones in historial_dict.items():
        for e in evaluaciones:
            e["objetivo"] = objetivo
            historial.append(e)

    if not historial:
        await cl.Message(content=f"Hola {nombre_usuario}, no hay evaluaciones anteriores registradas.").send()
        return

    historial.sort(key=lambda e: datetime.strptime(e["fecha"], "%Y-%m-%d"), reverse=True)

    resumen_por_objetivo = defaultdict(list)
    comentarios_globales = []

    for e in historial:
        resumen_por_objetivo[e["objetivo"]].append(e)

    objetivos = []
    promedios = []

    for objetivo in sorted(resumen_por_objetivo.keys()):
        evaluaciones = resumen_por_objetivo[objetivo]
        notas = [e["nota"] for e in evaluaciones]
        promedio = round(statistics.mean(notas), 2)
        objetivos.append(objetivo.capitalize())
        promedios.append(promedio)



    tabla = "| Objetivo | Nº Exámenes | Nota Promedio | Comentarios Destacados |\n"
    tabla += "|----------|--------------|----------------|--------------------------|\n"

    for objetivo in sorted(resumen_por_objetivo.keys()):
        evaluaciones = resumen_por_objetivo[objetivo]
        notas = [e["nota"] for e in evaluaciones]
        comentarios = [e["comentario"] for e in evaluaciones]
        comentarios_globales.extend(comentarios)
        promedio = round(statistics.mean(notas), 2)
        comentarios_destacados = "; ".join(comentarios[:2]).replace("\n", " ")
        tabla += f"| {objetivo.capitalize()} | {len(evaluaciones)} | {promedio} / 10 | {comentarios_destacados} |\n"

    todos_los_comentarios = "\n".join(comentarios_globales)
    prompt_resumen = f"""
    A continuación te proporciono una serie de comentarios realizados tras diferentes evaluaciones de un empleado. 
    Tu tarea es sintetizar esta información y generar un comentario general sobre la evolución profesional del empleado, 
    identificando fortalezas, áreas de mejora y cualquier tendencia observable en su rendimiento.

    Comentarios:
    {todos_los_comentarios}

    Por favor, redacta un análisis global constructivo en un párrafo centrandote en que objetivos va bien y en cuales no, posibles planes de mejora. Siempre en español.
    """
    resumen_general = chatbot.chat.send_message(prompt_resumen).text.strip()

    await cl.Message(content=f"🧠 **Resumen Global de tu Evolución Profesional por Objetivos:**\n\n{resumen_general}").send()
    await cl.Message(content=f"📋 **Detalle por Objetivo:**\n\n{tabla}").send()








#######################
##### EVALUACIÓN  #####
#######################


@cl.action_callback("Evaluación personal")
async def evaluacion_interna_callback(action):
    await cl.Message(
        content=(
            "**¡Bienvenido a la Evaluación Final!**\n\n"

            "Estás a punto de realizar el Examen Final, una evaluación completa que incluye todos los objetivos del programa. "
            "Este examen sirve como cierre del proceso de entrenamiento y tiene carácter oficial.\n\n"
            "Hazlo cuando te sientas preparado, ya que una vez finalices:\n"
            "• Se generará un informe detallado con tus resultados\n"
            "• El informe será enviado automáticamente a tu empresa\n\n"
            "No es un simulacro. Esta es tu oportunidad para demostrar todo lo que has aprendido.\n\n"
            "Haz clic cuando estés listo para comenzar:"
        ),

        actions=[
            cl.Action(name="Examen final", label="📝 Comenzar Examen Final", value="Examen final", payload={}),
        ]
    ).send()




@cl.action_callback("Examen final")
async def comenzar_evaluacion_callback(action):
    num_preguntas = 20 

    cl.user_session.set("modo", "evaluacion")
    cl.user_session.set("pregunta_idx_eval", 0)
    cl.user_session.set("aciertos_eval", 0)
    cl.user_session.set("fallos_eval", 0)
    cl.user_session.set("respuestas_usuario", [])

    preguntas_final = []

    niveles = [
        "nivel1", "nivel2", "nivel3", "nivel4", 
        "nivel5", "nivel6", "nivel7"
    ]

    for nivel in niveles:
        texto_nivel = TEXTO_BLOQUES.get(nivel, "")
        if not texto_nivel:
            print(f"⚠️ No hay texto para el {nivel}")
            continue

        try:
            if nivel == "nivel1":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel1_final(texto_nivel)
            elif nivel == "nivel2":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel2_final(texto_nivel)
            elif nivel == "nivel3":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel3_final(texto_nivel)
            elif nivel == "nivel4":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel4_final(texto_nivel)
            elif nivel == "nivel5":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel5_final(texto_nivel)
            elif nivel == "nivel6":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel6_final(texto_nivel)
            elif nivel == "nivel7":
                lote = chatbot.generar_lote_preguntas_por_objetivo_nivel7_final(texto_nivel)
            else:
                lote = []
        except Exception as e:
            print(f"❌ Error generando preguntas para {nivel}: {e}")
            lote = []

        print(f"Nivel: {nivel} - Preguntas generadas: {len(lote)}")

        preguntas_validas = []
        for p in lote:
            if isinstance(p, tuple) and len(p) == 4:
                preguntas_validas.append(p + (nivel,))
            else:
                print(f"⚠️ Pregunta inválida descartada en {nivel}: {p}")

        preguntas_final.extend(preguntas_validas)

    random.shuffle(preguntas_final)
    preguntas_final = preguntas_final[:num_preguntas]

    cl.user_session.set("preguntas_final", preguntas_final)
    cl.user_session.set("max_preguntas", len(preguntas_final))

    user_key = str(id(cl.user_session))
    temporizadores_activos[user_key] = asyncio.create_task(iniciar_temporizador(user_key))

    await cl.Message(content=f"**🎓 ¡Comienza el Examen Final!**\n\n"
"Responderás a una serie de preguntas que abarcan todos los objetivos trabajados durante tu formación. "
"Recuerda que cada pregunta tiene un valor diferente, así que tómate tu tiempo para responder con atención.\n\n"
"📝 Este examen representa el cierre oficial del proceso de entrenamiento.\n\n"
"**¡Mucha suerte, confía en todo lo que has aprendido!**"
).send()
    await enviar_pregunta_evaluacion()



async def enviar_pregunta_evaluacion():
    pregunta_idx = cl.user_session.get("pregunta_idx_eval", 0)
    max_preguntas = cl.user_session.get("max_preguntas", 20)

    if pregunta_idx >= max_preguntas:
        await mostrar_resultado_final()
        return

    preguntas_final = cl.user_session.get("preguntas_final", [])
    tipo, pregunta, opciones, correcta, nivel = preguntas_final[pregunta_idx]

    cl.user_session.set("respuesta_correcta_eval", correcta)
    cl.user_session.set("tipo_pregunta_eval", tipo)
    cl.user_session.set("pregunta_eval", pregunta)
    cl.user_session.set("opciones_eval", opciones)

    preguntas_usuario = cl.user_session.get("respuestas_usuario", [])
    preguntas_usuario.append({
        "pregunta_numero": pregunta_idx + 1,
        "pregunta": pregunta,
        "tipo": tipo,
        "opciones": opciones,
        "respuesta_correcta": correcta,
        "respuesta_usuario": None
    })
    cl.user_session.set("respuestas_usuario", preguntas_usuario)

    if tipo == "abierta":
        await cl.Message(content=f"**Pregunta {pregunta_idx + 1}: Abierta**\n\n{pregunta}").send()
        await cl.Message(content="Escribe tu respuesta abajo:").send()

    elif tipo == "situacion":
        await cl.Message(content=f"**Pregunta {pregunta_idx + 1}: Situación**\n\n{pregunta}\n\nDescribe cómo actuarías:").send()

    else:
        label_tipo = "**Verdadero/Falso**" if tipo == "vf" else "**Opción múltiple**"
        await cl.Message(
            content=f"**Pregunta {pregunta_idx + 1}: {label_tipo}**\n\n{pregunta}",
            actions=[
                cl.Action(name=f"eval_respuesta_{i}", label=op, value=str(i), payload={})
                for i, op in enumerate(opciones)
            ]
        ).send()


async def siguiente_pregunta_evaluacion():
    idx = cl.user_session.get("pregunta_idx_eval", 0) + 1
    cl.user_session.set("pregunta_idx_eval", idx)

    max_preguntas = cl.user_session.get("max_preguntas", 20)

    if idx >= max_preguntas:
        await cl.Message(
            content="**Has terminado todas las preguntas. Haz clic en el botón para enviar tus respuestas.**",
            actions=[
                cl.Action(name="enviar_resultado_final", label="Enviar resultados", value="enviar", payload={})
            ]
        ).send()
    else:
        await enviar_pregunta_evaluacion()



@cl.action_callback("eval_respuesta_0")
@cl.action_callback("eval_respuesta_1")
@cl.action_callback("eval_respuesta_2")
@cl.action_callback("eval_respuesta_3")

async def respuesta_evaluacion_callback(action):
    seleccion = int(action.name.split("_")[2])
    opciones = cl.user_session.get("opciones_eval")
    respuesta_usuario = opciones[seleccion]
    correcta = cl.user_session.get("respuesta_correcta_eval")


    preguntas_usuario = cl.user_session.get("respuestas_usuario")
    preguntas_usuario[-1]["respuesta_usuario"] = respuesta_usuario
    cl.user_session.set("respuestas_usuario", preguntas_usuario)

    if respuesta_usuario.strip().lower() == correcta.strip().lower():
        cl.user_session.set("aciertos_eval", cl.user_session.get("aciertos_eval") + 1)
    else:
        cl.user_session.set("fallos_eval", cl.user_session.get("fallos_eval") + 1)

    await siguiente_pregunta_evaluacion()

def guardar_respuesta(pregunta, respuesta_usuario, respuesta_correcta, tipo, nivel):
    respuestas_usuario = cl.user_session.get("respuestas_usuario", [])

    respuesta = {
        "pregunta": pregunta,
        "respuesta_usuario": respuesta_usuario,
        "respuesta_correcta": respuesta_correcta,
        "tipo": tipo,
        "nivel": nivel,
    }
    respuestas_usuario.append(respuesta)
    cl.user_session.set("respuestas_usuario", respuestas_usuario)



@cl.action_callback("enviar_resultado_final")
async def enviar_resultado_final_callback(action):
    await mostrar_resultado_final()


async def mostrar_resultado_final():
    user_key = str(id(cl.user_session))
    tarea = temporizadores_activos.pop(user_key, None)
    if tarea and not tarea.done():
        tarea.cancel()

    respuestas_usuario = cl.user_session.get("respuestas_usuario", [])
    print(f"📝 Número total de preguntas: {len(respuestas_usuario)}")

    PESOS_GLOBAL = {
        "vf": 0.25,
        "opciones": 0.5,
        "abierta": 1.0,
        "situacion": 1.5
    }

    nombres_tipos = {
        "vf": "Verdadero y Falso",
        "opciones": "Opciones",
        "abierta": "Abierta",
        "situacion": "Situaciones"
    }

    total_puntos = 0.0
    total_maximo = 0.0
    detalle_resultado = ""


    resumen_tipos = {
        "vf": {"nombre": "Verdadero y Falso", "acertadas": [], "puntos": 0.0},
        "opciones": {"nombre": "Opciones", "acertadas": [], "puntos": 0.0},
        "abierta": {"nombre": "Abierta", "acertadas": [], "puntos": 0.0},
        "situacion": {"nombre": "Situaciones", "acertadas": [], "puntos": 0.0}
    }

    for idx, item in enumerate(respuestas_usuario, 1):
        pregunta = item["pregunta"]
        respuesta_usuario = item["respuesta_usuario"]
        respuesta_correcta = item.get("respuesta_correcta", "")
        tipo = item["tipo"].strip().lower()
        peso_tipo = PESOS_GLOBAL.get(tipo, 1.0)

        puntos = 0.0
        feedback = ""

        if tipo == "abierta":
            if len(respuesta_usuario.strip()) < 5 or respuesta_usuario.lower().strip() in {"a", "x", "no sé", "nose", "ns"}:
                evaluacion = "no"
            else:
                prompt = (
                    f"Eres un asistente evaluador. Compara la respuesta del usuario con la esperada.\n\n"
                    f"Pregunta: {pregunta}\n"
                    f"Respuesta del usuario: {respuesta_usuario}\n"
                    f"Respuesta correcta esperada: {respuesta_correcta}\n\n"
                    f"¿La respuesta del usuario es correcta o aceptable aunque no sea idéntica? "
                    f"Ten en cuenta si la respuesta es suficientemente informativa, coherente y relacionada con la pregunta.\n"
                    f"Responde únicamente con 'Sí' o 'No'."
                )
                evaluacion = chatbot.chat.send_message(prompt).text.strip().lower()

            if evaluacion.startswith("sí") or evaluacion.startswith("si"):
                puntos = peso_tipo
                feedback = "✅ ¡Buena respuesta!"
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos
            else:
                feedback = f"❌ No es exacta. La correcta sería: **{respuesta_correcta}**."

        elif tipo == "situacion":
            feedback_texto, puntuacion_original = chatbot.generar_feedback_situacion(pregunta, respuesta_usuario)
            puntuacion = max(0.0, min(1.0, puntuacion_original))
            puntos = puntuacion * peso_tipo
            feedback = feedback_texto or ""
            if puntos > 0:
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos

        elif tipo in ["vf", "opciones"]:
            if respuesta_usuario.strip().lower() == respuesta_correcta.strip().lower():
                puntos = peso_tipo
                feedback = "✅ Respuesta correcta."
                resumen_tipos[tipo]["acertadas"].append(idx)
                resumen_tipos[tipo]["puntos"] += puntos
            else:
                feedback = f"❌ Incorrecta. La correcta era: {respuesta_correcta}."

        else:
            feedback = f"⚠️ Tipo de pregunta desconocido: {tipo}. No se asignaron puntos."

        item["puntos"] = puntos
        total_puntos += puntos
        total_maximo += peso_tipo

        tipo_legible = nombres_tipos.get(tipo, tipo.capitalize())
        detalle_resultado += (
            f"---\n"
            f"**Pregunta {idx} - {tipo_legible}:** \n{pregunta}\n\n"
            f"**Respuesta del usuario:** {respuesta_usuario}\n"
            f"**Puntos obtenidos:** {round(puntos, 2)}/{peso_tipo}\n"
            f"**Corrección:** {feedback}\n\n"
        )

    nota_final = round((total_puntos / total_maximo) * 15, 2) if total_maximo > 0 else 0.0

 
    prompt_feedback = (
        "Eres un tutor evaluador. A continuación tienes el resumen de respuestas del estudiante.\n"
        "Escribe un comentario general breve (3-5 frases) destacando fortalezas, mejoras posibles y motivación.\n"
        "Luego incluye una tabla visual clara con resultados de los tipos de pregunta usados y respuestas correctas.\n\n"
        "Tabla con tres columnas:\n"
        "- Tipo de pregunta (usa nombres legibles)\n"
        "- Preguntas acertadas (número)\n"
        "- Puntuación sumada (ej. +1.0, +1.5)\n\n"
        "Resumen de respuestas:\n"
    )

    for idx, r in enumerate(respuestas_usuario, 1):
        prompt_feedback += f"{idx}. ({r['tipo']}) {r['pregunta']}\n   Respuesta: {r['respuesta_usuario']} – Puntos: {r.get('puntos', 0)}\n\n"

    orden_tipos = ["vf", "opciones", "abierta", "situacion"]
    tabla_resultados = ""
    for tipo in orden_tipos:
        info = resumen_tipos[tipo]
        if info["acertadas"]:
            preguntas_str = ", ".join(map(str, info["acertadas"]))
            puntos_str = f"+{round(info['puntos'], 2)}"
            tabla_resultados += f"{info['nombre']} | {preguntas_str} | {puntos_str}\n"

    prompt_feedback += "\nTabla:\n" + tabla_resultados

    comentario_general = chatbot.chat.send_message(prompt_feedback).text.strip()

    resultado_final = (
        f"\U0001F3C1 **Evaluación final completada**\n\n"
        f"{comentario_general}\n\n"
        f"{detalle_resultado}"
        f"---\n"
        f"**NOTA FINAL: {nota_final}/15**"
    )

    
    resultado_final_evolucion = (
        f"\U0001F3C1 **TU ÚLTIMA EVALUACIÓN:**\n\n"
        f"{comentario_general}\n\n"
        f"---\n"
        f"**NOTA FINAL: {nota_final}/15**"
    )
    user = cl.user_session.get("user")
    user_id = user.identifier if user else "anonimo"

    cl.user_session.set("resultado_final_evolucion", resultado_final_evolucion)


    await cl.Message(content=resultado_final).send()

    # Obtener el usuario actual
    user = cl.user_session.get("user")
    if not user:
        await cl.Message(content="No se pudo identificar al usuario. Por favor, inicia sesión.").send()
        return

    user_id = user.identifier
    nombre_usuario = user.display_name

    # Crear tabla del único examen actual
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    tabla = "| Examen | Fecha | Nota | Comentarios |\n"
    tabla += "|--------|-------|------|-------------|\n"
    comentario_simple = comentario_general.split("\n")[0].replace("\n", " ")
    tabla += f"| Examen actual | {fecha_actual} | {nota_final}/15 | {comentario_simple} |\n"

    resumen_prompt = f"""
El empleado {nombre_usuario} ha sido evaluado. A continuación, se muestra su resultado más reciente en forma de tabla:

{tabla}

Con base en este resultado, redacta un **informe profesional completo** que incluya los siguientes apartados con sus respectivos títulos en negrita usando markdown (por ejemplo, **Conclusión**). No añadas títulos extra. El texto debe ser plano, sin subapartados, ni listas, ni enumeraciones. Todo redactado.:

- Un texto breve sobre el propósito del informe.

- **1. Análisis general de su evolución**

- **2. Fortalezas observadas**

- **3. Áreas de mejora**

- **4. Conclusión**

➡️ El tono debe ser profesional, claro, positivo y constructivo. No uses símbolos como *** ni frases como “a continuación”. Las listas deben estar correctamente formateadas con asteriscos (*) y con buena puntuación. Mantén una estructura limpia con espacios adecuados entre párrafos y apartados.
""".strip()

    informe_generado = chatbot.chat.send_message(resumen_prompt).text.strip()

    ruta_pdf = f"./data/{user_id}_informe_{fecha_actual}.pdf"
    historial = [{
        "fecha": fecha_actual,
        "nota": nota_final,
        "comentario": comentario_general
    }]
    crear_pdf_informe_completo_1(ruta_pdf, nombre_usuario, informe_generado, historial)

    pdf_element = cl.Pdf(name=f"{user_id}_informe", display="inline", path=ruta_pdf, page=1)

    await cl.Message(
        content=f"📤 **Informe generado para {nombre_usuario}**\n\n🔽 Puedes visualizarlo aquí:",
        elements=[pdf_element],
        actions=[
            cl.Action(name="enviar_a_empresa", label="📤 Enviar a la empresa", payload={"action": "enviar"}),
            cl.Action(name="cancelar", label="❌ Cancelar", payload={"action": "cancelar"})
        ]
    ).send()























# ---------------- RESPUESTA ABIERTA UNIFICADA ----------------


@cl.on_message
async def manejar_respuesta_abierta(message: cl.Message):
    modo = cl.user_session.get("modo")
    respuesta_usuario = message.content.strip()

    if modo == "objetivo":
        tipo = cl.user_session.get("tipo_pregunta_eval")

        respuestas = cl.user_session.get("respuestas_usuario")
        if respuestas and respuestas[-1]["respuesta_usuario"] is None:
            respuestas[-1]["respuesta_usuario"] = respuesta_usuario
            cl.user_session.set("respuestas_usuario", respuestas)

        if tipo == "abierta":
            await siguiente_pregunta_evaluacion_1()
        elif tipo == "situacion":
            await siguiente_pregunta_evaluacion_1()

    elif modo == "evaluacion":
        tipo = cl.user_session.get("tipo_pregunta_eval")

        respuestas = cl.user_session.get("respuestas_usuario")
        if respuestas and respuestas[-1]["respuesta_usuario"] is None:
            respuestas[-1]["respuesta_usuario"] = respuesta_usuario
            cl.user_session.set("respuestas_usuario", respuestas)

        if tipo == "abierta":
            await siguiente_pregunta_evaluacion()
        elif tipo == "situacion":
            await siguiente_pregunta_evaluacion()

    elif modo == "Preguntas sobre el gimnasio":
        prompt = (
            f"Eres un asistente experto del centro deportivo Classic Fit Gym. "
            f"Aquí tienes la información oficial del centro:\n\n{TEXTO_PDF}\n\n"
            f"Pregunta del usuario: {respuesta_usuario}"
        )
        respuesta = chatbot.chat.send_message(prompt)
        await cl.Message(content=respuesta.text.strip()).send()


    elif modo == "Formación para tu puesto de trabajo":
        modulo_actual = cl.user_session.get("modulo_formacion_actual")
        contenido = SECCIONES_FORMACION.get(modulo_actual, "No se encontró información sobre este módulo.")
        pregunta = respuesta_usuario

        prompt_profesor = (
            "Actúa como un formador experto en Classic Fit. Responde únicamente a la siguiente pregunta del alumno, basándote **exclusivamente** en el siguiente contenido del módulo:"
            f"\n\n---\n{contenido}\n---\n\nPregunta del alumno: {pregunta}"
        )


        respuesta = chatbot.chat.send_message(prompt_profesor)
        await cl.Message(content=respuesta.text.strip()).send()
  