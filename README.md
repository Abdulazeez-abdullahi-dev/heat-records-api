# Heat Records API

![tests](https://github.com/Abdulazeez-abdullahi-dev/heat-records-api/actions/workflows/tests.yml/badge.svg)

A REST API for storing and querying steelmaking heat records (EAF and LRF), built with Python, FastAPI and SQLite. It has a web page for browsing, charting, editing and exporting heats, is protected by an API key, and is packaged as a downloadable Windows app.

![Heat Records web page](screenshot.png)

All data in this repository is **made up** for demonstration. It contains no real plant records.

## What it does

The API stores heats (one batch of steel) and the events recorded during each heat, such as temperature readings and chemistry samples. You can list and filter heats, update them as results come in, and get a summary per grade, including totals and consumption per tonne of steel.

## Features

- List heats with filters: furnace, grade, date range
- Create and update heats (POST, PATCH)
- Attach temperature and chemistry events to a heat
- Input validation, e.g. tap temperature must be between 1400 and 1800 °C
- Duplicate heat numbers are rejected (409 Conflict)
- Summary per grade: number of heats, total heat size, averages per heat (tap temperature, heat size, power, carbon injection, oxygen, lime) and per tonne of steel (power, carbon injection, oxygen, lime)
- Web page at `/` with the summary, a filterable heat table, and forms to add, edit and delete heats (API errors are shown on the page)
- Totals and per-tonne calculator: tick any heats (or use the heats shown) to get total heat size and total power, oxygen, carbon and lime divided by total tonnes
- Chart of tap temperature by heat, with EAF and LRF drawn as separate lines
- CSV export of the heats shown (opens in Excel)
- API-key protection: the key is created on first start and saved in `api_key.txt`
- Older databases are upgraded automatically when the app starts
- 21 automated tests, run on GitHub for every push
- Interactive documentation at `/docs`
- Packaged as a Windows app (`HeatRecordsAPI.exe`) that starts the server and opens the web page

## Download and run (Windows)

1. Download `HeatRecordsAPI.exe` from the [Releases](../../releases) page.
2. Double-click it. The first start can take up to 30 seconds.
3. If Windows shows "Windows protected your PC", click **More info**, then **Run anyway**. This warning appears for any app that is not code-signed.
4. A black window opens (this is the server, keep it open) and your browser opens the web page at http://127.0.0.1:8000/. The API documentation is at http://127.0.0.1:8000/docs.
5. On first start the app creates a file called `api_key.txt` next to the `.exe`. Open it, copy the key, and paste it into the box on the web page. Keep this file private.

The app starts with an empty database. Add heats with the form on the page. Close the black window to stop it.

## Run from source

Requires Python 3.10 or newer. Commands are for Windows PowerShell.

```
git clone https://github.com/Abdulazeez-abdullahi-dev/heat-records-api.git
cd heat-records-api
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python import_csv.py sample_heats.csv
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/ for the web page, or http://127.0.0.1:8000/docs to try the endpoints. The key is created on first start in `api_key.txt`. You can also set your own with the `HEAT_API_KEY` environment variable.

To build the app yourself:

```
pip install pyinstaller
pyinstaller --noconfirm --onefile --name HeatRecordsAPI --collect-submodules uvicorn launcher.py
```

The result is `dist\HeatRecordsAPI.exe`.

## Run the tests

```
pip install -r requirements-dev.txt
python -m pytest -v
```

The tests use a temporary in-memory database and their own test key, so they never touch your real data or your `api_key.txt`.

## Endpoints

Every endpoint except the web page (`/`) needs the key in an `X-API-Key` header. In `/docs`, click **Authorize** and paste the key.

| Method | Path | Purpose |
|---|---|---|
| GET | / | Web page |
| GET | /heats | List heats (filters: furnace, grade, date_from, date_to) |
| GET | /heats/{heat_no} | One heat with its events |
| POST | /heats | Create a heat |
| PATCH | /heats/{heat_no} | Update only the fields you send |
| POST | /heats/{heat_no}/events | Add a temperature or chemistry event |
| DELETE | /heats/{heat_no} | Delete a heat |
| GET | /summary | Per grade: heats, total heat size, averages per heat and per tonne of steel |
| GET | /export.csv | Heats as a CSV file (same filters as `/heats`) |

## Example

Calling the API from PowerShell with the key:

```
Invoke-RestMethod -Uri http://127.0.0.1:8000/summary -Headers @{ "X-API-Key" = "YOUR_KEY" }
```

`GET /summary` returns one entry per grade (values below are example numbers):

```json
[
  {
    "grade": "SAE1018",
    "heats": 3,
    "total_heat_size_t": 360.0,
    "avg_tap_temp": 1637.5,
    "avg_heat_size_t": 120.0,
    "avg_power_kwh": 40000.0,
    "avg_carbon_kg": 600.0,
    "avg_oxygen_nm3": 3000.0,
    "avg_lime_kg": 1500.0,
    "power_kwh_per_t": 333.33,
    "carbon_kg_per_t": 5.0,
    "oxygen_nm3_per_t": 25.0,
    "lime_kg_per_t": 12.5
  }
]
```

Per tonne means total used divided by total heat size, counting only heats that have both values. A value that has not been entered for any heat of that grade is returned as `null`.

## What I learned

I built this as a beginner, working through it step by step. I learned how an API turns a request into a database query, how POST and PATCH differ, and how status codes (200, 201, 404, 409, 422) describe what happened. I added my own fields with validation limits, wrote a summary endpoint and checked it against a hand calculation, published the project with Git and GitHub, built a web page for it with plain HTML and JavaScript, added a totals and per-tonne calculator, a two-line chart and CSV export, protected it with an API key, and packaged it as a Windows app with PyInstaller.

## Possible next steps

- Move from SQLite to PostgreSQL
- Serve over HTTPS for use on a network
