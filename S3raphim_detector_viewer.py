"""
S3RAPHIM ADS-B Anomaly Detector + Data Viewer
Version 2.1

Reads whichever dataset was last generated (by either generator) and
lets you browse records or scan for anomalies.

Run standalone:
    python s3raphim_detector_viewer.py
"""

import json

DATA_FILE = "s3raphim_adsb_data.json"


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


def display_records(data, start, end):
    print(f"\nShowing records {start} to {end - 1}:")
    print("-" * 60)
    for i, record in enumerate(data[start:end], start=start):
        print(f"[{i}] {record}")
    print("-" * 60)


def viewer_menu(data):
    while True:
        print("\n" + "=" * 55)
        print("           DATA VIEWER MENU")
        print("=" * 55)
        print("1. View first 10 records")
        print("2. View first 100 records")
        print("3. View first 500 records")
        print("4. View custom range")
        print("5. Run anomaly detection")
        print("6. Back / Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            display_records(data, 0, min(10, len(data)))
        elif choice == "2":
            display_records(data, 0, min(100, len(data)))
        elif choice == "3":
            display_records(data, 0, min(500, len(data)))
        elif choice == "4":
            try:
                start = int(input("Start index: "))
                end = int(input("End index: "))
                if start < 0 or end > len(data) or start >= end:
                    print("Invalid range.")
                else:
                    display_records(data, start, end)
            except ValueError:
                print("Please enter valid numbers.")
        elif choice == "5":
            detected = detect_anomalies(data)
            print(f"\nAnomalies detected: {len(detected):,}")
            if detected:
                print("\n--- First 5 detected anomalies ---")
                for item in detected[:5]:
                    print(f"\nIndex: {item['index']}")
                    print(f"Reason: {item['reason']}")
                    print(f"Record: {item['record']}")
            else:
                print("No anomalies found.")
        elif choice == "6":
            print("\nReturning...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    print("=" * 55)
    print("     S3RAPHIM ADS-B DETECTOR + VIEWER (v2.1)")
    print("=" * 55)

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        print(f"\nLoaded {len(data):,} records from {DATA_FILE}")
    except FileNotFoundError:
        print(f"\nFile '{DATA_FILE}' not found. Please run a generator first.")
        raise SystemExit(0)

    viewer_menu(data)