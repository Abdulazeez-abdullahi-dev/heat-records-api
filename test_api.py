import csv
import io

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import main


def heat(no="H1", **extra):
    """A valid heat. Pass extra fields to add or change values."""
    body = {
        "heat_no": no,
        "furnace": "EAF",
        "grade": "SAE1018",
        "start_time": "2026-10-01T06:00:00",
        "tap_temp": 1640,
    }
    body.update(extra)
    return body


# ---------- API key ----------

def test_page_is_open_but_data_needs_a_key(raw):
    assert raw.get("/").status_code == 200
    assert raw.get("/heats").status_code == 401
    assert raw.get("/heats", headers={"X-API-Key": "wrong"}).status_code == 401
    assert raw.get("/summary").status_code == 401
    assert raw.get("/export.csv").status_code == 401


def test_right_key_is_accepted(client):
    assert client.get("/heats").status_code == 200


def test_home_page_has_the_key_box(raw):
    assert "API key" in raw.get("/").text


# ---------- creating and reading heats ----------

def test_create_and_read_back(client):
    r = client.post("/heats", json=heat("H1", tap_weight_t=120))
    assert r.status_code == 201
    got = client.get("/heats/H1").json()
    assert got["heat_no"] == "H1"
    assert got["tap_weight_t"] == 120
    assert got["events"] == []


def test_duplicate_heat_number_is_rejected(client):
    assert client.post("/heats", json=heat("H1")).status_code == 201
    assert client.post("/heats", json=heat("H1")).status_code == 409


@pytest.mark.parametrize("temp", [1399, 1801])
def test_tap_temp_outside_limits_is_rejected(client, temp):
    assert client.post("/heats", json=heat("H1", tap_temp=temp)).status_code == 422


def test_unknown_furnace_is_rejected(client):
    assert client.post("/heats", json=heat("H1", furnace="XYZ")).status_code == 422


def test_missing_heat_is_404(client):
    assert client.get("/heats/H404").status_code == 404


def test_filters(client):
    client.post("/heats", json=heat("H1"))
    client.post("/heats", json=heat("H2", furnace="LRF", grade="B500B"))
    assert len(client.get("/heats").json()) == 2
    by_furnace = client.get("/heats", params={"furnace": "LRF"}).json()
    assert [h["heat_no"] for h in by_furnace] == ["H2"]
    by_grade = client.get("/heats", params={"grade": "SAE1018"}).json()
    assert [h["heat_no"] for h in by_grade] == ["H1"]


# ---------- updating ----------

def test_patch_changes_only_the_fields_sent(client):
    client.post("/heats", json=heat("H1", shift="A"))
    r = client.patch("/heats/H1", json={"tap_temp": 1650})
    assert r.status_code == 200
    got = r.json()
    assert got["tap_temp"] == 1650
    assert got["shift"] == "A"
    assert got["grade"] == "SAE1018"


def test_patch_with_null_clears_a_value(client):
    client.post("/heats", json=heat("H1", shift="A"))
    r = client.patch("/heats/H1", json={"shift": None})
    assert r.status_code == 200
    assert r.json()["shift"] is None


def test_patch_is_validated(client):
    client.post("/heats", json=heat("H1"))
    assert client.patch("/heats/H1", json={"tap_temp": 2000}).status_code == 422


def test_patch_missing_heat_is_404(client):
    assert client.patch("/heats/H404", json={"tap_temp": 1640}).status_code == 404


# ---------- events ----------

def test_event_attaches_to_the_heat(client):
    client.post("/heats", json=heat("H1"))
    body = {"timestamp": "2026-10-01T06:30:00", "kind": "temperature", "temperature": 1620}
    assert client.post("/heats/H1/events", json=body).status_code == 201
    events = client.get("/heats/H1").json()["events"]
    assert len(events) == 1
    assert events[0]["temperature"] == 1620


def test_event_is_validated(client):
    client.post("/heats", json=heat("H1"))
    cold = {"timestamp": "2026-10-01T06:30:00", "kind": "temperature", "temperature": 900}
    assert client.post("/heats/H1/events", json=cold).status_code == 422
    odd = {"timestamp": "2026-10-01T06:30:00", "kind": "banana"}
    assert client.post("/heats/H1/events", json=odd).status_code == 422
    ok = {"timestamp": "2026-10-01T06:30:00", "kind": "temperature", "temperature": 1620}
    assert client.post("/heats/H404/events", json=ok).status_code == 404


# ---------- deleting ----------

def test_delete_removes_the_heat(client):
    client.post("/heats", json=heat("H1"))
    event = {"timestamp": "2026-10-01T06:30:00", "kind": "temperature", "temperature": 1620}
    client.post("/heats/H1/events", json=event)
    assert client.delete("/heats/H1").status_code == 204
    assert client.get("/heats/H1").status_code == 404
    assert client.get("/heats").json() == []


# ---------- summary ----------

def three_heats_of_120_t(client):
    rows = [
        ("H1", 40000, 1200, 300, 900, 1640),
        ("H2", 41000, 1300, 320, 1000, 1630),
        ("H3", 39000, 1100, 280, 800, 1650),
    ]
    for no, power, oxygen, carbon, lime, temp in rows:
        body = heat(no, tap_weight_t=120, power_kwh=power, oxygen_nm3=oxygen,
                    carbon_kg=carbon, lime_kg=lime, tap_temp=temp)
        assert client.post("/heats", json=body).status_code == 201


def entry_for(client, grade):
    data = client.get("/summary").json()
    return next(e for e in data if e["grade"] == grade)


def test_summary_totals_and_per_tonne(client):
    three_heats_of_120_t(client)
    s = entry_for(client, "SAE1018")
    assert s["heats"] == 3
    assert s["total_heat_size_t"] == pytest.approx(360)
    assert s["avg_tap_temp"] == pytest.approx(1640)
    assert s["avg_heat_size_t"] == pytest.approx(120)
    assert s["avg_power_kwh"] == pytest.approx(40000)
    assert s["power_kwh_per_t"] == pytest.approx(120000 / 360, abs=0.01)
    assert s["oxygen_nm3_per_t"] == pytest.approx(3600 / 360, abs=0.01)
    assert s["carbon_kg_per_t"] == pytest.approx(900 / 360, abs=0.01)
    assert s["lime_kg_per_t"] == pytest.approx(2700 / 360, abs=0.01)


def test_heat_without_a_size_is_left_out_of_per_tonne(client):
    three_heats_of_120_t(client)
    client.post("/heats", json=heat("H4", power_kwh=50000))
    s = entry_for(client, "SAE1018")
    assert s["heats"] == 4
    assert s["avg_power_kwh"] == pytest.approx(42500)       # counted in the plain average
    assert s["total_heat_size_t"] == pytest.approx(360)      # but has no size
    assert s["power_kwh_per_t"] == pytest.approx(120000 / 360, abs=0.01)  # so not in per tonne


def test_summary_time_and_electrode(client):
    first = heat("H1", start_time="2026-10-01T06:00:00", end_time="2026-10-01T07:00:00",
                 tap_weight_t=120, electrode_kg=60)
    second = heat("H2", start_time="2026-10-01T08:00:00", end_time="2026-10-01T09:30:00",
                  tap_weight_t=120, electrode_kg=90)
    assert client.post("/heats", json=first).status_code == 201
    assert client.post("/heats", json=second).status_code == 201
    s = entry_for(client, "SAE1018")
    assert s["avg_duration_min"] == pytest.approx(75)
    assert s["tonnes_per_hour"] == pytest.approx(96, abs=0.1)      # 240 t in 2.5 hours
    assert s["avg_electrode_kg"] == pytest.approx(75)
    assert s["electrode_kg_per_t"] == pytest.approx(150 / 240, abs=0.01)


def test_heat_ending_before_it_starts_is_left_out_of_durations(client):
    body = heat("H1", start_time="2026-10-01T08:00:00", end_time="2026-10-01T07:00:00", tap_weight_t=120)
    assert client.post("/heats", json=body).status_code == 201
    s = entry_for(client, "SAE1018")
    assert s["avg_duration_min"] is None
    assert s["tonnes_per_hour"] is None


# ---------- CSV export ----------

def test_csv_export(client):
    client.post("/heats", json=heat("H1", tap_weight_t=120, power_kwh=40000))
    client.post("/heats", json=heat("H2", grade="=SUM(1)"))
    r = client.get("/export.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    rows = list(csv.reader(io.StringIO(r.text.lstrip("\ufeff"))))
    header = rows[0]
    assert "power_kwh_per_t" in header
    by_no = {row[0]: dict(zip(header, row)) for row in rows[1:]}
    assert by_no["H1"]["power_kwh_per_t"] == "333.33"
    assert by_no["H2"]["power_kwh_per_t"] == ""          # no heat size, so no per-tonne value
    assert by_no["H2"]["grade"] == "'=SUM(1)"             # Excel cannot run it as a formula


# ---------- upgrading an old database ----------

def test_old_database_is_upgraded(monkeypatch):
    old = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    with old.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE heats (id INTEGER PRIMARY KEY, heat_no VARCHAR NOT NULL UNIQUE, "
            "furnace VARCHAR NOT NULL, grade VARCHAR, shift VARCHAR, start_time DATETIME, "
            "end_time DATETIME, tap_temp FLOAT, power_kwh FLOAT, electrode_kg FLOAT)"
        )
    monkeypatch.setattr(main, "engine", old)
    main.add_missing_columns()
    main.add_missing_columns()      # running it a second time must change nothing and not fail
    with old.connect() as conn:
        columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(heats)")}
    assert {"tap_weight_t", "oxygen_nm3", "lime_kg", "carbon_kg"} <= columns
