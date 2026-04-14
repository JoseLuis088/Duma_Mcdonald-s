from backend_db import get_ice_cream_current
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

try:
    print("Fetching Juárez Tecnológico...")
    res = get_ice_cream_current('2026-04-01', '2026-04-12', 'Juárez', 'Tecnológico', 'hour')
    print("RES LENGTH:", len(res['labels']))
    
    encoded = jsonable_encoder(res)
    resp = JSONResponse(content={"status": "success", "data": encoded})
    print("SUCCESS! JSONResponse created.")
except Exception as e:
    print("ERROR:", e)
