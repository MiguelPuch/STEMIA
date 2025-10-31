import google.generativeai as genai
import fitz
import os
import random
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from chatbot.prompt import (
    generar_pregunta_con_opciones,
    generar_pregunta_verdadero_falso,
    generar_pregunta_abierta,
    generar_prompt_feedback_situacion,
    generar_prompt_pregunta_situacion
)


class ChatbotPreguntas:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash", pdf_path="./Classic_Fit.pdf"):
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY', '')
        self.model_name = model_name or os.getenv('LLM_MODEL', 'gemini-2.0-flash')
        self.pdf_path = pdf_path

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.chat = self.model.start_chat(history=[])
        self.document_text = self.extract_text_from_pdf()

    def extract_text_from_pdf(self) -> str:
        doc = fitz.open(self.pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def extraer_bloque(texto, inicio, fin):
        try:
            i = texto.index(inicio)
            j = texto.index(fin) if fin else len(texto)
            return texto[i:j].strip()
        except ValueError:
            return f"⚠️ No se encontró la sección que comienza por: '{inicio}'"

    def extraer_secciones_pdf(self):
        reader = PdfReader(self.pdf_path)
        texto = ""

        for pagina in reader.pages[3:]:
            texto += pagina.extract_text() + "\n"

        secciones = {
            "nivel1": ChatbotPreguntas.extraer_bloque(texto, "El centro", "Servicios, Suscripciones, Modalidades de Abonos y Actividades"),
            "nivel2": ChatbotPreguntas.extraer_bloque(texto, "Servicios, Suscripciones, Modalidades de Abonos y Actividades", "Tarifas y formas de pago"),
            "nivel3": ChatbotPreguntas.extraer_bloque(texto, "Tarifas y formas de pago", "Normas y Políticas de uso de las instalaciones"),
            "nivel4": ChatbotPreguntas.extraer_bloque(texto, "Normas y Políticas de uso de las instalaciones", "Trámites"),
            "nivel5": ChatbotPreguntas.extraer_bloque(texto, "Trámites", "Preguntas Frecuentes (FAQs)"),
            "nivel6": ChatbotPreguntas.extraer_bloque(texto, "Preguntas Frecuentes (FAQs)", "Atención al Cliente"),
            "nivel7": ChatbotPreguntas.extraer_bloque(texto, "Atención al Cliente", None)
        }

        return secciones


    def generar_pregunta_con_opciones_func(self,texto: str):
        prompt = generar_pregunta_con_opciones(texto)

        response = self.chat.send_message(prompt).text

        try:
            pregunta = response.split("Pregunta:")[1].split("Opciones:")[0].strip()
            opciones = [line.strip("- ").strip() for line in response.split("Opciones:")[1].split("Respuesta correcta:")[0].strip().split("\n")]
            respuesta_correcta = response.split("Respuesta correcta:")[1].strip()

            if respuesta_correcta not in opciones:
                opciones.append(respuesta_correcta)
            opciones = random.sample(opciones, k=min(len(opciones), 3))

            return pregunta, opciones, respuesta_correcta

        except Exception as e:
            return (
                "❌ No se pudo generar una pregunta correctamente.",
                ["Error al procesar opciones."],
                "N/A"
            )
        
    # -------------- Q. V/F ---------------------------------

    def generar_pregunta_verdadero_falso_func(self,texto: str):
        prompt = generar_pregunta_verdadero_falso(texto)

        response = self.chat.send_message(prompt).text

        try:
            pregunta = response.split("Pregunta:")[1].split("Opciones:")[0].strip()
            opciones = ["Verdadero", "Falso"]
            respuesta_correcta = response.split("Respuesta correcta:")[1].strip()
            return pregunta, opciones, respuesta_correcta

        except Exception as e:
            return (
                "❌ No se pudo generar una pregunta verdadero/falso correctamente.",
                ["Verdadero", "Falso"],
                "N/A"
            )


    # -------------- Q. ABIERTAS ---------------------------------


    def generar_pregunta_abierta_func(self,texto: str):
        prompt = generar_pregunta_abierta(texto)

        response = self.chat.send_message(prompt).text

        try:
            pregunta = response.split("Pregunta:")[1].split("Respuesta correcta:")[0].strip()
            respuesta_correcta = response.split("Respuesta correcta:")[1].strip()
            return pregunta, respuesta_correcta
        except Exception:
            return "❌ No se pudo generar la pregunta correctamente.", "N/A"


    # ------------- Q. SITUACIONES ----------------------------------

    def generar_pregunta_situacion(self,texto):
        prompt = generar_prompt_pregunta_situacion(texto)
        response = self.model.generate_content(prompt)
        pregunta_texto = response.text.strip()
        return "situacion", pregunta_texto, [], ""

    def generar_feedback_situacion(self,pregunta: str, respuesta: str) -> tuple[str, float]:
            prompt = generar_prompt_feedback_situacion(pregunta, respuesta)
            respuesta_llm = self.chat.send_message(prompt).text

            puntuacion = 0.0
            lineas = respuesta_llm.splitlines()
            lineas_visibles = []

            for linea in lineas:
                if "##PUNTUACION:" in linea:
                    try:
                        puntuacion = float(linea.split(":")[1].strip())
                    except:
                        puntuacion = 0.0
                else:
                    lineas_visibles.append(linea)

            texto_feedback = "\n".join(lineas_visibles).strip()
            return texto_feedback, puntuacion


    #########################
    ### 10 Q. OBJETIVOS #####
    #########################


    def generar_lote_preguntas_por_objetivo(self,texto_bloque):
        preguntas = []

        for _ in range(2):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))

        for _ in range(2):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        for _ in range(3): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))

        for _ in range(3): 
            tipo, pregunta, opciones, correcta = self.generar_pregunta_situacion(texto_bloque)
            preguntas.append((tipo, pregunta, opciones, correcta))

        return preguntas

    # ---- NIVEL 1 -------

    def generar_lote_preguntas_por_objetivo_nivel1(self,texto_bloque):
        preguntas = []

        for _ in range(5):
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))

        for _ in range(5):
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        return preguntas

    # ---- NIVEL 2 ------- 

    def generar_lote_preguntas_por_objetivo_nivel2(self,texto_bloque):
        preguntas = []

        for _ in range(5):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))

        for _ in range(5):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        return preguntas

    # ---- NIVEL 3 -------

    def generar_lote_preguntas_por_objetivo_nivel3(self,texto_bloque):
        preguntas = []

        for _ in range(5):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))

        for _ in range(5):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        return preguntas

    # ---- NIVEL 4 -------

    def generar_lote_preguntas_por_objetivo_nivel4(self,texto_bloque):
        preguntas = []

        for _ in range(4):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))

        for _ in range(4):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        for _ in range(2): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))


        return preguntas

    # ---- NIVEL 5 -------

    def generar_lote_preguntas_por_objetivo_nivel5(self,texto_bloque):
        preguntas = []

        for _ in range(2):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))

        for _ in range(2):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        for _ in range(3): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))

        for _ in range(3): 
            tipo, pregunta, opciones, correcta = self.generar_pregunta_situacion(texto_bloque)
            preguntas.append((tipo, pregunta, opciones, correcta))

        return preguntas


    # ---- NIVEL 6 -------

    def generar_lote_preguntas_por_objetivo_nivel6(self,texto_bloque):
        preguntas = []

        for _ in range(5): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))

        for _ in range(5): 
            tipo, pregunta, opciones, correcta = self.generar_pregunta_situacion(texto_bloque)
            preguntas.append((tipo, pregunta, opciones, correcta))

        return preguntas


    # ---- NIVEL 7 -------

    def generar_lote_preguntas_por_objetivo_nivel7(self,texto_bloque):
        preguntas = []

        for _ in range(5): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))

        for _ in range(5): 
            tipo, pregunta, opciones, correcta = self.generar_pregunta_situacion(texto_bloque)
            preguntas.append((tipo, pregunta, opciones, correcta))

        return preguntas




    #########################
    ### 20 Q.EVAL FINAL ####
    #########################

    # ---- NIVEL 1 -------

    def generar_lote_preguntas_por_objetivo_nivel1_final(self,texto_bloque):
        preguntas = []

        for _ in range(2):
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))


        return preguntas

    # ---- NIVEL 2 ------- 

    def generar_lote_preguntas_por_objetivo_nivel2_final(self,texto_bloque):
        preguntas = []

        for _ in range(2):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))


        return preguntas

    # ---- NIVEL 3 -------

    def generar_lote_preguntas_por_objetivo_nivel3_final(self,texto_bloque):
        preguntas = []

        for _ in range(1):  
            pregunta, opciones, correcta = self.generar_pregunta_verdadero_falso_func(texto_bloque)
            preguntas.append(("vf", pregunta, opciones, correcta))
        
        for _ in range(2):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        return preguntas

    # ---- NIVEL 4 -------

    def generar_lote_preguntas_por_objetivo_nivel4_final(self,texto_bloque):
        preguntas = []


        for _ in range(3):  
            pregunta, opciones, correcta = self.generar_pregunta_con_opciones_func(texto_bloque)
            preguntas.append(("opciones", pregunta, opciones, correcta))

        for _ in range(2): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))


        return preguntas

    # ---- NIVEL 5 -------

    def generar_lote_preguntas_por_objetivo_nivel5_final(self,texto_bloque):
        preguntas = []


        for _ in range(2): 
            pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
            preguntas.append(("abierta", pregunta, [], correcta))


        return preguntas


    # ---- NIVEL 6 -------

    def generar_lote_preguntas_por_objetivo_nivel6_final(self,texto_bloque):
        preguntas = []

        for _ in range(1): 
            try:
                pregunta, correcta = self.generar_pregunta_abierta_func(texto_bloque)
                preguntas.append(("abierta", pregunta, [], correcta))
            except Exception as e:
                print(f"❌ Error pregunta abierta nivel 6: {e}")

        for _ in range(2): 
            try:
                tipo, pregunta, opciones, correcta = self.generar_pregunta_situacion(texto_bloque)
                preguntas.append((tipo, pregunta, opciones, correcta))
            except Exception as e:
                print(f"❌ Error pregunta situación nivel 6: {e}")

        return preguntas


    # ---- NIVEL 7 -------

    def generar_lote_preguntas_por_objetivo_nivel7_final(self,texto_bloque):
        preguntas = []


        for _ in range(3): 
            tipo, pregunta, opciones, correcta = self.generar_pregunta_situacion(texto_bloque)
            preguntas.append((tipo, pregunta, opciones, correcta))

        return preguntas
