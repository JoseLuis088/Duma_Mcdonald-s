from backend_db import get_ice_cream_current
import sys

try:
    print("Fetching Mexicali...")
    res = get_ice_cream_current('2026-04-01', '2026-04-12', 'Mexicali', 'Benito Juarez', 'hour')
    print("RES LENGTH:", len(res['labels']))
    print("FIRST 10 LABELS:", res['labels'][:10])
except Exception as e:
    print("ERROR:", e)
    import traceback
    traceback.print_exc()
