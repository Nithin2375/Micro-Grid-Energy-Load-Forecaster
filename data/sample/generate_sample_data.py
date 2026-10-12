import os
import math
import random
from datetime import datetime, timedelta

def generate_sample_data():
    start_date = datetime(2026, 1, 1, 0, 0, 0)
    hours = 24 * 60  # 60 days of hourly data
    
    rows = ["timestamp,load_kW,solar_generation_kW,wind_generation_kW,battery_soc,grid_import_kW"]
    
    random.seed(42)
    
    for i in range(hours):
        dt = start_date + timedelta(hours=i)
        hour = dt.hour
        day_of_week = dt.weekday()
        
        # Base daily load profile (kW)
        # Night baseline ~120-150 kW, Morning peak ~320-380 kW, Evening peak ~400-480 kW
        morning_peak = math.exp(-((hour - 9) ** 2) / 8.0) * 180
        evening_peak = math.exp(-((hour - 19) ** 2) / 10.0) * 250
        night_base = 130 + math.sin(hour / 24.0 * math.pi) * 20
        weekend_factor = 0.85 if day_of_week >= 5 else 1.0
        
        noise = random.gauss(0, 15)
        load_kw = max(50.0, (night_base + morning_peak + evening_peak) * weekend_factor + noise)
        
        # Solar generation (kW) - max ~ 250 kW
        if 6 <= hour <= 18:
            solar_peak = math.sin((hour - 6) / 12.0 * math.pi) * 240
            cloud_cover = random.uniform(0.7, 1.0) if random.random() > 0.2 else random.uniform(0.2, 0.6)
            solar_kw = max(0.0, solar_peak * cloud_cover + random.gauss(0, 5))
        else:
            solar_kw = 0.0
            
        # Wind generation (kW) - max ~ 180 kW
        wind_base = 60 + 40 * math.sin(i / 18.0) + 30 * math.cos(i / 7.0)
        wind_kw = max(0.0, wind_base + random.gauss(0, 12))
        
        # Net balance
        net = load_kw - (solar_kw + wind_kw)
        
        # Battery SOC %
        battery_soc = max(20.0, min(95.0, 60.0 - (net / 10.0) + random.gauss(0, 3)))
        
        # Grid import kW
        grid_import_kw = max(0.0, net)
        
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        rows.append(f"{timestamp_str},{load_kw:.2f},{solar_kw:.2f},{wind_kw:.2f},{battery_soc:.1f},{grid_import_kw:.2f}")
        
    out_dir = r"C:\Users\nithi\.gemini\antigravity-ide\scratch\microgrid_load_forecaster\data\sample"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "microgrid_sample_hourly.csv")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    print(f"Generated sample dataset with {len(rows)-1} records at {out_file}")

if __name__ == "__main__":
    generate_sample_data()
