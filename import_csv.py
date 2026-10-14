"""Load heats from a CSV: python import_csv.py sample_heats.csv"""
import csv
import sys
from datetime import datetime

from main import Heat, SessionLocal


def num(v):
    return float(v) if v not in (None, "") else None


def dt(v):
    return datetime.fromisoformat(v) if v else None


db = SessionLocal()
added = skipped = 0
with open(sys.argv[1], newline="") as f:
    for row in csv.DictReader(f):
        if db.query(Heat).filter_by(heat_no=row["heat_no"]).first():
            skipped += 1
            continue
        db.add(Heat(
            heat_no=row["heat_no"], furnace=row["furnace"], grade=row["grade"],
            shift=row["shift"], start_time=dt(row["start_time"]),
            end_time=dt(row["end_time"]), tap_temp=num(row["tap_temp"]),
            power_kwh=num(row["power_kwh"]), electrode_kg=num(row["electrode_kg"]),
        ))
        added += 1
db.commit()
print(f"added {added}, skipped {skipped} duplicates")
