# Heat Records API

Personal project: a REST API for steelmaking heat records (EAF/LRF).

## Run
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python import_csv.py sample_heats.csv
uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs to try every endpoint.

## Endpoints
- GET /heats?furnace=EAF&grade=B500B&date_from=2026-10-01
- GET /heats/{heat_no}
- POST /heats
- PATCH /heats/{heat_no}
- POST /heats/{heat_no}/events
- DELETE /heats/{heat_no}

Sample data is made up. Do not put real plant data in a public repo.
