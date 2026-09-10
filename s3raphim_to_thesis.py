# S3RAPHIM → Thesis bridge
import json
import csv
from pathlib import Path

DATA_FILE = "s3raphim_adsb_data.json"
OUTPUT_CSV = "adsb_thesis_features.csv"
ALTITUDE_RATE_THRESHOLD = 100


def load_records(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list of ADS-B records.")
    return data


def safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_features(records: list) -> list:
    by_aircraft = {}
    for i, rec in enumerate(records):
        key = rec.get("icao24") or f"unknown_{i}"
        by_aircraft.setdefault(key, []).append((i, rec))

    for key in by_aircraft:
        by_aircraft[key].sort(key=lambda pair: pair[1].get("timestamp") or "")

    rows = [None] * len(records)

    for key, items in by_aircraft.items():
        prev = None
        for idx, rec in items:
            altitude = safe_float(rec.get("altitude"))
            velocity = safe_float(rec.get("velocity"))
            heading = safe_float(rec.get("heading"))
            latitude = safe_float(rec.get("latitude"))
            longitude = safe_float(rec.get("longitude"))

            altitude_rate = safe_float(rec.get("vertical_rate"), default=None)
            heading_change = 0.0
            acceleration = 0.0

            if prev is not None:
                prev_rec = prev[1]
                prev_alt = safe_float(prev_rec.get("altitude"))
                prev_vel = safe_float(prev_rec.get("velocity"))
                prev_head = safe_float(prev_rec.get("heading"))

                alt_diff = altitude - prev_alt
                vel_diff = velocity - prev_vel
                head_diff = heading - prev_head

                if altitude_rate is None:
                    altitude_rate = alt_diff
                heading_change = head_diff
                acceleration = vel_diff
            else:
                if altitude_rate is None:
                    altitude_rate = 0.0

            abnormal = 1 if abs(altitude_rate) > ALTITUDE_RATE_THRESHOLD else 0

            rows[idx] = {
                "icao24": rec.get("icao24") or "",
                "callsign": rec.get("callsign") or "",
                "altitude": round(altitude, 4),
                "velocity": round(velocity, 4),
                "heading": round(heading, 4),
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "altitude_rate": round(altitude_rate, 4),
                "heading_change": round(heading_change, 4),
                "acceleration": round(acceleration, 4),
                "abnormal": abnormal,
                "s3raphim_anomaly_flag": 1 if rec.get("anomaly") else 0,
                "timestamp": rec.get("timestamp") or "",
            }
            prev = (idx, rec)

    return [r for r in rows if r is not None]


def save_csv(rows: list, path: str) -> None:
    fieldnames = [
        "icao24", "callsign", "altitude", "velocity", "heading",
        "latitude", "longitude", "altitude_rate", "heading_change",
        "acceleration", "abnormal", "s3raphim_anomaly_flag", "timestamp",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows: list) -> None:
    total = len(rows)
    thesis_abnormal = sum(1 for r in rows if r["abnormal"] == 1)
    thesis_normal = total - thesis_abnormal
    s3_flags = sum(1 for r in rows if r["s3raphim_anomaly_flag"] == 1)
    both = sum(1 for r in rows if r["abnormal"] == 1 and r["s3raphim_anomaly_flag"] == 1)

    print("=" * 55)
    print("   S3RAPHIM → THESIS BRIDGE COMPLETE")
    print("=" * 55)
    print(f"Total records processed : {total:,}")
    print(f"Thesis NORMAL           : {thesis_normal:,}")
    print(f"Thesis ABNORMAL         : {thesis_abnormal:,}")
    print(f"  (rule: |altitude_rate| > {ALTITUDE_RATE_THRESHOLD})")
    print(f"S3RAPHIM anomaly flags  : {s3_flags:,}")
    print(f"Overlap (both systems)  : {both:,}")
    print(f"\nSaved → {OUTPUT_CSV}")
    print("=" * 55)


def main():
    if not Path(DATA_FILE).exists():
        print(f"File not found: {DATA_FILE}")
        print("Run a S3RAPHIM generator first, then try again.")
        return

    print(f"Loading {DATA_FILE} ...")
    records = load_records(DATA_FILE)
    print(f"Loaded {len(records):,} records.")

    print("Computing thesis features and labels ...")
    rows = compute_features(records)
    save_csv(rows, OUTPUT_CSV)
    print_summary(rows)


if __name__ == "__main__":
    main()