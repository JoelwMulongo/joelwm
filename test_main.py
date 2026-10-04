import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from database import get_session
from main import app
from seed import SAMPLE_BOOKS, seed_books

ORWELL = {"title": "1984", "author": "George Orwell", "genre": "Dystopian"}
HUXLEY = {"title": "Brave New World", "author": "Aldous Huxley", "genre": "Dystopian"}


@pytest.fixture(name="client")
def client_fixture():
    # Fresh in-memory database per test: tables guaranteed, no books.db pollution.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_home_serves_ui(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_add_and_list(client):
    r = client.post("/books/", json=ORWELL)
    assert r.status_code == 201
    assert r.json()["id"] is not None
    books = client.get("/books/").json()
    assert [b["title"] for b in books] == ["1984"]


def test_validation_rejects_blank_and_missing(client):
    assert client.post("/books/", json={**ORWELL, "title": "   "}).status_code == 422
    assert client.post("/books/", json={"title": "x"}).status_code == 422


def test_duplicate_rejected_case_insensitive(client):
    client.post("/books/", json=ORWELL)
    r = client.post("/books/", json={**ORWELL, "title": "1984 ", "author": "george orwell"})
    assert r.status_code == 409


def test_search_and_genre_filter(client):
    client.post("/books/", json=ORWELL)
    client.post("/books/", json={"title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi"})
    assert len(client.get("/books/", params={"q": "orwell"}).json()) == 1
    assert len(client.get("/books/", params={"genre": "sci-fi"}).json()) == 1
    assert client.get("/books/", params={"q": "zzz"}).json() == []


def test_pagination_limits(client):
    assert client.get("/books/", params={"limit": 0}).status_code == 422
    assert client.get("/books/", params={"skip": -1}).status_code == 422


def test_get_update_delete(client):
    book_id = client.post("/books/", json=ORWELL).json()["id"]
    assert client.get(f"/books/{book_id}").json()["author"] == "George Orwell"

    r = client.patch(f"/books/{book_id}", json={"genre": "Classic"})
    assert r.status_code == 200 and r.json()["genre"] == "Classic"

    assert client.delete(f"/books/{book_id}").status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404
    assert client.delete(f"/books/{book_id}").status_code == 404


def test_update_to_duplicate_rejected(client):
    client.post("/books/", json=ORWELL)
    other_id = client.post("/books/", json=HUXLEY).json()["id"]
    r = client.patch(f"/books/{other_id}", json=ORWELL)
    assert r.status_code == 409


def test_genres(client):
    client.post("/books/", json=ORWELL)
    client.post("/books/", json={"title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi"})
    assert client.get("/genres/").json() == ["Dystopian", "Sci-Fi"]


def test_recommendations(client):
    client.post("/books/", json=ORWELL)
    client.post("/books/", json=HUXLEY)
    r = client.get("/recommendations/", params={"genre": "dystopian", "limit": 1})
    assert r.status_code == 200 and len(r.json()) == 1


def test_recommendations_not_found(client):
    assert client.get("/recommendations/", params={"genre": "Nope"}).status_code == 404


def test_seed_adds_real_books_once(client):
    engine_session = next(app.dependency_overrides[get_session]())
    first = seed_books(engine_session)
    assert first == len(SAMPLE_BOOKS)
    assert seed_books(engine_session) == 0  # idempotent
    assert any(b["author"] == "Chinua Achebe" for b in client.get("/books/", params={"limit": 200}).json())
