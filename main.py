from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from models import Book
from database import create_db_and_tables, get_session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/books/", response_model=Book)
def add_book(book: Book, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/books/", response_model=list[Book])
def list_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books

@app.get("/recommendations/", response_model=list[Book])
def get_recommendations(genre: str, session: Session = Depends(get_session)):
    books = session.exec(select(Book).where(Book.genre == genre)).all()
    if not books:
        raise HTTPException(status_code=404, detail="No recommendations found for this genre")
    return books
