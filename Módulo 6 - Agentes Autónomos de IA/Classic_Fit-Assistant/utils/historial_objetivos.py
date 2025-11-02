import os
import json
from datetime import datetime

CARPETA_HISTORIAL = "data"


def cargar_historial_usuario_objetivos(user_id):
    ruta = os.path.join(CARPETA_HISTORIAL, f"{user_id}_objetivos.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
