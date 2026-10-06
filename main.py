import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from sqlmodel import Session, func, select

from database import create_db_and_tables, engine, get_session
from models import Book, BookCreate, BookUpdate
from seed import seed_books

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("joelwm")

STATIC_DIR = Path(__file__).parent / "static"

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    if os.getenv("SEED_SAMPLE_DATA", "1") != "0":
        with Session(engine) as session:
            if session.exec(select(func.count()).select_from(Book)).one() == 0:
                logger.info("Empty database: added %s sample books", seed_books(session))
    logger.info("Database ready")
    yield


app = FastAPI(
    title="Book Recommendation API",
    description="Add books, search them, and get recommendations by genre.",
    version="1.0.0",
    lifespan=lifespan,
)


def _find_duplicate(
    session: Session, title: str, author: str, exclude_id: int | None = None
) -> Book | None:
    stmt = select(Book).where(
        func.lower(Book.title) == title.lower(),
        func.lower(Book.author) == author.lower(),
    )
    if exclude_id is not None:
        stmt = stmt.where(Book.id != exclude_id)
    return session.exec(stmt).first()


@app.get("/", include_in_schema=False)
def home():
    index = STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(
            status_code=503,
            detail=f"Web page not found. Expected file at: {index}",
        )
    return FileResponse(index)


@app.get("/health")
def health(session: SessionDep):
    session.exec(select(1)).one()
    return {"status": "ok"}


@app.post("/books/", response_model=Book, status_code=status.HTTP_201_CREATED)
def add_book(payload: BookCreate, session: SessionDep):
    if _find_duplicate(session, payload.title, payload.author):
        raise HTTPException(status_code=409, detail="This book already exists")
    book = Book.model_validate(payload)
    session.add(book)
    session.commit()
    session.refresh(book)
    logger.info("Added book id=%s", book.id)
    return book


@app.get("/books/", response_model=list[Book])
def list_books(
    session: SessionDep,
    q: Annotated[str | None, Query(description="Search title or author")] = None,
    genre: Annotated[str | None, Query(description="Filter by genre")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    stmt = select(Book)
    if q and q.strip():
        term = q.strip().lower()
        stmt = stmt.where(
            func.lower(Book.title).contains(term, autoescape=True)
            | func.lower(Book.author).contains(term, autoescape=True)
        )
    if genre and genre.strip():
        stmt = stmt.where(func.lower(Book.genre) == genre.strip().lower())
    stmt = stmt.order_by(Book.id.desc()).offset(skip).limit(limit)
    return session.exec(stmt).all()


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: SessionDep):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, payload: BookUpdate, session: SessionDep):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    changes = {
        k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None
    }
    new_title = changes.get("title", book.title)
    new_author = changes.get("author", book.author)
    if _find_duplicate(session, new_title, new_author, exclude_id=book.id):
        raise HTTPException(status_code=409, detail="This book already exists")
    for key, value in changes.items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: SessionDep):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/genres/", response_model=list[str])
def list_genres(session: SessionDep):
    return session.exec(select(Book.genre).distinct().order_by(Book.genre)).all()


@app.get("/recommendations/", response_model=list[Book])
def get_recommendations(
    genre: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=50)] = 5,
):
    books = session.exec(
        select(Book)
        .where(func.lower(Book.genre) == genre.strip().lower())
        .order_by(func.random())
        .limit(limit)
    ).all()
    if not books:
        raise HTTPException(
            status_code=404, detail="No recommendations found for this genre"
        )
    return books
