# S3RAPHIM ADS-B Toolkit

Simulated ADS-B flight data generator + anomaly detector, for learning,
testing, and anomaly-detection practice. Pure Python standard library —
**no installs, no dependencies, no API keys.**

## Requirements

- Python 3.8+ (nothing else)

## Files

| File | What it does |
|---|---|
| `s3raphim_launcher.py` | **Start here.** One menu that ties everything together. |
| `s3raphim_generator_anomalies.py` | Generates flight records, injecting ~5% intentional anomalies (impossible altitude/speed, contradictory ground state, etc). |
| `s3raphim_generator_clean.py` | Generates only valid, realistic flight records — no anomalies. |
| `s3raphim_detector_viewer.py` | Loads the saved dataset, lets you browse records, and scans for anomalies. |

All three scripts read/write the same file, `s3raphim_adsb_data.json`,
so whichever generator you run last is what the detector inspects.

## Quick start

```bash
git clone <this-repo-url>
cd <repo-folder>
python s3raphim_launcher.py
```

Then just follow the menu:

1. Generate data with anomalies (or clean data)
2. View / detect anomalies

That's it — no setup required.

## Running scripts individually

Each script also works standalone if you don't want the menu:

```bash
python s3raphim_generator_anomalies.py   # or s3raphim_generator_clean.py
python s3raphim_detector_viewer.py
```

## Data format

Each record is a JSON object like:

```json
{
    "icao24": "8b2a26",
    "callsign": "AA711",
    "altitude": 35000,
    "velocity": 430,
    "heading": 210,
    "latitude": 9.0765,
    "longitude": 7.3986,
    "on_ground": false,
    "vertical_rate": 500,
    "timestamp": "2026-09-10T14:04:55.133043Z",
    "anomaly": false
}
```