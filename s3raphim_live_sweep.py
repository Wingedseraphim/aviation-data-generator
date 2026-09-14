"""S3RAPHIM live monitor — sweep + phase + constraints + optional model."""
from __future__ import annotations
import json, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from s3raphim_phases import classify_phase
from s3raphim_constraints import check_constraints

DATA_FILE, MODEL_FILE = "s3raphim_adsb_data.json", "s3raphim_model.joblib"
MAX_AGE, FEATURE_COLS = 30.0, ["altitude","velocity","heading","latitude","longitude","altitude_rate","heading_change","acceleration"]

def parse_timestamp(v: Any):
    if v is None: return None
    if isinstance(v,(int,float)): return float(v)
    t=str(v).strip()
    if not t: return None
    if t.endswith("Z"): t=t[:-1]+"+00:00"
    try:
        dt=datetime.fromisoformat(t)
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except: return None

class FlightSweeper:
    def __init__(self, max_age=MAX_AGE):
        self.max_age=max_age; self.active=set(); self.state={}; self.last_seen={}
    def ingest(self, rec, now=None):
        now = now or time.time()
        icao=str(rec.get("icao24") or "UNKNOWN")
        self.active.add(icao); self.state[icao]=rec
        self.last_seen[icao]=parse_timestamp(rec.get("timestamp")) or now
        return icao
    def sweep(self, now=None):
        now=now or time.time(); removed=[]
        for icao in list(self.active):
            last=self.last_seen.get(icao)
            if last is None or (now-last)>self.max_age:
                self.active.discard(icao); self.state.pop(icao,None); self.last_seen.pop(icao,None); removed.append(icao)
        return removed

def load_model():
    if not Path(MODEL_FILE).exists(): return None
    try:
        import joblib; return joblib.load(MODEL_FILE)["model"]
    except: return None

def score_ml(rec, model):
    if model is None: return None
    try:
        import pandas as pd
        feats={
            "altitude":float(rec.get("altitude") or 0),"velocity":float(rec.get("velocity") or 0),
            "heading":float(rec.get("heading") or 0),"latitude":float(rec.get("latitude") or 0),
            "longitude":float(rec.get("longitude") or 0),"altitude_rate":float(rec.get("vertical_rate") or 0),
            "heading_change":0.0,"acceleration":0.0,
        }
        return int(model.predict(pd.DataFrame([feats])[FEATURE_COLS])[0])
    except: return None

def main():
    print("="*60+"\n  S3RAPHIM LIVE MONITOR\n"+"="*60)
    if not Path(DATA_FILE).exists():
        print(f"Missing {DATA_FILE}"); return
    records=json.load(open(DATA_FILE,encoding="utf-8"))
    model=load_model()
    print("Model:", "loaded" if model else "none (constraints only)")
    sw, total, chunk, hits = FlightSweeper(), min(len(records),5000), 200, 0
    for i in range(0,total,chunk):
        batch=records[i:i+chunk]
        times=[parse_timestamp(r.get("timestamp")) for r in batch]
        times=[t for t in times if t is not None]
        now=max(times) if times else time.time()
        for rec in batch:
            icao=sw.ingest(rec, now=now)
            phase=classify_phase(rec)
            warns=check_constraints(rec, phase)
            ml=score_ml(rec, model)
            if warns or ml==1:
                hits+=1
                print(f"WARNING | {rec.get('callsign') or icao:8} | {phase:8} | ALT={rec.get('altitude')} VS={rec.get('vertical_rate')} | {warns}")
        removed=sw.sweep(now=now)
        print(f"[chunk {i//chunk+1}] active={len(sw.active)} removed={len(removed)} warnings={hits}")
    print("="*60+f"\nDone active={len(sw.active)} warnings={hits}\n"+"="*60)

if __name__=="__main__": main()