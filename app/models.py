from dataclasses import dataclass


@dataclass
class Chapter:
    index: int
    title: str
    text: str


@dataclass
class BookContent:
    title: str
    chapters: list[Chapter]
