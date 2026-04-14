import requests
import json

try:
    print("Testing Filters...")
    r = requests.get("http://localhost:8000/api/sense/filters")
    print(r.status_code, r.text[:200])
    
    print("\nTesting Chart Data...")
    payload = {
        "from_day": "2023-01-01",
        "to_day": "2025-01-01",
        "ciudad": "All",
        "sucursal": "All",
        "granularity": "hour"
    }
    r2 = requests.post("http://localhost:8000/api/sense/chart-data", json=payload)
    print(r2.status_code, r2.text[:200])

    print("\nTesting AI Analysis...")
    payload_ai = {
        "summary": "Sucursal: All (All). Periodo: 2023-01-01 a 2025-01-01. Uptime: 95.0%. Carga: 2.1A. Desbalance: 1.0%."
    }
    r3 = requests.post("http://localhost:8000/api/sense/ai-analysis", json=payload_ai)
    print(r3.status_code, r3.text[:200])

except Exception as e:
    print(f"Error: {e}")
