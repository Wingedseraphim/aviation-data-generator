"""S3RAPHIM flight phase classification."""

def classify_phase(record: dict) -> str:
    alt = float(record.get("altitude") or 0)
    spd = float(record.get("velocity") or 0)
    vs = float(record.get("vertical_rate") or 0)
    on_ground = bool(record.get("on_ground", False))
    if on_ground or alt < 50:
        if spd < 5: return "PARKED"
        if spd < 40: return "TAXI"
        return "TAKEOFF" if vs >= 0 else "LANDING"
    if alt < 3000 and vs < -500: return "APPROACH"
    if alt < 2000 and spd < 180 and vs <= 0: return "LANDING" if alt < 800 else "APPROACH"
    if vs > 500 and alt < 30000: return "CLIMB"
    if vs < -500 and alt > 3000: return "DESCENT"
    if abs(vs) <= 500 and alt >= 25000: return "CRUISE"
    if abs(vs) <= 500 and 3000 <= alt < 25000: return "CRUISE"
    if vs > 200: return "CLIMB"
    if vs < -200: return "DESCENT"
    return "UNKNOWN"