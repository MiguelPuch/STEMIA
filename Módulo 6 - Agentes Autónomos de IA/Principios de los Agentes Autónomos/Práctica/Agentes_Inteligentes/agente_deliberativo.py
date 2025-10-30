class AgenteDeliberativo:
    """Agente deliberativo con planificación hacia un objetivo."""
    
    def __init__(self, objetivo=24.0):
        self.objetivo = objetivo
        self.nombre = "Agente Deliberativo (Objetivos)"
        self.plan = [] # Estado interno para almacenar el plan

    def ejecutar_ciclo(self, percepcion):
        """Implementa el ciclo Percepción -> Planificación (Lógica) -> Acción."""
        
        # 1. PERCEPCIÓN
        temp_actual = percepcion['temperatura']
        
        # 2. PLANIFICACIÓN (Deliberación)
        if not self.plan: # Si no hay plan, se genera uno nuevo (deliberación)
            print(f"[DELIBERA]: Generando un nuevo plan de acción...")
            
            diferencia = temp_actual - self.objetivo
            
            if abs(diferencia) <= 1.0:
                # Cerca del objetivo: plan de mantenimiento
                self.plan = ["Mantener"] * 3
            elif diferencia > 1.0:
                # Demasiado caliente: plan de enfriamiento
                self.plan = ["Enfriar"] * 2 + ["Mantener"]
            elif diferencia < -1.0:
                # Demasiado frío: plan de calentamiento
                self.plan = ["Calentar"] * 2 + ["Mantener"]
        
        # 3. ACCIÓN
        # Ejecutar la primera acción del plan y eliminarla para el siguiente ciclo
        accion = self.plan.pop(0) 
        return accion