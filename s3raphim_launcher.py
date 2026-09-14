"""
S3RAPHIM Launcher — v1 data + bridge + v2 ML + v3 live sweep
"""

import json
import os
import subprocess
import sys

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


def _run_script(script_name: str) -> bool:
    if not os.path.exists(script_name):
        print(f"Missing file: {script_name}")
        return False
    result = subprocess.run([sys.executable, script_name])
    return result.returncode == 0


def run_generator_with_anomalies():
    num_records = _prompt_for_count()
    data, injected = generate_dataset(num_records, anomaly_rate=0.05)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nGenerated {num_records:,} records ({injected:,} anomalies).")
    print(f"Saved → {DATA_FILE}")


def run_generator_clean():
    num_records = _prompt_for_count("clean records")
    data = generate_clean_dataset(num_records)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nGenerated {num_records:,} clean records.")
    print(f"Saved → {DATA_FILE}")


def run_viewer():
    if not os.path.exists(DATA_FILE):
        print(f"\nNo data file ('{DATA_FILE}'). Generate first (1 or 2).")
        return
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    print(f"\nLoaded {len(data):,} records")
    viewer_menu(data)


def run_bridge_and_qda():
    if not os.path.exists(DATA_FILE):
        print(f"\nNo data file. Generate first (1 or 2).")
        return
    print("\n--- Thesis bridge ---")
    if not _run_script("s3raphim_to_thesis.py"):
        return
    print("\n--- QDA eval ---")
    _run_script("s3raphim_qda_eval.py")


def run_ml_pipeline_v2():
    if not os.path.exists("adsb_thesis_features.csv"):
        print("Missing adsb_thesis_features.csv — run option 4 (bridge) first.")
        return
    print("\n--- S3RAPHIM v2 ML pipeline ---")
    _run_script("s3raphim_ml_pipeline.py")


def run_live_sweep_v3():
    if not os.path.exists(DATA_FILE):
        print(f"\nNo data file. Generate first (1 or 2).")
        return
    print("\n--- S3RAPHIM v3 live sweep ---")
    _run_script("s3raphim_live_sweep.py")


def main():
    print("=" * 55)
    print("            S3RAPHIM ADS-B TOOLKIT")
    print("=" * 55)

    while True:
        print("\n" + "=" * 55)
        print("                  MAIN MENU")
        print("=" * 55)
        print("1. Generate data WITH anomalies")
        print("2. Generate CLEAN data")
        print("3. View / detect anomalies")
        print("4. Thesis bridge + QDA eval")
        print("5. v2 ML pipeline (train + save model)")
        print("6. v3 Live sweep + score")
        print("7. Exit")

        choice = input("\nEnter choice (1-7): ").strip()

        if choice == "1":
            run_generator_with_anomalies()
        elif choice == "2":
            run_generator_clean()
        elif choice == "3":
            run_viewer()
        elif choice == "4":
            run_bridge_and_qda()
        elif choice == "5":
            run_ml_pipeline_v2()
        elif choice == "6":
            run_live_sweep_v3()
        elif choice == "7":
            print("\nGoodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()