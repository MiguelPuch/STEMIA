# Cargamos librerías

import chainlit as cl
import asyncio
import random
import matplotlib.pyplot as plt
import io
import datetime
from reportlab.pdfgen import canvas
import base64
from PIL import Image
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import re
import os, json
from collections import defaultdict
import statistics
import textwrap
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from dotenv import load_dotenv
from chatbot.chatbot import ChatbotPreguntas

import logging
logger = logging.getLogger(__name__)
load_dotenv()
chatbot = ChatbotPreguntas(api_key=os.getenv("GOOGLE_API_KEY"), model_name="gemini-2.0-flash")


## TEXTO

from PyPDF2 import PdfReader

def cargar_pdf_texto(path):
    reader = PdfReader(path)
    texto = ""
    for pagina in reader.pages:
        texto += pagina.extract_text() + "\n"
    return texto

## PUNTUACIÓN PARA OBJETIVOS

def calcular_puntuacion(respuestas_usuario: list, nivel: str = "nivel1") -> float:
    tipos_respuestas = [(r["tipo"],) for r in respuestas_usuario]

    pesos = calcular_pesos_reales(tipos_respuestas, nivel=nivel)

    puntuacion_total = 0.0
    for r in respuestas_usuario:
        tipo = r.get("tipo", "").strip().lower()
        puntos = r.get("puntos", 0.0)
        peso = pesos.get(tipo, 1.0)  
        puntuacion_total += puntos * peso

    return round(puntuacion_total, 2)


PESOS_PERSONALIZADOS = {
    "nivel1": {
        "vf": 1.0,
        "opciones": 1.0,
        "abierta": 0.0,
        "situacion": 0.0
    },
    "nivel2": {
        "vf": 1.0,
        "opciones": 1.0,
        "abierta": 0.0,
        "situacion": 0.0
    },
    "nivel3": {
        "vf": 1.0,
        "opciones": 1.0,
        "abierta": 0.0,
        "situacion": 0.0
    },
    "nivel4": {
        "vf": 0.75,
        "opciones": 1.0,
        "abierta": 1.5,
        "situacion": 0.0
    },
    "nivel5": {
        "vf": 0.5,
        "opciones": 0.75,
        "abierta": 1.0,
        "situacion": 1.5
    },
    "nivel6": {
        "vf": 0.0,
        "opciones": 0.0,
        "abierta": 0.5,
        "situacion": 1.5
    },
    "nivel7": {
        "vf": 0.0,
        "opciones": 0.0,
        "abierta": 0.5,
        "situacion": 1.5
    }
}

def calcular_pesos_reales(tipos_respuestas, nivel="nivel1"):
    pesos_config = PESOS_PERSONALIZADOS.get(nivel, PESOS_PERSONALIZADOS["nivel1"])

    pesos_reales = {}
    for tipo, in tipos_respuestas:
        tipo = tipo.strip().lower()
        peso = pesos_config.get(tipo, 1.0)
        pesos_reales[tipo] = peso

    return pesos_reales




#### RENDIMIENTO DEL EMPLEADO



# ------ GLOBAL --------


def resumir_comentario(contenido_comentario):
    prompt = f"""Resume en una sola línea de forma profesional y clara el siguiente comentario de evaluación:\n\n\"{contenido_comentario.strip()}\"\n\n:"""
    return chatbot.chat.send_message(prompt).text.strip()

def crear_pdf_informe_completo(ruta_pdf, nombre_usuario, texto_informe, historial):


    ancho, alto = letter
    margen_izq = 50
    margen_der = 50
    ancho_texto = ancho - margen_izq - margen_der

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    y = alto - 50

    styles = getSampleStyleSheet()
    style_title = styles['Heading1']
    style_title.fontName = 'Helvetica-Bold'
    style_title.fontSize = 16
    style_title.spaceAfter = 14

    style_subtitle = styles['Heading2']
    style_subtitle.fontName = 'Helvetica-Bold'
    style_subtitle.fontSize = 14
    style_subtitle.spaceAfter = 12

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )

    def markdown_to_html(text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'(<br\s*/?>)+', '', text)  # Elimina cualquier <br>
        return text.strip()

    p = Paragraph(f"Informe de Evaluación Profesional - {nombre_usuario}", style_title)
    w, h = p.wrap(ancho_texto, y)
    if y - h < 50:
        c.showPage()
        y = alto - 50
    p.drawOn(c, margen_izq, y - h)
    y -= h + 20

    p = Paragraph("📄 INFORME GENERAL", style_subtitle)
    w, h = p.wrap(ancho_texto, y)
    if y - h < 50:
        c.showPage()
        y = alto - 50
    p.drawOn(c, margen_izq, y - h)
    y -= h + 10

    bloques = texto_informe.split('\n\n')
    i = 0
    while i < len(bloques):
        bloque_limpio = bloques[i].strip()
        if not bloque_limpio:
            i += 1
            continue

        bloque_html = markdown_to_html(bloque_limpio)

        if bloque_html.startswith('<b>') and i + 1 < len(bloques):
            siguiente_bloque_html = markdown_to_html(bloques[i + 1].strip())

            p_titulo = Paragraph(bloque_html, ParagraphStyle(
                'TitleLike',
                parent=style_normal,
                fontSize=14,
                leading=18,
                spaceAfter=20,
            ))
            p_texto = Paragraph(siguiente_bloque_html, style_normal)

            w1, h1 = p_titulo.wrap(ancho_texto, y)
            w2, h2 = p_texto.wrap(ancho_texto, y - h1 - 20)

            if y - (h1 + h2 + 40) < 50:
                c.showPage()
                y = alto - 50

            p_titulo.drawOn(c, margen_izq, y - h1)
            y -= h1 + 10
            p_texto.drawOn(c, margen_izq, y - h2)
            y -= h2 + 30 
            i += 2
        else:
        
            p = Paragraph(bloque_html, style_normal)
            w, h = p.wrap(ancho_texto, y)
            if y - h < 50:
                c.showPage()
                y = alto - 50
            p.drawOn(c, margen_izq, y - h)
            y -= h + 20
            i += 1


    espacio_tabla_minimo = 200
    if y < espacio_tabla_minimo + 50:
        c.showPage()
        y = alto - 50
    else:
        y -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "📊 RESUMEN RESULTADOS DE LAS EVALUACIONES")
    y -= 30

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Examen")
    c.drawString(110, y, "Fecha")
    c.drawString(180, y, "Nota")
    c.drawString(230, y, "Comentario")
    y -= 25

    c.setFont("Helvetica", 10)

    for idx, e in enumerate(historial):
        if y < 80:
            c.showPage()
            y = alto - 50
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Examen")
            c.drawString(110, y, "Fecha")
            c.drawString(180, y, "Nota")
            c.drawString(230, y, "Comentario")
            y -= 20
            c.setFont("Helvetica", 10)

        examen = f"Examen {idx + 1}"
        fecha = e.get("fecha", "—").split()[0] 
        nota = f"{e.get('nota', '—')}/15"
        comentario = e.get("comentario", "—").replace("\n", " ")
        resumen = resumir_comentario(comentario)

        c.drawString(50, y, examen)
        c.drawString(110, y, fecha)
        c.drawString(180, y, nota)

        x_comentario = 230
        max_width = ancho - x_comentario - 50

        words = resumen.split()
        line = ""
        for word in words:
            prueba_linea = (line + " " + word).strip()
            if c.stringWidth(prueba_linea, "Helvetica", 10) > max_width:
                c.drawString(x_comentario, y, line.strip())
                y -= 12
                line = word
            else:
                line = prueba_linea
        if line:
            c.drawString(x_comentario, y, line.strip())
            y -= 15
        else:
            y -= 15

    fechas = [e["fecha"].split()[0] for e in historial]
    notas = [e["nota"] for e in historial]

    plt.figure(figsize=(6, 2.5))
    plt.plot(fechas, notas, marker='o', color='blue')
    plt.title(f'Evolución de notas de {nombre_usuario}')
    plt.xlabel('Fecha')
    plt.ylabel('Nota')
    plt.ylim(0, 15)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    imagen = ImageReader(buf)


    y -= 180
    if y < 100:
        c.showPage()
        y = alto - 230

    c.drawImage(imagen, 50, y, width=450, height=180)

    c.save()





# ----- OBJETIVOS -----------------


def resumir_comentario_1(contenido_comentario_1):
    prompt = f"""Resume en una sola línea de forma profesional y clara el siguiente comentario de evaluación:\n\n\"{contenido_comentario_1.strip()}. Solo una frase.\"\n\n:"""
    return chatbot.chat.send_message(prompt).text.strip()

def crear_pdf_informe_objetivos(ruta_pdf, nombre_usuario, texto_informe, resumen_por_nivel, grafico_img_bytes):
    ancho, alto = letter
    margen_izq = 50
    margen_der = 50
    ancho_texto = ancho - margen_izq - margen_der

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    y = alto - 50

    styles = getSampleStyleSheet()
    style_title = styles['Heading1']
    style_title.fontName = 'Helvetica-Bold'
    style_title.fontSize = 16
    style_title.spaceAfter = 14

    style_subtitle = styles['Heading2']
    style_subtitle.fontName = 'Helvetica-Bold'
    style_subtitle.fontSize = 14
    style_subtitle.spaceAfter = 12

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )

    def markdown_to_html(text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'(<br\s*/?>)+', '', text)  # Elimina <br>
        return text.strip()

    # Título
    p = Paragraph(f"Informe por Objetivos - {nombre_usuario}", style_title)
    w, h = p.wrap(ancho_texto, y)
    if y - h < 50:
        c.showPage()
        y = alto - 50
    p.drawOn(c, margen_izq, y - h)
    y -= h + 20

    # Subtítulo
    p = Paragraph("📄 INFORME GENERAL", style_subtitle)
    w, h = p.wrap(ancho_texto, y)
    p.drawOn(c, margen_izq, y - h)
    y -= h + 10

    bloques = texto_informe.split('\n\n')
    i = 0
    while i < len(bloques):
        bloque_limpio = bloques[i].strip()
        if not bloque_limpio:
            i += 1
            continue

        bloque_html = markdown_to_html(bloque_limpio)

        if bloque_html.startswith('<b>') and i + 1 < len(bloques):
            siguiente_bloque_html = markdown_to_html(bloques[i + 1].strip())

            p_titulo = Paragraph(bloque_html, ParagraphStyle(
                'TitleLike',
                parent=style_normal,
                fontSize=14,
                leading=18,
                spaceAfter=20,
            ))
            p_texto = Paragraph(siguiente_bloque_html, style_normal)

            w1, h1 = p_titulo.wrap(ancho_texto, y)
            w2, h2 = p_texto.wrap(ancho_texto, y - h1 - 20)

            if y - (h1 + h2 + 40) < 50:
                c.showPage()
                y = alto - 50

            p_titulo.drawOn(c, margen_izq, y - h1)
            y -= h1 + 10
            p_texto.drawOn(c, margen_izq, y - h2)
            y -= h2 + 30 
            i += 2
        else:
        
            p = Paragraph(bloque_html, style_normal)
            w, h = p.wrap(ancho_texto, y)
            if y - h < 50:
                c.showPage()
                y = alto - 50
            p.drawOn(c, margen_izq, y - h)
            y -= h + 20
            i += 1


    espacio_tabla_minimo = 200
    if y < espacio_tabla_minimo + 50:
        c.showPage()
        y = alto - 50
    else:
        y -= 40



    # Estilos para tabla
    style_celda = ParagraphStyle(
        'Celda',
        parent=style_normal,
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=0,
        spaceBefore=0,
    )

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen_izq, y, "📊 Resumen por nivel")
    y -= 25

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margen_izq, y, "Nivel")
    c.drawString(margen_izq + 100, y, "Exámenes")
    c.drawString(margen_izq + 200, y, "Promedio")
    c.drawString(margen_izq + 300, y, "Comentarios Destacados")
    y -= 20

    for nivel, evaluaciones in resumen_por_nivel.items():
        comentarios = [e["comentario"] for e in evaluaciones]
        resumenes = [resumir_comentario_1(com) for com in comentarios[:2]]
        destacados = "; ".join(resumenes)

        promedio = round(statistics.mean([e["nota"] for e in evaluaciones]), 2)

        # Crear Paragraphs para cada columna
        p_nivel = Paragraph(nivel.capitalize(), style_celda)
        p_exams = Paragraph(str(len(evaluaciones)), style_celda)
        p_promedio = Paragraph(f"{promedio}/10", style_celda)
        p_comentarios = Paragraph(markdown_to_html(destacados), style_celda)

        # Anchos de columnas
        ancho_col_1 = 100
        ancho_col_2 = 100
        ancho_col_3 = 100
        ancho_col_4 = ancho_texto - (ancho_col_1 + ancho_col_2 + ancho_col_3)

        # Calcular alturas de cada párrafo para la fila
        w1, h1 = p_nivel.wrap(ancho_col_1, y)
        w2, h2 = p_exams.wrap(ancho_col_2, y)
        w3, h3 = p_promedio.wrap(ancho_col_3, y)
        w4, h4 = p_comentarios.wrap(ancho_col_4, y)

        altura_fila = max(h1, h2, h3, h4)

        if y - altura_fila < 50:
            c.showPage()
            y = alto - 50

        # Dibujar cada columna alineado verticalmente
        p_nivel.drawOn(c, margen_izq, y - h1)
        p_exams.drawOn(c, margen_izq + ancho_col_1, y - h2)
        p_promedio.drawOn(c, margen_izq + ancho_col_1 + ancho_col_2, y - h3)
        p_comentarios.drawOn(c, margen_izq + ancho_col_1 + ancho_col_2 + ancho_col_3, y - h4)

        y -= altura_fila + 5


    espacio_grafico = 200
    if y < espacio_grafico + 50:
        c.showPage()
        y = alto - 50
    else:
        y -= 40

    imagen = ImageReader(io.BytesIO(grafico_img_bytes))
    img_width = 400
    img_height = 150
    img_x = (ancho - img_width) / 2  # Centrado opcional
    c.drawImage(imagen, img_x, y - img_height, width=img_width, height=img_height)

    c.save()
















# --------------- FINAL --------------------


def crear_pdf_informe_completo_1(ruta_pdf, nombre_usuario, texto_informe, historial):


    ancho, alto = letter
    margen_izq = 50
    margen_der = 50
    ancho_texto = ancho - margen_izq - margen_der

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    y = alto - 50

    styles = getSampleStyleSheet()
    style_title = styles['Heading1']
    style_title.fontName = 'Helvetica-Bold'
    style_title.fontSize = 16
    style_title.spaceAfter = 14

    style_subtitle = styles['Heading2']
    style_subtitle.fontName = 'Helvetica-Bold'
    style_subtitle.fontSize = 14
    style_subtitle.spaceAfter = 12

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )

    def markdown_to_html(text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'(<br\s*/?>)+', '', text)  # Elimina cualquier <br>
        return text.strip()

    p = Paragraph(f"Informe de Evaluación Profesional - {nombre_usuario}", style_title)
    w, h = p.wrap(ancho_texto, y)
    if y - h < 50:
        c.showPage()
        y = alto - 50
    p.drawOn(c, margen_izq, y - h)
    y -= h + 20

    p = Paragraph("📄 INFORME GENERAL", style_subtitle)
    w, h = p.wrap(ancho_texto, y)
    if y - h < 50:
        c.showPage()
        y = alto - 50
    p.drawOn(c, margen_izq, y - h)
    y -= h + 10

    bloques = texto_informe.split('\n\n')
    i = 0
    while i < len(bloques):
        bloque_limpio = bloques[i].strip()
        if not bloque_limpio:
            i += 1
            continue

        bloque_html = markdown_to_html(bloque_limpio)

        if bloque_html.startswith('<b>') and i + 1 < len(bloques):
            siguiente_bloque_html = markdown_to_html(bloques[i + 1].strip())

            p_titulo = Paragraph(bloque_html, ParagraphStyle(
                'TitleLike',
                parent=style_normal,
                fontSize=14,
                leading=18,
                spaceAfter=20,
            ))
            p_texto = Paragraph(siguiente_bloque_html, style_normal)

            w1, h1 = p_titulo.wrap(ancho_texto, y)
            w2, h2 = p_texto.wrap(ancho_texto, y - h1 - 20)

            if y - (h1 + h2 + 40) < 50:
                c.showPage()
                y = alto - 50

            p_titulo.drawOn(c, margen_izq, y - h1)
            y -= h1 + 10
            p_texto.drawOn(c, margen_izq, y - h2)
            y -= h2 + 30 
            i += 2
        else:
        
            p = Paragraph(bloque_html, style_normal)
            w, h = p.wrap(ancho_texto, y)
            if y - h < 50:
                c.showPage()
                y = alto - 50
            p.drawOn(c, margen_izq, y - h)
            y -= h + 20
            i += 1

    
    c.save()
