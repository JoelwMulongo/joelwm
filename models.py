from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class BookBase(SQLModel):
    # Trim whitespace before validating, so "   " is rejected as empty.
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    genre: str = Field(min_length=1, max_length=60)


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BookCreate(BookBase):
    """Request body for POST /books/ (the id is assigned by the server)."""


class BookUpdate(SQLModel):
    """Request body for PATCH /books/{id}: send only the fields to change."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=120)
    genre: Optional[str] = Field(default=None, min_length=1, max_length=60)
