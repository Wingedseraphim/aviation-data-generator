"""
S3RAPHIM ADS-B Data Generator (WITH anomalies)
Creates realistic flight records and injects a small % of anomalies
(impossible altitude/speed, contradictory ground state, etc).

Run standalone:
    python s3raphim_generator_anomalies.py

Or import generate_dataset() from another script.
"""

import random
import json
from datetime import datetime, timezone

DATA_FILE = "s3raphim_adsb_data.json"


def create_normal_record():
    on_ground = random.choice([True, False])

    if on_ground:
        altitude = random.randint(0, 50)
        velocity = random.randint(0, 30)
        vertical_rate = 0
    else:
        altitude = random.randint(5000, 42000)
        velocity = random.randint(250, 520)
        vertical_rate = random.randint(-2000, 2000)

    return {
        "icao24": ''.join(random.choices("0123456789abcdef", k=6)),
        "callsign": f"{random.choice(['BA', 'AA', 'DL', 'UA', 'EK', 'QR', 'LH', 'AF', 'KL', 'SQ'])}{random.randint(100, 999)}",
        "altitude": altitude,
        "velocity": velocity,
        "heading": random.randint(0, 359),
        "latitude": round(random.uniform(4.0, 13.5), 4),
        "longitude": round(random.uniform(2.5, 14.5), 4),
        "on_ground": on_ground,
        "vertical_rate": vertical_rate,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "anomaly": False
    }


def create_anomalous_record():
    record = create_normal_record()
    anomaly_type = random.choice([
        "impossible_altitude",
        "impossible_speed",
        "ground_high_alt",
        "extreme_vertical",
        "missing_callsign"
    ])

    if anomaly_type == "impossible_altitude":
        record["altitude"] = random.choice([65000, -500, 72000])
    elif anomaly_type == "impossible_speed":
        record["velocity"] = random.choice([650, -20, 800])
    elif anomaly_type == "ground_high_alt":
        record["on_ground"] = True
        record["altitude"] = random.randint(5000, 35000)
    elif anomaly_type == "extreme_vertical":
        record["vertical_rate"] = random.choice([9000, -9500, 11000])
    elif anomaly_type == "missing_callsign":
        record["callsign"] = None

    record["anomaly"] = True
    return record


def generate_dataset(num_records, anomaly_rate=0.05):
    data = []
    anomaly_count = 0

    for _ in range(num_records):
        if random.random() < anomaly_rate:
            data.append(create_anomalous_record())
            anomaly_count += 1
        else:
            data.append(create_normal_record())

    return data, anomaly_count


def _prompt_for_count():
    while True:
        try:
            num_records = int(input("\nHow many records do you want to generate? → "))
            if num_records <= 0:
                print("Please enter a number greater than 0.")
                continue
            return num_records
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    print("=" * 55)
    print("       S3RAPHIM ADS-B GENERATOR (with Anomalies)")
    print("=" * 55)

    num_records = _prompt_for_count()
    data, injected = generate_dataset(num_records, anomaly_rate=0.05)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nSuccessfully generated {num_records:,} records.")
    print(f"Anomalies injected: {injected:,}")
    print(f"Data saved to → {DATA_FILE}")