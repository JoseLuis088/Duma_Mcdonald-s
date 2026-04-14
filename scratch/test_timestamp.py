from backend_db import fetch_ice_cream_data
import sys

df = fetch_ice_cream_data('2026-04-01', '2026-04-12', 'Chihuahua', 'Américas')
if df is not None and not df.empty:
    print(df[['LocalTimeSpan', 'sensor_id', 'measured_avg_value']].head(24))
else:
    print("NO DATA")
