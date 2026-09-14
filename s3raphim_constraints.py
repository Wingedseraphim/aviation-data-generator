"""S3RAPHIM phase-aware constraint checks."""
from s3raphim_phases import classify_phase

def check_constraints(record: dict, phase: str | None = None) -> list[str]:
    if phase is None: phase = classify_phase(record)
    alt = float(record.get("altitude") or 0)
    spd = float(record.get("velocity") or 0)
    vs = float(record.get("vertical_rate") or 0)
    on_ground = bool(record.get("on_ground", False))
    w = []
    if alt > 60000 or alt < -100: w.append("Impossible altitude")
    if spd > 600 or spd < 0: w.append("Impossible speed")
    if abs(vs) > 8000: w.append("Extreme vertical rate")
    if on_ground and alt > 1000: w.append("On-ground flag with high altitude")
    if not record.get("callsign"): w.append("Missing callsign")
    if phase in ("PARKED","TAXI") and spd > 80: w.append(f"Speed too high for {phase}")
    if phase == "PARKED" and abs(vs) > 50: w.append("Vertical rate while PARKED")
    if phase == "CRUISE" and alt < 10000: w.append("CRUISE but altitude low")
    if phase == "CRUISE" and abs(vs) > 1500: w.append("Strong VS in CRUISE")
    if phase == "CLIMB" and vs < -300: w.append("Descending while CLIMB")
    if phase == "DESCENT" and vs > 300: w.append("Climbing while DESCENT")
    if phase in ("APPROACH","LANDING") and spd > 280: w.append(f"Speed high for {phase}")
    return w