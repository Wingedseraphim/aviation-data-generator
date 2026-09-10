"""
S3RAPHIM ADS-B Clean Data Generator (NO anomalies)
Creates only realistic, valid flight records. Useful as a baseline
dataset, for demos, or to confirm the detector reports zero false
positives on clean data.

Run standalone:
    python s3raphim_generator_clean.py

Or import generate_clean_dataset() from another script.
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


def generate_clean_dataset(num_records):
    return [create_normal_record() for _ in range(num_records)]


def _prompt_for_count():
    while True:
        try:
            num_records = int(input("\nHow many clean records do you want to generate? → "))
            if num_records <= 0:
                print("Please enter a number greater than 0.")
                continue
            return num_records
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    print("=" * 55)
    print("     S3RAPHIM CLEAN DATA GENERATOR (No Anomalies)")
    print("=" * 55)

    num_records = _prompt_for_count()
    data = generate_clean_dataset(num_records)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nSuccessfully generated {num_records:,} clean records.")
    print(f"Data saved to → {DATA_FILE}")