# Book Recommendation API

A FastAPI project with persistent storage and automated CI/CD.

## Features

- Add books (title, author, genre)
- List all books
- Get recommendations by genre

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Usage

- POST `/books/`  
  `{ "title": "...", "author": "...", "genre": "..." }`
- GET `/books/`
- GET `/recommendations/?genre=GENRE`

## Test

```bash
pytest
```

## Lint

```bash
ruff .
```

## Docker

```bash
docker build -t joelmw .
docker run -p 8000:8000 joelmw
```

## GitHub Actions

- Lints and tests code on every push/PR
- Builds and pushes Docker image to GHCR on push to `main`
