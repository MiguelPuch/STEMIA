import random

class EntornoHVAC:
    """Simula un entorno de Calefacción, Ventilación y Aire Acondicionado (HVAC)."""
    def __init__(self, temp_inicial=22.0, objetivo_temp=24.0):
        self.temperatura = temp_inicial
        self.estado_hvac = "Apagado"
        self.objetivo_temp = objetivo_temp
        print(f"--- Entorno Inicializado: Temp = {self.temperatura:.1f}°C, Objetivo = {self.objetivo_temp:.1f}°C ---")

    def percibir(self):
        """Devuelve la percepción actual del entorno."""
        return {
            "temperatura": self.temperatura,
            "objetivo": self.objetivo_temp,
            "estado_hvac": self.estado_hvac
        }

    def actuar(self, accion):
        """Ejecuta una acción y actualiza el entorno."""
        if accion == "Calentar":
            self.temperatura += 1.5
            self.estado_hvac = "Calentando"
        elif accion == "Enfriar":
            self.temperatura -= 1.5
            self.estado_hvac = "Enfriando"
        elif accion == "Mantener":
            # Variación natural
            self.temperatura += random.uniform(-0.5, 0.5) 
            self.estado_hvac = "Manteniendo"
        else:
            # Tendencia natural al calor
            self.temperatura += random.uniform(-0.3, 0.7) 
            self.estado_hvac = "Apagado"
        
        # Redondear y simular ruido (más realista)
        self.temperatura = round(self.temperatura, 1)

        print(f"-> ACCIÓN: {accion} | Nuevo estado: {self.temperatura:.1f}°C, {self.estado_hvac}")
        return self.percibir()