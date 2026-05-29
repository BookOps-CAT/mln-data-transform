from dataclasses import dataclass


@dataclass
class CallNumber:
    """The components that make up a call number for a Teacher Set bib."""

    enumeration: str
    format: str
    grade_level: str
    shelf_number: str
    subject_code: str
    set_title: str
    enhanced: str | None = None

    @property
    def sub_a(self) -> str:
        return f"MLNYC {self.subject_code}-{self.shelf_number}"

    @property
    def sub_c(self) -> str:
        split_title = [i for i in self.set_title.split(" ") if not i.isdigit()]
        if len(split_title) >= 2:
            cutter_title = " ".join(split_title[:2])
        else:
            cutter_title = " ".join(split_title)
        return f"{cutter_title} {self.enumeration}"

    @property
    def sub_f(self) -> str:
        if self.enhanced:
            return f"{self.format} {self.enhanced}"
        else:
            return self.format

    @property
    def sub_p(self) -> str:
        return self.grade_level

    def __str__(self) -> str:
        return f"{self.sub_a} {self.sub_f} {self.sub_p} {self.sub_c}"


@dataclass
class SubjectData:
    """Data used to create a 6xx field."""

    tag: str
    ind1: str
    ind2: str
    subfields: list[tuple[str, str]]


@dataclass(frozen=True)
class SetPart:
    """A book or other item included within a Teacher Set."""

    copies: int
    description: str
    title: str


@dataclass(frozen=True)
class TeacherSetBook(SetPart):
    """A book included within a Teacher Set."""

    isbn: str
    full_title: str
    author: str | None = None
    author_dates: str | None = None
    pub_date: str | None = None
    statement_of_responsibility: str | None = None


@dataclass(frozen=True)
class TeacherSetSpecialFormat(SetPart):
    """A special format item included within a Teacher Set."""

    pub_date: str | None = None
