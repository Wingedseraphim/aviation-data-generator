"""
S3RAPHIM ADS-B Flight Data Generator
Interactive version – user chooses how many records to generate.
"""

import random
from datetime import datetime

def create_realistic_adsb_record():
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
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def generate_adsb_data(num_records):
    print(f"\nGenerating {num_records:,} simulated ADS-B records...")
    data = [create_realistic_adsb_record() for _ in range(num_records)]
    print("Generation complete.")
    return data

if __name__ == "__main__":
    print("=" * 50)
    print("       S3RAPHIM ADS-B DATA GENERATOR")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nHow many ADS-B records do you want to generate? → ")
            num_records = int(user_input)

            if num_records <= 0:
                print("Please enter a number greater than 0.")
                continue

            # Warning for large numbers
            if num_records >= 50000:
                confirm = input(f"\n⚠️  {num_records:,} is a large number and may use a lot of memory.\nDo you want to continue? (y/n): ").lower()
                if confirm != "y":
                    print("Cancelled. Try a smaller number.")
                    continue

            break

        except ValueError:
            print("Please enter a valid number.")

    # Generate the data
    adsb_data = generate_adsb_data(num_records)

    # Show results
    print(f"\nTotal records created: {len(adsb_data):,}")
    print("\n--- Sample Record (first) ---")
    print(adsb_data[0])

    print("\n--- Sample Record (middle) ---")
    print(adsb_data[len(adsb_data)//2])

    print("\n--- Sample Record (last) ---")
    print(adsb_data[-1])

    print("\nS3RAPHIM data generation finished successfully.")