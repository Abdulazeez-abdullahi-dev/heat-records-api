"""Replaces the /summary function in main.py with the latest version.

Run it once from the project folder:   python update_summary.py
A backup of your file is saved as main.py.bak first.
"""
import re
import shutil

NEW_FUNCTION = r"""@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Heat.grade,
            func.count(Heat.id),
            func.sum(Heat.tap_weight_t),
            func.avg(Heat.tap_temp),
            func.avg(Heat.tap_weight_t),
            func.avg(Heat.power_kwh),
            func.avg(Heat.carbon_kg),
            func.avg(Heat.oxygen_nm3),
            func.avg(Heat.lime_kg),
            func.avg(Heat.electrode_kg),
        )
        .group_by(Heat.grade)
        .all()
    )

    # Per tonne = total used / total tonnes, counting only heats that have both values
    per_tonne_columns = {
        "power_kwh_per_t": Heat.power_kwh,
        "carbon_kg_per_t": Heat.carbon_kg,
        "oxygen_nm3_per_t": Heat.oxygen_nm3,
        "lime_kg_per_t": Heat.lime_kg,
        "electrode_kg_per_t": Heat.electrode_kg,
    }
    per_tonne = {}
    for key, column in per_tonne_columns.items():
        pairs = (
            db.query(Heat.grade, func.sum(column), func.sum(Heat.tap_weight_t))
            .filter(column.isnot(None), Heat.tap_weight_t.isnot(None), Heat.tap_weight_t > 0)
            .group_by(Heat.grade)
            .all()
        )
        per_tonne[key] = {g: used / tonnes for g, used, tonnes in pairs}

    # Heat duration and productivity, from the start and end times
    timed = (
        db.query(Heat.grade, Heat.start_time, Heat.end_time, Heat.tap_weight_t)
        .filter(Heat.start_time.isnot(None), Heat.end_time.isnot(None))
        .all()
    )
    minutes_by_grade = {}
    tonnes_and_minutes = {}
    for g, start, end, size in timed:
        minutes = (end - start).total_seconds() / 60
        if minutes <= 0:
            continue
        minutes_by_grade.setdefault(g, []).append(minutes)
        if size is not None and size > 0:
            pair = tonnes_and_minutes.setdefault(g, [0.0, 0.0])
            pair[0] += size
            pair[1] += minutes

    def rnd(value, digits=1):
        return round(value, digits) if value is not None else None

    result = []
    for g, n, total, t, w, p, c, o, l, e in rows:
        minutes = minutes_by_grade.get(g)
        pair = tonnes_and_minutes.get(g)
        entry = {
            "grade": g,
            "heats": n,
            "total_heat_size_t": rnd(total),
            "avg_tap_temp": rnd(t),
            "avg_heat_size_t": rnd(w),
            "avg_power_kwh": rnd(p),
            "avg_carbon_kg": rnd(c),
            "avg_oxygen_nm3": rnd(o),
            "avg_lime_kg": rnd(l),
            "avg_electrode_kg": rnd(e),
            "avg_duration_min": rnd(sum(minutes) / len(minutes)) if minutes else None,
            "tonnes_per_hour": rnd(pair[0] / (pair[1] / 60)) if pair else None,
        }
        for key, values in per_tonne.items():
            entry[key] = rnd(values.get(g), 2)
        result.append(entry)
    return result
"""

src = open("main.py", encoding="utf-8").read()

if "tonnes_per_hour" in src:
    print("main.py already has the latest /summary function. Nothing changed.")
    raise SystemExit

if '@app.get("/summary")' not in src:
    print("Could not find @app.get(\"/summary\") in main.py. Nothing changed.")
    raise SystemExit

shutil.copy("main.py", "main.py.bak")

start = src.index('@app.get("/summary")')
def_end = src.index("\n", src.index("def summary", start))
# the old function ends at the next line that starts at the left edge, or at the end of the file
m = re.search(r"\n(?=\S)", src[def_end:])
end = def_end + m.start() + 1 if m else len(src)

tail = src[end:]
if tail.strip():
    new_src = src[:start] + NEW_FUNCTION + "\n\n" + tail
else:
    new_src = src[:start] + NEW_FUNCTION

open("main.py", "w", encoding="utf-8").write(new_src)
print("Done. /summary replaced. Your old file is saved as main.py.bak")
