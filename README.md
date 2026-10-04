# Book Recommendation API

FastAPI + SQLModel + SQLite, with a built-in web page at `/`.

## Run locally
```
python -m venv .venv
.venv\Scripts\Activate.ps1      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://127.0.0.1:8000 (web page) or http://127.0.0.1:8000/docs (API docs).

## Sample data
On first start with an empty database, ~60 real books are added automatically (set `SEED_SAMPLE_DATA=0` to disable).
To add them to an existing database: `python seed.py` (skips ones already there).

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Web page |
| GET | `/health` | Health check |
| POST | `/books/` | Add a book (201; 409 if duplicate; 422 if invalid) |
| GET | `/books/?q=&genre=&skip=&limit=` | List / search |
| GET | `/books/{id}` | One book |
| PATCH | `/books/{id}` | Update some fields |
| DELETE | `/books/{id}` | Delete (204) |
| GET | `/genres/` | All genres |
| GET | `/recommendations/?genre=&limit=` | Random books in a genre (404 if none) |

## Test and lint
```
pytest
ruff check .
```

## Docker
```
docker build -t joelwm .
docker run -p 8000:8000 -v joelwm-data:/data joelwm
```
The volume keeps your books between container restarts. Set `DATABASE_URL` to use another database file.

## CI
GitHub Actions lints and tests on every push/PR to `master`, and pushes the image to GHCR on push to `master`.
