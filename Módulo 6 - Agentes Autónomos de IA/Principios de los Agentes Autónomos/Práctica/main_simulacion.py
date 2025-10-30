import os
import sys

# =================================================================
# 1. FORZAR LA RUTA DE BÚSQUEDA DEL DIRECTORIO ACTUAL (CRÍTICO)
# Esto añade la carpeta 'Práctica' al path de Python para que pueda encontrar
# el paquete 'Agentes_Inteligentes' que está dentro. NO ES MEGANECESARIO SI ESTAIS EN LA RUTA QUE TOCA.
# =================================================================

directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

# =================================================================
# 2. IMPORTACIONES DEL PAQUETE 
# =================================================================

from Agentes_Inteligentes.entorno import EntornoHVAC
from Agentes_Inteligentes.agente_reactivo import AgenteReactivo
from Agentes_Inteligentes.agente_deliberativo import AgenteDeliberativo
from Agentes_Inteligentes.agente_utilidad import AgenteUtilidad


def simular_agente(agente, entorno, ciclos=6):
    """
    Ejecuta el ciclo de vida Percepción-Planificación-Acción (P-P-A) para un agente.
    """
    print("\n" + "="*70)
    print(f"SIMULACIÓN INICIADA: {agente.nombre} | Objetivo: {entorno.objetivo_temp:.1f}°C")
    print("="*70)
    
    percepcion_actual = entorno.percibir()

    for i in range(1, ciclos + 1):
        print(f"\n--- Ciclo {i} | Temp Inicial: {percepcion_actual['temperatura']:.1f}°C ---")
        
        # FASE 2: PLANIFICACIÓN (El agente decide)
        accion_elegida = agente.ejecutar_ciclo(percepcion_actual)
        
        # FASE 3: ACCIÓN (El entorno actúa y cambia)
        percepcion_actual = entorno.actuar(accion_elegida)
        
        # Analizar el resultado del ciclo
        if abs(percepcion_actual['temperatura'] - entorno.objetivo_temp) <= 1.0:
            print("    *** [RESULTADO]: Temperatura dentro del rango aceptable. ***")
        
        
if __name__ == "__main__":
    
    # ----------------------------------------------------
    # 1. PRUEBA DEL AGENTE REACTIVO
    # ----------------------------------------------------

    entorno_r = EntornoHVAC(temp_inicial=19.0, objetivo_temp=24.0)
    agente_r = AgenteReactivo(objetivo=24.0)
    simular_agente(agente_r, entorno_r, ciclos=6)
    
    # ----------------------------------------------------
    # 2. PRUEBA DEL AGENTE DELIBERATIVO
    # ----------------------------------------------------

    entorno_d = EntornoHVAC(temp_inicial=18.0, objetivo_temp=23.0)
    agente_d = AgenteDeliberativo(objetivo=23.0)
    simular_agente(agente_d, entorno_d, ciclos=6)
    
    # ----------------------------------------------------
    # 3. PRUEBA DEL AGENTE BASADO EN UTILIDAD
    # ----------------------------------------------------
    
    entorno_u = EntornoHVAC(temp_inicial=25.5, objetivo_temp=24.0)
    agente_u = AgenteUtilidad(objetivo=24.0, peso_confort=0.5, peso_coste=0.5) 
    simular_agente(agente_u, entorno_u, ciclos=6)