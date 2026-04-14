import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

# Always load .env from the same directory as this file, regardless of CWD
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(_HERE, ".env"), override=True)

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

def ensure_utf8(val):
    if val is None:
        return ""
    if isinstance(val, (bytes, bytearray)):
        return val.decode('utf-8', errors='replace').strip()
    
    # Python strings from Databricks might be garbled if they were meant to be UTF-8 but treated as Latin1
    s = str(val).strip()
    # Check for the replacement character \ufffd
    if '\ufffd' in s:
        try:
            # Common fix for Databricks/connector character scrambling
            return s.encode('latin1').decode('utf-8')
        except:
            pass
    return s

def get_filter_options():
    try:
        mapping = {}
        all_sucursales = set()
        
        with sql.connect(server_hostname=DATABRICKS_HOST, http_path=DATABRICKS_HTTP_PATH, access_token=DATABRICKS_TOKEN) as connection:
            with connection.cursor() as cursor:
                # Fetch distinct pairs of city and location
                cursor.execute("SELECT DISTINCT city_name, location_name FROM prod.silver.00_dimensions WHERE city_name IS NOT NULL AND location_name IS NOT NULL ORDER BY city_name, location_name")
                for row in cursor.fetchall():
                    city = ensure_utf8(row[0])
                    loc = ensure_utf8(row[1])
                    if city not in mapping:
                        mapping[city] = []
                    if loc not in mapping[city]:
                        mapping[city].append(loc)
                    all_sucursales.add(loc)
                    
        return {
            "ciudades": sorted(list(mapping.keys())), 
            "mapping": mapping,
            "sucursales": sorted(list(all_sucursales))
        }
    except Exception as e:
        print(f"Error fetching filters: {e}")
        return {"ciudades": [], "mapping": {}, "sucursales": []}

def fetch_ice_cream_data(from_day, to_day, ciudad, sucursal="All"):
    base_query = f"""
    SELECT 
        e.LocalTimeSpan,
        e.measured_avg_value,
        d.SensorId as sensor_id
    FROM prod.gold.43_sensor_hourly_evidence e
    JOIN prod.silver.00_dimensions d ON e.sensor_id = d.SensorId
    WHERE d.device_type = 'Máquina de nieve'
      AND d.sensor_type = 'Corriente'
      AND CAST(e.LocalTimeSpan AS DATE) >= '{from_day}'
      AND CAST(e.LocalTimeSpan AS DATE) <= '{to_day}'
    """
    if ciudad != "All":
        base_query += f" AND d.city_name = '{ciudad}'"
    
    if sucursal != "All":
        base_query += f" AND d.location_name = '{sucursal}'"
        
    base_query += " ORDER BY e.LocalTimeSpan ASC"
    query = base_query
    
    print(f"Ejecutando consulta en Databricks: {query}")
    try:
        with sql.connect(server_hostname=DATABRICKS_HOST,
                         http_path=DATABRICKS_HTTP_PATH,
                         access_token=DATABRICKS_TOKEN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                return df
    except Exception as e:
        print(f"Databricks SQL Error: {e}")
        return pd.DataFrame()

def get_ice_cream_current(from_day, to_day, ciudad, sucursal="All", granularity="hour"):
    df = fetch_ice_cream_data(from_day, to_day, ciudad, sucursal)
    if df.empty:
        return {"labels": [], "datasets": [], "kpis": {}}
    
    # Ensure LocalTimeSpan is datetime and sort
    df['LocalTimeSpan'] = pd.to_datetime(df['LocalTimeSpan'], errors='coerce')
    df = df.dropna(subset=['LocalTimeSpan'])
    
    df = df.sort_values('LocalTimeSpan')
    
    # --- KPI Calculation (ALWAYS on hourly data) ---
    kpis = analyze_kpis(df.copy(), from_day, to_day)
    
    # Handle Daily Granularity for the Chart only
    if granularity == "day":
        df['LocalTimeSpan'] = df['LocalTimeSpan'].dt.normalize()
        df = df.groupby(['LocalTimeSpan', 'sensor_id'])['measured_avg_value'].mean().reset_index()
        df = df.sort_values('LocalTimeSpan')
    
    # Get unique timestamps for labels
    if granularity == "day":
        fmt = '%Y-%m-%d'
    else:
        fmt = '%Y-%m-%d %H:%M'
        
    labels_series = df['LocalTimeSpan'].dt.strftime(fmt).drop_duplicates()
    labels = labels_series.tolist()
    
    # Group by sensor_id
    datasets = []
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#e67e22', '#e74c3c']
    
    for idx, (sensor, group) in enumerate(df.groupby('sensor_id')):
        # Map values to the labels
        group_dict = dict(zip(group['LocalTimeSpan'].dt.strftime(fmt), group['measured_avg_value']))
        
        # Build data array strictly matching the labels index
        data = []
        for label in labels:
            val = group_dict.get(label)
            if pd.notnull(val):
                data.append(float(val))
            else:
                data.append(None)
        
        datasets.append({
            "label": f"Fase {idx+1}",
            "data": data,
            "borderColor": colors[idx % len(colors)],
            "fill": False,
            "tension": 0.1
        })
        
    return {"labels": labels, "datasets": datasets, "kpis": kpis}

def analyze_kpis(df, start_date=None, end_date=None):
    """
    [Duma] Expert logic for Ice Cream machines based on hourly amperage patterns.
    """
    if df.empty:
        return {"availability": "0%", "heat_cycle": "N/A", "avg_load": "0A", "missing_hours": 0}

    # Ensure LocalTimeSpan is datetime
    df['LocalTimeSpan'] = pd.to_datetime(df['LocalTimeSpan'])
    
    # 1. Availability: hours between 9 AM and 10 PM with activity > 0.5A
    # We take the max current across all phases for each hour to know if the machine was ON
    hourly_max = df.groupby('LocalTimeSpan')['measured_avg_value'].max().reset_index()
    
    df_day = hourly_max[(hourly_max['LocalTimeSpan'].dt.hour >= 9) & (hourly_max['LocalTimeSpan'].dt.hour <= 22)]
    if not df_day.empty:
        active_hours = df_day[df_day['measured_avg_value'] > 0.5].shape[0]
        total_hours = df_day.shape[0]
        avail = (active_hours / total_hours) * 100
    else:
        avail = 0.0

    # 2. Heat Cycle: Expert Window (11 PM - 6 AM). 
    # Logic: Success if detected variability (Max - Min > 1.0A) during the window.
    # This ignores steady electronic baselines and focuses on cycle activity.
    night_mask = (hourly_max['LocalTimeSpan'].dt.hour >= 23) | (hourly_max['LocalTimeSpan'].dt.hour <= 6)
    df_night = hourly_max[night_mask]
    days = hourly_max['LocalTimeSpan'].dt.date.unique()
    success_days = 0
    
    # Calculate Daily Availability for the second chart
    daily_stats = []
    
    for d in days:
        night_sample = df_night[df_night['LocalTimeSpan'].dt.date == d]
        # Expert heuristic: Range > 1.0A indicates heater activity
        if not night_sample.empty:
            v_range = night_sample['measured_avg_value'].max() - night_sample['measured_avg_value'].min()
            if v_range > 1.0:
                success_days += 1
            
        # Daily Avail for chart
        day_samples = hourly_max[hourly_max['LocalTimeSpan'].dt.date == d]
        day_active = day_samples[(day_samples['LocalTimeSpan'].dt.hour >= 9) & 
                                 (day_samples['LocalTimeSpan'].dt.hour <= 22) & 
                                 (day_samples['measured_avg_value'] > 0.5)].shape[0]
        day_total = day_samples[(day_samples['LocalTimeSpan'].dt.hour >= 9) & 
                                (day_samples['LocalTimeSpan'].dt.hour <= 22)].shape[0]
        day_avail = (day_active / day_total * 100) if day_total > 0 else 0
        daily_stats.append({"date": d.strftime('%Y-%m-%d'), "value": round(day_avail, 1)})
    
    heat_rate = (success_days / len(days)) * 100 if len(days) > 0 else 0

    # 3. Load & Imbalance during active work (>1.0A)
    # We group by timestamp to look at the phases together for each hour
    active_snapshots = df[df['measured_avg_value'] > 1.0].groupby('LocalTimeSpan')['measured_avg_value'].apply(list)
    
    peak_loads = []
    imbalances = []
    
    for vals in active_snapshots:
        if len(vals) > 0:
            m_val = max(vals)
            peak_loads.append(m_val)
            # Imbalance formula: (Max Dev from Mean / Mean) * 100
            if len(vals) >= 2: 
                avg_val = sum(vals) / len(vals)
                if avg_val > 0.1: # Avoid division by zero
                    max_dev = max([abs(v - avg_val) for v in vals])
                    imb = (max_dev / avg_val) * 100
                    imbalances.append(imb)

    final_max_load = sum(peak_loads) / len(peak_loads) if peak_loads else 0.0
    final_imbalance = sum(imbalances) / len(imbalances) if imbalances else 0.0

    # 4. Detect Information Gaps (Missing Hours)
    missing_count = 0
    if start_date and end_date:
        expected_range = pd.date_range(start=start_date, end=pd.to_datetime(end_date) + pd.Timedelta(hours=23), freq='h')
        actual_hours = df['LocalTimeSpan'].dt.floor('h').unique()
        missing_count = len(expected_range) - len(set(actual_hours) & set(expected_range))
        # Ensure we don't have negative (can happen with timezone shifts)
        missing_count = max(0, missing_count)

    return {
        "availability": f"{avail:.1f}%",
        "heat_cycle": f"{heat_rate:.0f}%",
        "avg_load": f"{final_max_load:.2f}A", # Keep key name but value is now Peak
        "imbalance": f"{final_imbalance:.1f}%",
        "daily_availability": daily_stats,
        "missing_hours": missing_count
    }

if __name__ == "__main__":
    # Test block
    print("Testing Filters...")
    print(get_filter_options())
    print("Testing Chart...")
    res = get_ice_cream_current('2023-01-01', '2026-12-31')
    print(res)

# ============================================================
# SODA MACHINE (Máquina de sodas)
# device_type = 'Máquina de sodas'
# sensor_type = 'Corriente' | 'Presión'
# ============================================================

SODA_DEVICE_TYPE = 'Máquina de sodas'

def _soda_query_base(sensor_type, from_day, to_day, ciudad, sucursal):
    q = f"""
    SELECT
        e.LocalTimeSpan,
        e.measured_avg_value,
        d.SensorId as sensor_id
    FROM prod.gold.43_sensor_hourly_evidence e
    JOIN prod.silver.00_dimensions d ON e.sensor_id = d.SensorId
    WHERE d.device_type = '{SODA_DEVICE_TYPE}'
      AND d.sensor_type = '{sensor_type}'
      AND CAST(e.LocalTimeSpan AS DATE) >= '{from_day}'
      AND CAST(e.LocalTimeSpan AS DATE) <= '{to_day}'
    """
    if ciudad != "All":
        q += f" AND d.city_name = '{ciudad}'"
    if sucursal != "All":
        q += f" AND d.location_name = '{sucursal}'"
    q += " ORDER BY e.LocalTimeSpan ASC"
    return q

def _run_databricks_query(query):
    try:
        with sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        print(f"Databricks SQL Error: {e}")
        return pd.DataFrame()

def fetch_soda_current_data(from_day, to_day, ciudad, sucursal="All"):
    q = _soda_query_base('Corriente', from_day, to_day, ciudad, sucursal)
    print(f"[Soda Current] Query: {q[:120]}...")
    return _run_databricks_query(q)

def fetch_soda_pressure_data(from_day, to_day, ciudad, sucursal="All"):
    q = _soda_query_base('Presión', from_day, to_day, ciudad, sucursal)
    print(f"[Soda Pressure] Query: {q[:120]}...")
    return _run_databricks_query(q)

def get_soda_machine_data(from_day, to_day, ciudad, sucursal="All", granularity="hour"):
    df_cur = fetch_soda_current_data(from_day, to_day, ciudad, sucursal)
    df_pres = fetch_soda_pressure_data(from_day, to_day, ciudad, sucursal)

    if df_cur.empty:
        return {"labels": [], "datasets": [], "kpis": {}, "pressure_data": None}

    # --- Process current data (identical to ice cream) ---
    df_cur['LocalTimeSpan'] = pd.to_datetime(df_cur['LocalTimeSpan'], errors='coerce')
    df_cur = df_cur.dropna(subset=['LocalTimeSpan']).sort_values('LocalTimeSpan')

    # KPIs calculated from hourly current
    kpis = analyze_kpis(df_cur.copy(), from_day, to_day)

    if granularity == "day":
        df_cur['LocalTimeSpan'] = df_cur['LocalTimeSpan'].dt.normalize()
        df_cur = df_cur.groupby(['LocalTimeSpan', 'sensor_id'])['measured_avg_value'].mean().reset_index()
        df_cur = df_cur.sort_values('LocalTimeSpan')

    fmt = '%Y-%m-%d' if granularity == "day" else '%Y-%m-%d %H:%M'
    labels = df_cur['LocalTimeSpan'].dt.strftime(fmt).drop_duplicates().tolist()

    datasets = []
    colors = ['#1abc9c', '#3498db', '#9b59b6', '#e67e22', '#e74c3c']
    for idx, (sensor, group) in enumerate(df_cur.groupby('sensor_id')):
        group_dict = dict(zip(group['LocalTimeSpan'].dt.strftime(fmt), group['measured_avg_value']))
        data = []
        for label in labels:
            val = group_dict.get(label)
            data.append(float(val) if pd.notnull(val) else None)
        datasets.append({
            "label": f"Fase {idx+1}",
            "data": data,
            "borderColor": colors[idx % len(colors)],
            "fill": False,
            "tension": 0.1
        })

    # --- Process pressure data ---
    pressure_data = None
    if not df_pres.empty:
        df_pres['LocalTimeSpan'] = pd.to_datetime(df_pres['LocalTimeSpan'], errors='coerce')
        df_pres = df_pres.dropna(subset=['LocalTimeSpan']).sort_values('LocalTimeSpan')
        df_pres['date'] = df_pres['LocalTimeSpan'].dt.date
        daily_pres = df_pres.groupby('date')['measured_avg_value'].mean().reset_index()

        p_labels = [str(d) for d in daily_pres['date']]
        p_values = [round(float(v), 2) for v in daily_pres['measured_avg_value']]
        pressure_data = {"labels": p_labels, "values": p_values}

        avg_psi = daily_pres['measured_avg_value'].mean()
        kpis['avg_pressure'] = f"{avg_psi:.1f} PSI"
        kpis['pressure_val'] = round(float(avg_psi), 2)

    return {
        "labels": labels,
        "datasets": datasets,
        "kpis": kpis,
        "pressure_data": pressure_data
    }
