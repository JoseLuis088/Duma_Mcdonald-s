from backend_db import get_ice_cream_current
import sys
import json

try:
    print("Fetching Chihuahua Juventud...")
    res = get_ice_cream_current('2026-04-01', '2026-04-12', 'Chihuahua', 'Juventud', 'hour')
    print("RES LENGTH:", len(res['labels']))
    
    # Try to JSON serialize
    try:
        json_str = json.dumps(res)
        print("JSON length:", len(json_str))
    except Exception as je:
        print("JSON serialization failed:", je)
except Exception as e:
    print("ERROR:", e)
    import traceback
    traceback.print_exc()
