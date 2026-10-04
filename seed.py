"""Sample library of real books.

Run `python seed.py` to add any that are missing (safe to run repeatedly).
The app also calls seed_books() on startup when the database is empty;
set SEED_SAMPLE_DATA=0 to turn that off.
"""

from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import Book

SAMPLE_BOOKS = [
    # Dystopian
    ("1984", "George Orwell", "Dystopian"),
    ("Brave New World", "Aldous Huxley", "Dystopian"),
    ("Fahrenheit 451", "Ray Bradbury", "Dystopian"),
    ("The Handmaid's Tale", "Margaret Atwood", "Dystopian"),
    ("We", "Yevgeny Zamyatin", "Dystopian"),
    # Science Fiction
    ("Dune", "Frank Herbert", "Science Fiction"),
    ("Foundation", "Isaac Asimov", "Science Fiction"),
    ("Neuromancer", "William Gibson", "Science Fiction"),
    ("The Left Hand of Darkness", "Ursula K. Le Guin", "Science Fiction"),
    ("Ender's Game", "Orson Scott Card", "Science Fiction"),
    ("The Martian", "Andy Weir", "Science Fiction"),
    ("Snow Crash", "Neal Stephenson", "Science Fiction"),
    # Fantasy
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy"),
    ("The Fellowship of the Ring", "J.R.R. Tolkien", "Fantasy"),
    ("A Wizard of Earthsea", "Ursula K. Le Guin", "Fantasy"),
    ("The Name of the Wind", "Patrick Rothfuss", "Fantasy"),
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Fantasy"),
    ("A Game of Thrones", "George R.R. Martin", "Fantasy"),
    # Classic
    ("Pride and Prejudice", "Jane Austen", "Classic"),
    ("Jane Eyre", "Charlotte Brontë", "Classic"),
    ("Wuthering Heights", "Emily Brontë", "Classic"),
    ("Great Expectations", "Charles Dickens", "Classic"),
    ("Moby-Dick", "Herman Melville", "Classic"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Classic"),
    ("To Kill a Mockingbird", "Harper Lee", "Classic"),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Classic"),
    ("War and Peace", "Leo Tolstoy", "Classic"),
    # African Literature
    ("Things Fall Apart", "Chinua Achebe", "African Literature"),
    ("Half of a Yellow Sun", "Chimamanda Ngozi Adichie", "African Literature"),
    ("Purple Hibiscus", "Chimamanda Ngozi Adichie", "African Literature"),
    ("Americanah", "Chimamanda Ngozi Adichie", "African Literature"),
    ("Weep Not, Child", "Ngũgĩ wa Thiong'o", "African Literature"),
    ("The River Between", "Ngũgĩ wa Thiong'o", "African Literature"),
    ("A Grain of Wheat", "Ngũgĩ wa Thiong'o", "African Literature"),
    ("Petals of Blood", "Ngũgĩ wa Thiong'o", "African Literature"),
    ("The Beautyful Ones Are Not Yet Born", "Ayi Kwei Armah", "African Literature"),
    # Fiction
    ("The Alchemist", "Paulo Coelho", "Fiction"),
    ("The Kite Runner", "Khaled Hosseini", "Fiction"),
    ("Life of Pi", "Yann Martel", "Fiction"),
    ("One Hundred Years of Solitude", "Gabriel García Márquez", "Fiction"),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction"),
    # Mystery
    ("Murder on the Orient Express", "Agatha Christie", "Mystery"),
    ("And Then There Were None", "Agatha Christie", "Mystery"),
    ("The Hound of the Baskervilles", "Arthur Conan Doyle", "Mystery"),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Mystery"),
    ("Gone Girl", "Gillian Flynn", "Mystery"),
    ("The Da Vinci Code", "Dan Brown", "Mystery"),
    # Horror
    ("Dracula", "Bram Stoker", "Horror"),
    ("Frankenstein", "Mary Shelley", "Horror"),
    ("The Shining", "Stephen King", "Horror"),
    # Non-fiction
    ("Sapiens", "Yuval Noah Harari", "Non-fiction"),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Non-fiction"),
    ("Atomic Habits", "James Clear", "Non-fiction"),
    ("Guns, Germs, and Steel", "Jared Diamond", "Non-fiction"),
    ("A Brief History of Time", "Stephen Hawking", "Non-fiction"),
    # Memoir
    ("Long Walk to Freedom", "Nelson Mandela", "Memoir"),
    ("Born a Crime", "Trevor Noah", "Memoir"),
    ("Educated", "Tara Westover", "Memoir"),
    ("Unbowed", "Wangari Maathai", "Memoir"),
    ("The Diary of a Young Girl", "Anne Frank", "Memoir"),
    # Programming
    ("Clean Code", "Robert C. Martin", "Programming"),
    ("The Pragmatic Programmer", "Andrew Hunt and David Thomas", "Programming"),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Programming"),
    ("Fluent Python", "Luciano Ramalho", "Programming"),
    ("Python Crash Course", "Eric Matthes", "Programming"),
]


def seed_books(session: Session) -> int:
    """Insert sample books that are not already present. Returns how many were added."""
    existing = {
        (title.lower(), author.lower())
        for title, author in session.exec(select(Book.title, Book.author)).all()
    }
    added = 0
    for title, author, genre in SAMPLE_BOOKS:
        if (title.lower(), author.lower()) in existing:
            continue
        session.add(Book(title=title, author=author, genre=genre))
        added += 1
    session.commit()
    return added


if __name__ == "__main__":
    create_db_and_tables()
    with Session(engine) as session:
        print(f"Added {seed_books(session)} new books.")
