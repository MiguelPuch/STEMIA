import os
import json
from datetime import datetime

CARPETA_HISTORIAL = "data"

#def guardar_evaluacion_usuario(user_id, nota, comentario, resumen):
    #os.makedirs(CARPETA_HISTORIAL, exist_ok=True)
    #ruta = os.path.join(CARPETA_HISTORIAL, f"{user_id}.json")

    #nueva_evaluacion = {
        #"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #"nota": nota,
        #"comentario": comentario,
        #"resumen": resumen
    #}

    #if os.path.exists(ruta):
        #with open(ruta, "r", encoding="utf-8") as f:
            #historial = json.load(f)
    #else:
        #historial = []

    #historial.insert(0, nueva_evaluacion)  # Lo más reciente primero
    #historial = historial[:5]  # Solo los últimos 5

    #with open(ruta, "w", encoding="utf-8") as f:
        #json.dump(historial, f, indent=2, ensure_ascii=False)


def cargar_historial_usuario(user_id):
    ruta = os.path.join(CARPETA_HISTORIAL, f"{user_id}.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
