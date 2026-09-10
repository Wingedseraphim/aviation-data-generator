"""
S3RAPHIM Launcher
Single entry point for the whole toolkit — generate data (with or
without anomalies) and inspect/detect anomalies, all from one menu.

Run:
    python s3raphim_launcher.py

Requires s3raphim_generator_anomalies.py, s3raphim_generator_clean.py,
and s3raphim_detector_viewer.py to be in the same folder.
"""

import json
import os

from s3raphim_generator_anomalies import generate_dataset
from s3raphim_generator_clean import generate_clean_dataset
from s3raphim_detector_viewer import viewer_menu

DATA_FILE = "s3raphim_adsb_data.json"


def _prompt_for_count(label="records"):
    while True:
        try:
            n = int(input(f"\nHow many {label} do you want to generate? → "))
            if n <= 0:
                print("Please enter a number greater than 0.")
                continue
            return n
        except ValueError:
            print("Please enter a valid number.")


def run_generator_with_anomalies():
    num_records = _prompt_for_count()
    data, injected = generate_dataset(num_records, anomaly_rate=0.05)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nGenerated {num_records:,} records ({injected:,} anomalies injected).")
    print(f"Saved to → {DATA_FILE}")


def run_generator_clean():
    num_records = _prompt_for_count("clean records")
    data = generate_clean_dataset(num_records)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nGenerated {num_records:,} clean records.")
    print(f"Saved to → {DATA_FILE}")


def run_viewer():
    if not os.path.exists(DATA_FILE):
        print(f"\nNo data file found ('{DATA_FILE}'). Generate data first (option 1 or 2).")
        return
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    print(f"\nLoaded {len(data):,} records from {DATA_FILE}")
    viewer_menu(data)


def main():
    print("=" * 55)
    print("            S3RAPHIM ADS-B TOOLKIT")
    print("=" * 55)

    while True:
        print("\n" + "=" * 55)
        print("                  MAIN MENU")
        print("=" * 55)
        print("1. Generate data WITH anomalies")
        print("2. Generate CLEAN data (no anomalies)")
        print("3. View / detect anomalies in saved data")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            run_generator_with_anomalies()
        elif choice == "2":
            run_generator_clean()
        elif choice == "3":
            run_viewer()
        elif choice == "4":
            print("\nGoodbye.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()