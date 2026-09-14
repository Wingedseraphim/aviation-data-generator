"""S3RAPHIM trajectory generator — multi-step flights per ICAO."""

from __future__ import annotations
import json, random
from datetime import datetime, timedelta, timezone

OUTPUT_FILE = "s3raphim_adsb_data.json"
AIRLINES = ["BA","AA","DL","UA","EK","QR","LH","AF","KL","SQ"]

def _icao(): return "".join(random.choices("0123456789abcdef", k=6))
def _callsign(): return f"{random.choice(AIRLINES)}{random.randint(100,999)}"
def _clamp(v, lo, hi): return max(lo, min(hi, v))

def generate_flight(flight_id, n_steps, inject_anomaly):
    icao, callsign = _icao(), _callsign()
    t0 = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 120))
    lat, lon = random.uniform(6.4, 6.7), random.uniform(3.3, 3.5)
    heading, alt, spd, vs, on_ground = random.uniform(0,360), 20.0, 0.0, 0.0, True
    anomaly_at = random.randint(15, n_steps-10) if inject_anomaly else None
    anomaly_type = random.choice(["impossible_altitude","extreme_vs","speed_spike","ground_flag_airborne"]) if inject_anomaly else None
    records = []
    for step in range(n_steps):
        if step < 5:
            on_ground, spd, alt, vs = True, _clamp(spd+random.uniform(1,4),0,30), random.uniform(15,40), 0
        elif step < 9:
            on_ground = step < 7
            spd = _clamp(spd+random.uniform(8,18),30,180)
            vs = random.uniform(800,1800) if not on_ground else random.uniform(0,200)
            alt = _clamp(alt+vs/60*2,20,3000)
        elif step < 21:
            on_ground, spd = False, _clamp(spd+random.uniform(-2,6),180,320)
            vs = random.uniform(1000,2500); alt = _clamp(alt+vs/60*2,1000,37000)
        elif step < 36:
            on_ground, spd = False, _clamp(spd+random.uniform(-3,3),400,490)
            vs = random.uniform(-150,150); alt = _clamp(alt+vs/60*2,33000,39000)
        elif step < 49:
            on_ground, spd = False, _clamp(spd+random.uniform(-8,2),250,420)
            vs = random.uniform(-2500,-800); alt = _clamp(alt+vs/60*2,3000,38000)
        elif step < 55:
            on_ground, spd = False, _clamp(spd+random.uniform(-10,2),140,220)
            vs = random.uniform(-1200,-400); alt = _clamp(alt+vs/60*2,500,5000)
        else:
            spd = _clamp(spd-random.uniform(5,15),0,160)
            vs = random.uniform(-400,-50) if alt > 50 else 0
            alt = _clamp(alt+vs/60*2,0,800)
            on_ground = alt < 50
            if on_ground: vs, spd = 0, _clamp(spd-3,0,40)
        heading = (heading+random.uniform(-3,3))%360
        lat += random.uniform(-0.01,0.02); lon += random.uniform(-0.01,0.02)
        is_anomaly = False
        if anomaly_at is not None and anomaly_at <= step <= anomaly_at+2:
            is_anomaly = True
            if anomaly_type=="impossible_altitude": alt = random.choice([65000,-200,72000])
            elif anomaly_type=="extreme_vs": vs = random.choice([9000,-9500,11000])
            elif anomaly_type=="speed_spike": spd = random.choice([650,720,-10])
            elif anomaly_type=="ground_flag_airborne":
                on_ground = True
                if alt < 1000: alt = random.uniform(5000,20000)
        ts = t0 + timedelta(seconds=step*2)
        records.append({
            "icao24":icao,"callsign":callsign,"flight_id":flight_id,
            "altitude":round(alt,1),"velocity":round(spd,1),"heading":round(heading,1),
            "latitude":round(lat,4),"longitude":round(lon,4),"on_ground":on_ground,
            "vertical_rate":round(vs,1),"timestamp":ts.isoformat().replace("+00:00","Z"),
            "anomaly":is_anomaly,
        })
    return records

def generate_trajectories(n_flights=40, n_steps=60, anomaly_rate=0.15):
    data, anomaly_flights = [], 0
    for fid in range(n_flights):
        inject = random.random() < anomaly_rate
        if inject: anomaly_flights += 1
        data.extend(generate_flight(fid, n_steps, inject))
    return data, anomaly_flights

if __name__ == "__main__":
    print("="*55 + "\n   S3RAPHIM TRAJECTORY GENERATOR\n" + "="*55)
    try:
        n = int(input("How many flights? [40] → ") or 40)
        steps = int(input("Steps per flight? [60] → ") or 60)
    except ValueError:
        n, steps = 40, 60
    data, af = generate_trajectories(n, steps)
    with open(OUTPUT_FILE,"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
    print(f"Flights={n} steps={steps} records={len(data):,} anomaly_flights={af}")
    print(f"Saved → {OUTPUT_FILE}")