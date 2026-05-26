from dataclasses import dataclass
from enum import StrEnum


class GradeReadingLevel(StrEnum):
    A = "Pre-K"
    B = "K-2"
    C = "3-5"
    D = "6-8"
    E = "9-12"


class SetTypeFormat(StrEnum):
    AUDIO = "Audio & Digital Devices"
    CLUB = "Book Club"
    GAME = "Game"
    LPRINT = "Large Print"
    PHONIC = "Phonics & Decodeables"
    STORY = "Storytelling"
    TOPIC = "Topic"


class SubjectStudyProgram(StrEnum):
    ART = "Arts & Music"
    ENG = "Engineering"
    LAN = "Language Arts"
    MAT = "Math"
    PDE = "Professional Development"
    SCI = "Science"
    SEL = "Social Emotional Learning"
    SOC = "Social Studies"
    TEC = "Technology"


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
    author: str | None = None
    author_dates: str | None = None
    pub_date: str | None = None


@dataclass(frozen=True)
class TeacherSetSpecialFormat(SetPart):
    """A special format item included within a Teacher Set."""

    pub_date: str | None = None


class TaxonomyGenre(StrEnum):
    adventure = "Adventure"
    award_winners = "Award Winners"
    biography = "Biography"
    comics_graphic_novels = "Comics & Graphic Novels"
    coming_of_age = "Coming of Age"
    fantasy = "Fantasy"
    fiction = "Fiction"
    folklore = "Folklore"
    manga = "Manga"
    memoir = "Memoir"
    mystery = "Mystery"
    nonfiction = "Nonfiction"
    poetry = "Poetry"
    romance = "Romance"


class TaxonomySubject(StrEnum):
    arts_music = "Arts & Music"
    engineering = "Engineering"
    language_arts = "Language Arts"
    math = "Math"
    professional_development = "Professional Development"
    science = "Science"
    social_emotional_learning = "Social Emotional Learning"
    social_studies = "Social Studies"
    technology = "Technology"


class TaxonomyTopic(StrEnum):
    african_americans = "African Americans"
    ancient_civilization = "Ancient Civilization"
    animals = "Animals"
    asian_americans = "Asian Americans"
    astronomy = "Astronomy"
    autism = "Autism"
    behavior = "Behavior"
    bullying = "Bullying"
    chinese_americans = "Chinese Americans"
    civil_rights = "Civil Rights"
    community = "Community"
    concepts = "Concepts"
    cooking = "Cooking"
    courage = "Courage"
    cultural_heritage = "Cultural Heritage"
    dance = "Dance"
    family = "Family"
    health_wellness = "Health & Wellness"
    immigration = "Immigration"
    music = "Music"
    new_york_city = "New York City"
    plants = "Plants"
    sports = "Sports"
    weather = "Weather"
