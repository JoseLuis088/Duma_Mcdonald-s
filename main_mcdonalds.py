import uvicorn
# Token updated, trigger reload
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pydantic import BaseModel
from backend_db import get_filter_options, get_ice_cream_current, get_soda_machine_data

from fastapi.middleware.cors import CORSMiddleware

from src.ai_handler import duma_agent

app = FastAPI(title="Duma Mcdonald's API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve the static folder using absolute path
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/images", StaticFiles(directory=os.path.join(BASE_DIR, "static/images")), name="images")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(BASE_DIR, "static/index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/sense/filters")
def api_get_filters():
    # Return available cities and sucursales
    filters = get_filter_options()
    return {"status": "success", "data": filters}

class ChartRequest(BaseModel):
    from_day: str
    to_day: str
    ciudad: str = "All"
    sucursal: str = "All"
    granularity: str = "hour"
    device_type: str = "Máquina de nieve"

from fastapi import HTTPException
import traceback

@app.post("/api/sense/chart-data")
def api_chart_data(req: ChartRequest):
    print(f"\n>>>> [DUMA API] PETICION: {req.ciudad} - {req.sucursal} - {req.device_type} <<<<")
    try:
        if req.device_type == "Máquina de sodas":
            data = get_soda_machine_data(req.from_day, req.to_day, req.ciudad, req.sucursal, req.granularity)
        else:
            data = get_ice_cream_current(req.from_day, req.to_day, req.ciudad, req.sucursal, req.granularity)
        print(f">>>> [DUMA API] EXITO: {req.sucursal} ({len(data.get('labels', []))} puntos) <<<<")
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"\n!!!! [DUMA API] ERROR FATAL EN BACKEND !!!!\n{e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class AIAnalysisRequest(BaseModel):
    summary: str

@app.post("/api/sense/ai-analysis")
def api_ai_analysis(req: AIAnalysisRequest):
    print(f"\n>>>> [DUMA API] SOLICITANDO ANALISIS IA <<<<")
    try:
        report = duma_agent.run_analysis(req.summary)
        return {"status": "success", "report": report}
    except Exception as e:
        print(f"!!!! [DUMA API] ERROR IA !!!!\n{e}")
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    input: str
    thread_id: str | None = None

@app.post("/chat/")
def api_chat(req: ChatRequest):
    print(f"\n>>>> [DUMA API] SOLICITANDO CHAT IA <<<<")
    try:
        report = duma_agent.run_analysis(req.input)
        return {"status": "success", "message": report, "thread_id": "duma_chat_thread"}
    except Exception as e:
        print(f"!!!! [DUMA API] ERROR IA CHAT !!!!\n{e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Iniciando servidor Duma Mcdonald's...")
    uvicorn.run("main_mcdonalds:app", host="0.0.0.0", port=8000, reload=False)
