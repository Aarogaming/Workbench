# Python Environment Baseline

- Python: 3.12
- Create venv: `py -3.12 -m venv .venv`
- Upgrade pip: `.venv/Scripts/python -m pip install --upgrade pip`
- Install deps (per repo): `.venv/Scripts/python -m pip install -r requirements.txt`
- Run tests (AAS): `.venv/Scripts/python -m pytest`

Notes: keep per-repo pins; align on 3.12 to avoid wheel issues (Pillow/others).