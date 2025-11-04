# Agente Conversacional con Memoria y Herramientas (LangChain)

## Descripción
Asistente conversacional inteligente con memoria persistente y herramientas seguras, construido con **LangChain** y **OpenAI GPT-4o-mini**.

## Características
- 🧠 **Memoria conversacional**: Recuerda el contexto de la conversación
- 🔢 **Calculadora segura**: Operaciones matemáticas sin usar `eval()`
- 📏 **Conversor de unidades**: Conversión entre sistemas de medida
- 🌊 **Streaming**: Emisión progresiva de tokens en tiempo real

## Requisitos
- Python 3.10+
- Cuenta de OpenAI con API key

## Instalación

### 1. Crear entorno virtual
```bash
python -m venv venv
```

### 2. Activar el entorno virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia `.env.example` a `.env` y añade tu API key:
```
OPENAI_API_KEY=tu-api-key-aqui
```

## Uso

### Ejecutar en Jupyter Notebook
Abre y ejecuta el notebook `1. Agente con memoria.ipynb` secuencialmente.

## Funcionalidades

### 1. Memoria Conversacional
El agente recuerda el contexto de conversaciones anteriores:
```
Usuario: "Hola, mi nombre es Ana"
Agente: "¡Hola Ana! ..."
Usuario: "¿Recuerdas mi nombre?"
Agente: "Sí, tu nombre es Ana"
```

### 2. Calculadora Segura
Realiza operaciones matemáticas sin riesgos de seguridad:

**Operadores soportados:**
- `+` : Suma
- `-` : Resta
- `*` : Multiplicación
- `/` : División
- `**` : Potencia

**Formato:** `número operador número`

**Ejemplos:**
- "Calcula 25 * 4"
- "¿Cuánto es 100 / 5?"
- "Eleva 2 a la potencia 8"

### 3. Conversor de Unidades
Convierte entre diferentes unidades de medida:

**Formato:** `valor unidad_origen a unidad_destino`

**Unidades soportadas:**

#### Longitud
- `km` - Kilómetros
- `m` - Metros
- `cm` - Centímetros
- `mm` - Milímetros
- `mi` - Millas
- `ft` - Pies
- `in` - Pulgadas

#### Masa
- `kg` - Kilogramos
- `g` - Gramos
- `mg` - Miligramos
- `lb` - Libras
- `oz` - Onzas

#### Temperatura
- `C` - Celsius
- `F` - Fahrenheit
- `K` - Kelvin

**Ejemplos:**
- "Convierte 5 km a metros"
- "¿Cuántos gramos son 2.5 kg?"
- "25 grados Celsius a Fahrenheit"

### 4. Streaming
El agente emite tokens progresivamente, permitiendo ver la respuesta mientras se genera.

## Estructura del Proyecto
```
LANGCHAIN/
├── 1. Agente con memoria.ipynb    # Notebook principal
├── README.md                       # Este archivo
├── requirements.txt                # Dependencias
├── .env                            # Configuración (no en repo)
└── .env.example                    # Plantilla de configuración
```

## Arquitectura Técnica

### Componentes Principales

1. **LLM**: `ChatOpenAI` con modelo `gpt-4o-mini`
2. **Memoria**: `ConversationBufferMemory` para mantener el historial
3. **Agente**: `conversational-react-description` para razonamiento
4. **Tools**: Calculadora y Conversor de Unidades
5. **Callbacks**: `StreamingStdOutCallbackHandler` para streaming

### Flujo de Conversación
```
Usuario → Input → Agente → Razonamiento → Tool (si necesaria) → Output → Usuario
                     ↓
                  Memoria (almacena contexto)
```

## Seguridad

### Calculadora Segura
- ❌ **NO** usa `eval()` para evitar inyección de código
- ✅ Usa operadores seguros del módulo `operator`
- ✅ Valida inputs con expresiones regulares
- ✅ Previene división por cero

### Conversor de Unidades
- ✅ Validación de formatos
- ✅ Lista blanca de unidades permitidas
- ✅ Verificación de compatibilidad entre categorías
- ✅ Manejo robusto de errores

## Ejemplos de Conversaciones

### Ejemplo 1: Memoria + Cálculo
```
Usuario: "Hola, soy estudiante de ingeniería"
Agente: "¡Hola! Es un placer conocerte..."

Usuario: "Calcula 45 * 12"
Agente: [Usa herramienta Calculadora]
        45 * 12 = 540

Usuario: "¿Recuerdas qué estudio?"
Agente: "Sí, eres estudiante de ingeniería"
```

### Ejemplo 2: Conversión Compleja
```
Usuario: "Necesito convertir 2.5 km a pies"
Agente: [Usa herramienta ConvertirUnidades]
        2.5 km = 8202.0997 ft

Usuario: "Y ahora eso mismo pero a metros"
Agente: [Usa herramienta ConvertirUnidades]
        2.5 km = 2500.0000 m
```

## Limitaciones

### Calculadora
- Solo operaciones binarias simples (un operador por vez)
- No soporta paréntesis o expresiones complejas
- Para operaciones complejas, usar múltiples pasos

### Conversor
- No mezcla categorías (no puedes convertir kg a metros)
- Conversiones predefinidas en el código
- Precisión limitada a 4 decimales

## Troubleshooting

### Error: "OpenAI API key not found"
**Solución:** Verifica que `.env` existe y contiene `OPENAI_API_KEY=tu-clave`

### Error: "Formato no válido" en calculadora
**Solución:** Asegúrate de usar el formato: `número operador número`
- ✅ Correcto: "5 + 3"
- ❌ Incorrecto: "5+3" o "(5 + 3) * 2"

### Error: "No se pueden convertir unidades de diferentes categorías"
**Solución:** Verifica que ambas unidades son del mismo tipo (longitud, masa o temperatura)

## Extensiones Futuras

### Posibles Mejoras
1. **Más herramientas**: API del clima, búsqueda web, etc.
2. **Memoria persistente**: Guardar conversaciones en base de datos
3. **Calculadora avanzada**: Soportar expresiones complejas con `sympy`
4. **Más unidades**: Volumen, velocidad, energía, etc.
5. **Interfaz web**: Crear UI con Streamlit o Gradio

## Tecnologías Utilizadas

- **LangChain**: Framework para aplicaciones con LLMs
- **OpenAI GPT-4o-mini**: Modelo de lenguaje
- **Python 3.10+**: Lenguaje de programación
- **python-dotenv**: Gestión de variables de entorno

## Autor
Proyecto educativo - Módulo 6: Agentes Autónomos de IA

## Licencia
Material educativo

---

**Nota:** Este proyecto es parte de un curso de Agentes Autónomos de IA y está diseñado con fines educativos.
