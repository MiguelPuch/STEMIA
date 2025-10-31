class AgenteReactivo:
    """Agente reactivo basado en reglas simples (Estímulo-Respuesta)."""
    
    def __init__(self, objetivo=24.0):
        self.objetivo = objetivo
        self.nombre = "Agente Reactivo (Simple)"
        self.reglas = {
            'DemasiadoFrío': "Calentar",
            'DemasiadoCaliente': "Enfriar",
            'Normal': "Mantener"
        }

    def ejecutar_ciclo(self, percepcion):
        """Implementa el ciclo Percepción -> Planificación (Regla) -> Acción."""
        
        # 1. PERCEPCIÓN
        temp_actual = percepcion['temperatura']  # argumento que el método ejecutar_ciclo recibe cuando es llamado por el bucle de simulación (main_simulacion.py).
        
        # 2. PLANIFICACIÓN (Mapeo de Reglas)
        accion = "Apagar"
        if temp_actual < self.objetivo - 2.0:
            accion = self.reglas['DemasiadoFrío']
        elif temp_actual > self.objetivo + 2.0:
            accion = self.reglas['DemasiadoCaliente']
        else:
             accion = self.reglas['Normal']

        # 3. ACCIÓN (Devolver la acción)
        return accion