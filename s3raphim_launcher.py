"""
S3RAPHIM Launcher
Single entry point for the toolkit.

Run:
    python s3raphim_launcher.py
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


def run_bridge_and_qda():
    """Run thesis bridge, then QDA evaluation."""
    if not os.path.exists(DATA_FILE):
        print(f"\nNo data file found ('{DATA_FILE}'). Generate data first (option 1 or 2).")
        return

    print("\n--- Step 1/2: Thesis bridge ---")
    bridge = subprocess.run([sys.executable, "s3raphim_to_thesis.py"])
    if bridge.returncode != 0:
        print("Bridge failed. Fix errors above, then try again.")
        return

    if not os.path.exists("adsb_thesis_features.csv"):
        print("Bridge did not create adsb_thesis_features.csv")
        return

    print("\n--- Step 2/2: QDA evaluation ---")
    qda = subprocess.run([sys.executable, "s3raphim_qda_eval.py"])
    if qda.returncode != 0:
        print("QDA evaluation failed. Check that scikit-learn, pandas, matplotlib are installed:")
        print("  pip install scikit-learn pandas matplotlib")
        return

    print("\nBridge + QDA pipeline finished.")


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
        print("4. Run thesis bridge + QDA evaluation")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            run_generator_with_anomalies()
        elif choice == "2":
            run_generator_clean()
        elif choice == "3":
            run_viewer()
        elif choice == "4":
            run_bridge_and_qda()
        elif choice == "5":
            print("\nGoodbye.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()