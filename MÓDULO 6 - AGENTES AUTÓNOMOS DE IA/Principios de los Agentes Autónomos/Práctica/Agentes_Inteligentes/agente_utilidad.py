class AgenteUtilidad:
    """Agente basado en la utilidad para tomar la decisión más racional."""
    
    def __init__(self, objetivo=24.0, peso_confort=0.8, peso_coste=0.2):
        self.objetivo = objetivo
        self.nombre = "Agente Basado en Utilidad"
        self.w_confort = peso_confort # Peso para la cercanía a la meta
        self.w_coste = peso_coste     # Peso para el ahorro de energía

    def calcular_utilidad(self, temp_resultante, accion):
        """Función de Utilidad = (w_confort * Confort) + (w_coste * Coste/Ahorro).
        RECORDEMOS UTILIDAD:  Percepción-> Maximización de Utilidad ->Acción."""
        
        # 1. Utilidad de Confort (Maximizar cuando temp_resultante está cerca)
        error = abs(temp_resultante - self.objetivo)
        # La utilidad es 1.0 si error=0, disminuye a medida que el error aumenta
        utilidad_confort = max(0, 1 - (error / 5)) 
        
        # 2. Utilidad de Coste (Penalizar acciones que consumen energía)
        coste = 0.0
        if accion in ["Calentar", "Enfriar"]:
            coste = 0.8 # Alta penalización por consumir mucha energía
        else: # Mantener o Apagar es eficiente
            coste = 0.0
            
        utilidad_coste = 1 - coste # Mayor si el coste es menor
        
        # Utilidad Total Ponderada (Decisión racional)
        utilidad_total = (self.w_confort * utilidad_confort) + (self.w_coste * utilidad_coste)
        return utilidad_total

    def ejecutar_ciclo(self, percepcion):
        """Implementa el ciclo Percepción -> Planificación (Maximización) -> Acción."""
        
        # 1. PERCEPCIÓN
        temp_actual = percepcion['temperatura']
        
        # 2. PLANIFICACIÓN (Buscar la máxima Utilidad Esperada)
        acciones_posibles = {
            "Calentar": temp_actual + 1.5,
            "Enfriar": temp_actual - 1.5,
            "Mantener": temp_actual + 0.0,
            "Apagar": temp_actual + 0.5 
        }

        mejor_accion = "Apagar"
        max_utilidad = -float('inf')

        for accion, temp_estimada in acciones_posibles.items():
            utilidad = self.calcular_utilidad(temp_estimada, accion)
            
            if utilidad > max_utilidad:
                max_utilidad = utilidad
                mejor_accion = accion
        
        print(f"[UTILIDAD]: Mejor Acción = {mejor_accion} (Utilidad: {max_utilidad:.2f})")
        
        # 3. ACCIÓN
        return mejor_accion