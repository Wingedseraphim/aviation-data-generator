```markdown
# Aviation Data Generator

Simulated ADS-B flight data generator built for the **S3RAPHIM** aviation project.

This tool creates realistic aircraft position and flight parameter records that can be used for learning, testing, and developing aviation-related software.

## Features

- Interactive command-line interface
- Generate any number of simulated ADS-B records
- Realistic flight parameters:
  - ICAO24 address
  - Callsign
  - Altitude
  - Velocity
  - Heading
  - Latitude & Longitude
  - Vertical rate
  - On-ground status
  - Timestamp
- Option to save generated data as a JSON file
- Warning system for large data generation

## How to Run

```bash
python s3raphim_adsb_generator.py
```

The program will ask you:
1. How many records you want to generate
2. Whether you want to save the data as a JSON file

## Example

```
=======================================================
          S3RAPHIM ADS-B DATA GENERATOR
=======================================================

How many ADS-B records do you want to generate? → 1000

Generating 1,000 simulated ADS-B records...
Generation complete.

Total records created: 1,000

Do you want to save the data to a JSON file? (y/n): y
Data successfully saved to → s3raphim_adsb_data.json
```

## Requirements

- Python 3.7+
- No external libraries required (uses only built-in modules)

## Project Status

Current version supports:
- Custom number of records
- JSON export
- Basic realistic aviation values

## Future Improvements

- Better file naming
- Data statistics summary
- Ability to load existing datasets
- Filtering tools (e.g. high altitude aircraft)
- More realistic geographic and flight patterns

---

**Part of the S3RAPHIM Aviation Systems project**
```
