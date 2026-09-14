"""S3RAPHIM full launcher."""
import json, os, subprocess, sys

DATA_FILE="s3raphim_adsb_data.json"

def run(script):
    if not os.path.exists(script):
        print(f"Missing {script}"); return False
    return subprocess.run([sys.executable, script]).returncode==0

def gen_anom():
    from v1.s3raphim_generator_anomalies import generate_dataset
    n=int(input("How many records? → "))
    data, inj=generate_dataset(n,0.05)
    json.dump(data, open(DATA_FILE,"w"), indent=2)
    print(f"Saved {n:,} records ({inj} anomalies)")

def gen_clean():
    from v1.s3raphim_generator_clean import generate_clean_dataset
    n=int(input("How many clean records? → "))
    json.dump(generate_clean_dataset(n), open(DATA_FILE,"w"), indent=2)
    print(f"Saved {n:,} clean records")

def view():
    if not os.path.exists(DATA_FILE):
        print("Generate first"); return
    from v1.s3raphim_detector_viewer import viewer_menu
    data=json.load(open(DATA_FILE))
    print(f"Loaded {len(data):,}"); viewer_menu(data)

def main():
    print("="*55+"\n         S3RAPHIM TOOLKIT\n"+"="*55)
    while True:
        print("""
1. Generate SNAPSHOT data with anomalies
2. Generate CLEAN snapshot data
3. Generate TRAJECTORY flights (recommended)
4. View / rule-detect saved data
5. Thesis bridge
6. ML pipeline (train/save model)
7. Live monitor (phase + constraints + sweep)
8. Exit""")
        c=input("Choice: ").strip()
        if c=="1": gen_anom()
        elif c=="2": gen_clean()
        elif c=="3": run("s3raphim_generator_trajectories.py")
        elif c=="4": view()
        elif c=="5": run("s3raphim_to_thesis.py")
        elif c=="6":
            if not os.path.exists("adsb_thesis_features.csv"):
                print("Run option 5 first")
            else: run("s3raphim_ml_pipeline.py")
        elif c=="7": run("s3raphim_live_monitor.py")
        elif c=="8": print("Bye"); break
        else: print("Invalid")

if __name__=="__main__": main()