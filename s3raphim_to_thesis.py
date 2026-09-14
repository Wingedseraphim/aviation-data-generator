"""Bridge JSON → adsb_thesis_features.csv (thesis altitude-rate rule)."""
import json, csv
from pathlib import Path

DATA_FILE, OUTPUT_CSV, THRESH = "s3raphim_adsb_data.json", "adsb_thesis_features.csv", 100

def safe_float(v, d=0.0):
    try: return d if v is None else float(v)
    except: return d

def main():
    if not Path(DATA_FILE).exists():
        print(f"Missing {DATA_FILE}"); return
    records = json.load(open(DATA_FILE, encoding="utf-8"))
    by = {}
    for i,r in enumerate(records):
        by.setdefault(r.get("icao24") or f"u{i}", []).append((i,r))
    for k in by: by[k].sort(key=lambda p: p[1].get("timestamp") or "")
    rows = [None]*len(records)
    for items in by.values():
        prev=None
        for idx,rec in items:
            alt,vel,hdg = safe_float(rec.get("altitude")), safe_float(rec.get("velocity")), safe_float(rec.get("heading"))
            lat,lon = safe_float(rec.get("latitude")), safe_float(rec.get("longitude"))
            ar = safe_float(rec.get("vertical_rate"), None)
            hc,acc = 0.0,0.0
            if prev:
                pr=prev[1]
                if ar is None: ar = alt-safe_float(pr.get("altitude"))
                hc = hdg-safe_float(pr.get("heading")); acc = vel-safe_float(pr.get("velocity"))
            elif ar is None: ar = 0.0
            rows[idx] = {
                "icao24": rec.get("icao24") or "","callsign": rec.get("callsign") or "",
                "flight_id": rec.get("flight_id",""),
                "altitude":round(alt,4),"velocity":round(vel,4),"heading":round(hdg,4),
                "latitude":round(lat,6),"longitude":round(lon,6),
                "altitude_rate":round(ar,4),"heading_change":round(hc,4),"acceleration":round(acc,4),
                "abnormal": 1 if abs(ar)>THRESH else 0,
                "s3raphim_anomaly_flag": 1 if rec.get("anomaly") else 0,
                "timestamp": rec.get("timestamp") or "",
            }
            prev=(idx,rec)
    rows=[r for r in rows if r]
    fields=list(rows[0].keys())
    with open(OUTPUT_CSV,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    ab=sum(r["abnormal"] for r in rows)
    print(f"Saved {len(rows):,} rows → {OUTPUT_CSV} | abnormal={ab:,}")

if __name__=="__main__": main()