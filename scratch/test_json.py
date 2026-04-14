from fastapi.responses import JSONResponse
import math

try:
    resp = JSONResponse(content={"val": math.nan})
    print("SUCCESS:", resp.body)
except Exception as e:
    print("ERROR:", e)
