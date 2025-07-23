from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_and_list_books():
    # Add a book
    response = client.post("/books/", json={"title": "1984", "author": "George Orwell", "genre": "Dystopian"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "1984"
    # List books
    response = client.get("/books/")
    assert response.status_code == 200
    books = response.json()
    assert any(book["title"] == "1984" for book in books)

def test_recommendations():
    client.post("/books/", json={"title": "Brave New World", "author": "Aldous Huxley", "genre": "Dystopian"})
    response = client.get("/recommendations/", params={"genre": "Dystopian"})
    assert response.status_code == 200
    books = response.json()
    assert any(book["title"] in ["1984", "Brave New World"] for book in books)
