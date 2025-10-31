
####### EVALUACIÓN

def get_system_prompt() -> str:
    return (
        "Eres un asistente de formación para el centro deportivo S3 Fit Las Rehoyas. "
        "Tu tarea es generar una pregunta de formación a partir del contenido de un documento PDF. "
        "La pregunta debe ser clara, relacionada con el módulo indicado y enfocada en el aprendizaje del usuario."
    )


def generar_pregunta_con_opciones(texto: str) -> str:
    prompt = (
        f"Documento de referencia:\n{texto[:10000]}\n\n"
        f"Genera una pregunta de opción múltiple sobre el contenido del documento. "
        f"Incluye solo una opción correcta entre al menos 3. Devuelve el resultado en este formato:\n\n"
        f"Pregunta: <pregunta>\n"
        f"Opciones:\n- <opción 1>\n- <opción 2>\n- <opción 3>\n"
        f"Respuesta correcta: <opción correcta>"
    )
    return prompt


def generar_pregunta_verdadero_falso(texto: str) -> str:
    prompt = (
        f"Documento de referencia:\n{texto[:10000]}\n\n"
        f"Genera una afirmación verdadera o falsa sobre el contenido del documento. "
        f"Devuelve la pregunta en este formato:\n\n"
        f"Pregunta: <afirmación>\n"
        f"Opciones:\n- Verdadero\n- Falso\n"
        f"Respuesta correcta: <Verdadero o Falso>"
    )
    return prompt

def generar_pregunta_abierta(texto: str) -> str: 
    prompt = (
        f"Genera una pregunta de respuesta abierta basada únicamente en el siguiente contenido del módulo:\n\n"
        f"{texto[:10000]}\n\n"
        f"Devuelve el resultado en este formato:\n"
        f"Pregunta: <pregunta>\n"
        f"Respuesta correcta: <respuesta esperada>"
    )
    return prompt



def generar_prompt_pregunta_situacion(texto: str) -> str: # Le pongo texto para luego especificar si quiere objetivo o pdf completo
    prompt = (
        f"Eres un experto en el centro deportivo Classic Fit Gym y conoces en detalle la siguiente información:\n\n"
        f"{texto[:10000]}\n\n"
        f"Basándote en esta información, plantea una situación realista a un empleado del gimnasio que requiera que tome una decisión o explique cómo actuaría. "
        f"La situación debe ser concisa y relevante para el día a día del gimnasio. No incluyas títulos adicionales. \n\n"
        f"Situación:"
    )
    return prompt


def generar_prompt_feedback_situacion(situacion: str, respuesta_empleado: str) -> str:
    prompt = (
        f"Un empleado se enfrentó a la siguiente situación en el Hotel Atlántico:\n\n"
        f"**Situación:** {situacion}\n\n"
        f"Su respuesta fue:\n\n"
        f"**Respuesta del empleado:** {respuesta_empleado}\n\n"
        f"Evalúa esta respuesta basándote en tu conocimiento experto el hotel Atlántico y las mejores prácticas de atención al cliente y gestión en gimnasios.\n\n"
        f"Genera el feedback constructivo directamente en los siguientes puntos, sin añadir ninguna introducción o conclusión general:\n\n"
        f"**Aspectos positivos:** ¿Qué hizo bien el empleado en su respuesta? Sé específico y menciona las acciones o consideraciones correctas.\n\n"
        f"**Áreas de mejora:** ¿Qué podría haber hecho de manera diferente o qué aspectos faltaron en su respuesta? Ofrece sugerencias concretas y prácticas para mejorar su actuación en el futuro.\n\n"
        f"**Conclusión:** Resume tu evaluación con un breve comentario general sobre la respuesta.\n\n"
        f"##PUNTUACION: (escribe solo un número entre 0 y 1, con hasta dos decimales. No añadas texto antes ni después, ni etiquetas. No seas muy restrictivo al poner la puntuación, evalua al alza.)"



    )
    return prompt



###### FORMACIÓN

def generar_prompt_para_formacion():
    return (
        "Da formato claro y legible al siguiente texto. Sigue estas instrucciones con precisión:\n\n"
        "1. **No incluyas el título principal. Elimínalo completamente.**\n"
        "2. **MUY IMPORTANTE: Resalta en negrita los subtítulos numéricos, como por ejemplo: 1.1, 1.2, 2.3.4, 5.4.3, etc.**\n"
        "3. Formateame correctamente las listas, enumeraciones o estructuras similares. Muestralas atractivas visualmente."
        "4. Usa **saltos de línea adecuados** para separar claramente las secciones y mejorar la lectura.\n"
        "5. **No añadas encabezados nuevos, resúmenes, ni frases introductorias o explicativas**. Solo aplica formato al contenido original.\n"
        "6. Respeta el contenido del texto original: no inventes, resumas ni elimines nada salvo lo indicado arriba.\n\n"
        "Devuelve el texto solo con formato mejorado, listo para mostrar."
    )



