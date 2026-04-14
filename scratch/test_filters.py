import requests

try:
    r = requests.get("http://localhost:8000/api/sense/filters")
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
