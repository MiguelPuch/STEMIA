import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# --- Autochequeo -------------------------------------------------

exe = sys.executable.replace("\\", "/").lower()
if "anaconda3/python.exe" in exe or "miniconda3/python.exe" in exe:
    raise SystemExit(
        f"\n[ERROR] Estás ejecutando con {sys.executable}.\n"
        "Activa el venv y usa su Python:\n"
        r"   .\agente_mcp_env\Scripts\Activate.ps1" "\n"
        r"   python c:\ruta\a\tu_script.py" "\n"
        "O ejecuta directamente:\n"
        r"   .\agente_mcp_env\Scripts\python.exe c:\ruta\a\tu_script.py" "\n"
    )
# -----------------------------------------------------------------------

from dotenv import load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)

# -----------------------------------------------------------------------------
# 📘 ¿Qué es MCP (Model Context Protocol)?
#
# MCP (Model Context Protocol) es un estándar abierto que define **cómo un
# modelo de lenguaje (LLM)** puede comunicarse con herramientas externas
# (por ejemplo, el sistema de archivos, una base de datos o una API)
# de forma segura y unificada.
#
# Funciona como un "puente" entre el modelo y el entorno:
# - Permite que el LLM explore carpetas, lea archivos o ejecute comandos
#   sin acceso directo al sistema del usuario.
# - Usa un cliente-servidor: el LLM (cliente) se conecta a un "servidor MCP"
#   que expone herramientas específicas.
# - En este ejemplo, usamos `@modelcontextprotocol/server-filesystem`,
#   un servidor MCP que ofrece herramientas como:
#     • list_allowed_directories → muestra las rutas a las que puede acceder.
#     • list_directory → lista archivos dentro de un directorio.
#     • read_file → lee el contenido de un archivo.
# -----------------------------------------------------------------------------

def get_mcp_config() -> dict:
    """Arranca el servidor MCP en la carpeta del propio script (raíz visible)."""
    base_dir = str(Path(__file__).resolve().parent)
    return {
        "filesystem": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", base_dir],
        }
    }

MAX_DEPTH = 6
SHOW_TREE = True
TREE_MAX_ENTRIES = 200

LICENSE_EXACT = {
    "LICENSE", "LICENSE.txt", "LICENSE.md",
    "LICENCE", "LICENCE.txt", "LICENCE.md",
    "COPYING", "COPYING.txt", "COPYING.md",
    "UNLICENSE", "UNLICENSE.txt",
}
LICENSE_FUZZY_PATTERNS = ("license", "licence", "copying", "unlicense")

def _extract_allowed_paths(raw) -> List[str]:
    paths: List[str] = []
    if isinstance(raw, list):
        paths = [str(p).strip() for p in raw if str(p).strip()]
    elif isinstance(raw, str):
        for line in raw.splitlines():
            line = line.strip()
            if not line or (":" in line and not re.match(r"^[A-Za-z]:\\", line)):
                continue
            if re.match(r"^[A-Za-z]:\\", line):
                paths.append(line)
    else:
        s = str(raw)
        for line in s.splitlines():
            line = line.strip()
            if re.match(r"^[A-Za-z]:\\", line):
                paths.append(line)
    return [p for p in paths if os.path.isabs(p)]

async def list_dir(tool, path: str) -> List[Dict[str, Any]]:
    """Lista directorio con varios fallbacks para la raíz."""
    # 1) intento con el path tal cual
    try:
        entries = await tool.ainvoke({"path": path})
        if isinstance(entries, list) and entries:
            return entries
    except Exception:
        pass
    # 2) si es la raíz, prueba "", ".", "/"
    for alt in ("", ".", "/"):
        try:
            entries = await tool.ainvoke({"path": alt})
            if isinstance(entries, list) and entries:
                return entries
        except Exception:
            continue
    # 3) último intento: devuelve lista (posible vacía)
    try:
        entries = await tool.ainvoke({"path": path})
        return entries if isinstance(entries, list) else []
    except Exception:
        return []

async def print_tree(tools_map, root: str, max_entries: int = 200) -> None:
    list_tool = tools_map["list_directory"]
    print("\n📂 Árbol (2 niveles):")
    level0 = await list_dir(list_tool, root)
    print(Path(root).name + "\\")
    for e in level0[:max_entries]:
        print("  [{}] {}".format("D" if e.get("type")=="directory" else "F", e.get("name")))
    for e in level0[:max_entries]:
        if e.get("type") == "directory":
            sub = e.get("path") or os.path.join(root, e.get("name",""))
            lvl1 = await list_dir(list_tool, sub)
            print("  {}\\".format(e.get("name")))
            for f in lvl1[:max_entries]:
                print("    [{}] {}".format("D" if f.get("type")=="directory" else "F", f.get("name")))

def _is_license_name(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return False
    if n in LICENSE_EXACT:
        return True
    nlow = n.lower()
    return any(pat in nlow for pat in LICENSE_FUZZY_PATTERNS)

async def find_license_file(
    tools_map: Dict[str, Any],
    start_dir: str,
    max_depth: int = MAX_DEPTH
) -> Optional[str]:
    list_tool = tools_map["list_directory"]

    async def walk(path: str, depth: int) -> Optional[str]:
        if depth < 0:
            return None
        entries = await list_dir(list_tool, path)

        # 1) ¿Hay licencia en este directorio?
        for e in entries:
            name = (e.get("name") or "").strip()
            etype = (e.get("type") or "").strip().lower()
            if etype == "file" and _is_license_name(name):
                return e.get("path") or os.path.join(path, name)

        # 2) Baja a subdirectorios
        for e in entries:
            if (e.get("type") or "").strip().lower() == "directory":
                sub = e.get("path") or os.path.join(path, e.get("name",""))
                found = await walk(sub, depth - 1)
                if found:
                    return found
        return None

    return await walk(start_dir, max_depth)

async def try_read_license_direct(tools_map: Dict[str, Any], root: str) -> Optional[str]:
    """Intenta leer LICENSE directamente en la raíz con varias variantes."""
    read_tool = tools_map["read_file"]
    candidates = [
        "LICENSE", "LICENSE.txt", "LICENSE.md",
        ".\\LICENSE", ".\\LICENSE.txt", ".\\LICENSE.md",
        "./LICENSE", "./LICENSE.txt", "./LICENSE.md",
        os.path.join(root, "LICENSE"),
        os.path.join(root, "LICENSE.txt"),
        os.path.join(root, "LICENSE.md"),
        os.path.join(root, "license"),
        os.path.join(root, "license.txt"),
        os.path.join(root, "license.md"),
    ]
    for p in candidates:
        try:
            data = await read_tool.ainvoke({"path": p})
            text = data.get("content") if isinstance(data, dict) else (data if isinstance(data, str) else None)
            if text:
                print(f"\n✅ Encontrado por acceso directo: {p}")
                print("\n--- Contenido (inicio) ---\n")
                print(text[:2000])
                print("\n--- Fin del contenido (truncado) ---\n")
                return p
        except Exception:
            continue
    return None

async def main():
    client = MultiServerMCPClient(get_mcp_config())

    async with client.session("filesystem") as fs_session:
        tools = await load_mcp_tools(fs_session)
        tools_map = {t.name: t for t in tools}

        required = {"list_allowed_directories", "list_directory", "read_file"}
        missing = required - set(tools_map.keys())
        if missing:
            raise SystemExit(f"Faltan herramientas MCP necesarias: {missing}")

        # 1) Directorios permitidos
        raw_allowed = await tools_map["list_allowed_directories"].ainvoke({})
        allowed_paths = _extract_allowed_paths(raw_allowed)
        if not allowed_paths:
            raise SystemExit(f"No se pudieron extraer rutas válidas. Respuesta: {raw_allowed!r}")

        root = allowed_paths[0]
        print("\n🔐 Directorio raíz permitido por MCP:")
        for p in allowed_paths:
            print("   ", p)
        print(f"\n📌 Usando como raíz de búsqueda:\n   {root}")

        # 2) Árbol de verificación (ahora con fallbacks de raíz)
        if SHOW_TREE:
            await print_tree(tools_map, root, TREE_MAX_ENTRIES)

        # 3) Intento directo de lectura en raíz
        direct = await try_read_license_direct(tools_map, root)
        if direct:
            return

        # 4) Búsqueda recursiva
        print("\n🔎 Buscando archivo de licencia...")
        lic_path = await find_license_file(tools_map, start_dir=root, max_depth=MAX_DEPTH)

        if not lic_path:
            print("❌ No se encontró archivo de licencia en los niveles explorados.")
            print("   - Asegúrate de que LICENSE.txt está en ESTA carpeta o debajo.")
            print("   - Sube MAX_DEPTH si lo necesitas.")
            return

        print(f"✅ Licencia encontrada: {lic_path}")

        snippet = await read_text_file(tools_map, lic_path, max_bytes=2000)
        print("\n--- Contenido (inicio) ---\n")
        print(snippet)
        print("\n--- Fin del contenido (truncado) ---\n")

if __name__ == "__main__":
    asyncio.run(main())
