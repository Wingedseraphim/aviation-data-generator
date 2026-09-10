"""
S3RAPHIM ADS-B Anomaly Detector
Loads the generated data and detects anomalies.
"""

import json

def is_anomalous(record):
    if record["altitude"] > 60000 or record["altitude"] < -100:
        return True, "Impossible altitude"
    if record["velocity"] > 600 or record["velocity"] < 0:
        return True, "Impossible speed"
    if record["on_ground"] and record["altitude"] > 1000:
        return True, "On ground but high altitude"
    if abs(record.get("vertical_rate", 0)) > 8000:
        return True, "Extreme vertical rate"
    if not record.get("callsign"):
        return True, "Missing callsign"
    return False, None

def detect_anomalies(data):
    detected = []
    for i, record in enumerate(data):
        anomalous, reason = is_anomalous(record)
        if anomalous:
            detected.append({
                "index": i,
                "reason": reason,
                "record": record
            })
    return detected

if __name__ == "__main__":
    print("=" * 55)
    print("       S3RAPHIM ADS-B ANOMALY DETECTOR")
    print("=" * 55)

    filename = "s3raphim_adsb_data.json"

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"\nFile '{filename}' not found. Please run generator.py first.")
        exit()

    print(f"\nLoaded {len(data):,} records from {filename}")

    detected = detect_anomalies(data)

    print(f"\nAnomalies detected: {len(detected):,}")

    if detected:
        print("\n--- Examples of detected anomalies ---")
        for item in detected[:5]:  # show first 5
            print(f"\nIndex: {item['index']}")
            print(f"Reason: {item['reason']}")
            print(f"Record: {item['record']}")
    else:
        print("No anomalies found.")