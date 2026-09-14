"""
S3RAPHIM v3 — Live sweeper + monitor

- active set of ICAO24
- state dict per aircraft
- sweep timer drops stale tracks
- scores only active aircraft (rule baseline, or saved v2 model if present)

Usage:
    python s3raphim_live_sweep.py
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_FILE = "s3raphim_adsb_data.json"
MODEL_FILE = "s3raphim_model.joblib"
MAX_AGE_SECONDS = 30.0
SWEEP_INTERVAL = 5.0
FEATURE_COLS = [
    "altitude", "velocity", "heading", "latitude", "longitude",
    "altitude_rate", "heading_change", "acceleration",
]
ALTITUDE_RATE_THRESHOLD = 100


def parse_timestamp(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None


class FlightSweeper:
    def __init__(self, max_age_seconds: float = MAX_AGE_SECONDS):
        self.max_age_seconds = max_age_seconds
        self.active: set[str] = set()
        self.state: dict[str, dict] = {}
        self.last_seen: dict[str, float] = {}

    def ingest(self, record: dict, now: float | None = None) -> str:
        if now is None:
            now = time.time()
        icao = str(record.get("icao24") or "UNKNOWN")
        ts = parse_timestamp(record.get("timestamp"))
        if ts is None:
            ts = now
        self.active.add(icao)
        self.state[icao] = record
        self.last_seen[icao] = ts
        return icao

    def sweep(self, now: float | None = None) -> list[str]:
        if now is None:
            now = time.time()
        removed = []
        for icao in list(self.active):
            last = self.last_seen.get(icao)
            if last is None or (now - last) > self.max_age_seconds:
                self.active.discard(icao)
                self.state.pop(icao, None)
                self.last_seen.pop(icao, None)
                removed.append(icao)
        return removed


def record_to_features(rec: dict) -> dict:
    """Map S3RAPHIM record → feature dict for scoring."""
    alt_rate = rec.get("vertical_rate")
    if alt_rate is None:
        alt_rate = 0.0
    return {
        "altitude": float(rec.get("altitude") or 0),
        "velocity": float(rec.get("velocity") or 0),
        "heading": float(rec.get("heading") or 0),
        "latitude": float(rec.get("latitude") or 0),
        "longitude": float(rec.get("longitude") or 0),
        "altitude_rate": float(alt_rate),
        "heading_change": 0.0,
        "acceleration": 0.0,
    }


def load_model():
    path = Path(MODEL_FILE)
    if not path.exists():
        return None, None
    try:
        import joblib
        bundle = joblib.load(path)
        return bundle["model"], bundle.get("meta", {})
    except Exception as e:
        print(f"Could not load model: {e}")
        return None, None


def score_record(rec: dict, model=None) -> tuple[int, str]:
    """
    Returns (label, source)
    label: 0 normal, 1 abnormal
    """
    feats = record_to_features(rec)

    # Always available rule baseline
    rule_flag = 1 if abs(feats["altitude_rate"]) > ALTITUDE_RATE_THRESHOLD else 0

    if model is None:
        return rule_flag, "rule"

    try:
        import pandas as pd
        row = pd.DataFrame([feats])[FEATURE_COLS]
        pred = int(model.predict(row)[0])
        return pred, "model"
    except Exception:
        return rule_flag, "rule_fallback"


def status_line(icao: str, rec: dict, label: int, source: str) -> str:
    alt = rec.get("altitude")
    spd = rec.get("velocity")
    vs = rec.get("vertical_rate")
    flag = "WARNING " if label == 1 else "NORMAL  "
    return (
        f"{flag} | {icao:8} | alt={alt} spd={spd} vs={vs} | via={source}"
    )


def main():
    print("=" * 60)
    print("        S3RAPHIM v3 — LIVE SWEEP + SCORE")
    print("=" * 60)

    data_path = Path(DATA_FILE)
    if not data_path.exists():
        print(f"Missing {DATA_FILE}. Generate data first.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    model, meta = load_model()
    if model is not None:
        print(f"Loaded model: {meta.get('model_name', '?')} from {MODEL_FILE}")
    else:
        print("No saved model — using rule baseline only")

    sweeper = FlightSweeper(max_age_seconds=MAX_AGE_SECONDS)

    # Simulate a stream: feed records in chunks, sweep between chunks
    chunk_size = 200
    total = min(len(records), 3000)

    print(f"\nStreaming {total:,} records (chunk={chunk_size})...")
    print(f"Sweep every chunk | max_age={MAX_AGE_SECONDS}s\n")

    warnings = 0
    for i in range(0, total, chunk_size):
        chunk = records[i : i + chunk_size]
        times = [parse_timestamp(r.get("timestamp")) for r in chunk]
        times = [t for t in times if t is not None]
        now = max(times) if times else time.time()

        for rec in chunk:
            icao = sweeper.ingest(rec, now=now)
            label, source = score_record(rec, model=model)
            if label == 1:
                warnings += 1
                # print only warnings to keep output light
                print(status_line(icao, rec, label, source))

        removed = sweeper.sweep(now=now)
        print(
            f"[chunk {i//chunk_size + 1}] "
            f"active={len(sweeper.active)} removed={len(removed)} "
            f"warnings_so_far={warnings}"
        )

    print("\n" + "=" * 60)
    print(f"Done. Final active aircraft: {len(sweeper.active)}")
    print(f"Warning hits (row-level): {warnings}")
    print("=" * 60)


if __name__ == "__main__":
    main()