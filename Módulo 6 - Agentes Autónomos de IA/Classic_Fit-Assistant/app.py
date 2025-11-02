import uvicorn
from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(root_path="/fit-assistant")

@app.get("/")
async def root():
    return {"message": "Hola desde Docker"}
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/health")
async def check_health_status():
    return {"status": "up"}

@app.get("/")
async def landing():
    base_path = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_path, "web", "index.html"))

mount_chainlit(app=app, target="./main.py", path="/chainlit")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
