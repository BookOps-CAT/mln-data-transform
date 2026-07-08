import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VarFieldData:
    """Data used to create a 6xx field."""

    tag: str
    ind1: str
    ind2: str
    subfields: list[tuple[str, str]]


@dataclass
class SetBook:
    """A book included within a Teacher Set to be searched for in WorldCat."""

    copies: int
    id: str | None
    format: str | None = None


@dataclass(frozen=True)
class WorldcatSetPart:
    """A book included within a Teacher Set."""

    copies: int
    description: str
    id: str
    title: str
    author: str | None = None
    author_dates: str | None = None
    format: str | None = "book"
    pub_date: str | None = None
    subjects: list[dict[str, Any]] | None = None

    def entry_dict(self) -> dict[str, Any]:
        subfields = []
        if self.author:
            tag = "700"
            ind1 = "1"
            subfields.append(("a", self.author))
            if self.author_dates:
                subfields.append(("d", self.author_dates))
            subfields.append(("t", self.title))
        else:
            tag = "730"
            ind1 = "0"
            subfields.append(("a", self.title))
        if self.pub_date:
            subfields.append(("f", self.pub_date))
        subfields.append(("x", self.id))
        return {"tag": tag, "ind1": ind1, "ind2": "2", "subfields": subfields}

    def summary_component(self) -> tuple[str, str]:
        return (
            self.title.strip("."),
            self.description.strip("."),
            self.copies,
            self.format,
        )


@dataclass(frozen=True)
class TeacherSetSpecialFormat:
    """A special format item included within a Teacher Set."""

    copies: int
    description: str
    title: str
    pub_date: str | None = None

    def entry_dict(self) -> dict[str, Any]:
        return {}

    def summary_component(self) -> tuple[str, str]:
        return (self.title.strip("."), self.description.strip("."), self.copies)
