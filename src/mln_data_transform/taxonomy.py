import logging
import re
from enum import StrEnum

logger = logging.getLogger(__name__)


class ComponentFormat(StrEnum):
    lprint = "Large print"
    dvd = "DVD"
    book = "book"
    playaway = "Playaway audiobook"


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
    ELA = "Language Arts"
    CHLA = "Language Arts"
    FRLA = "Language Arts"
    SPLA = "Language Arts"
    MAT = "Math"
    PDE = "Professional Development"
    SCI = "Science"
    SEL = "Social Emotional Learning"
    SOC = "Social Studies"
    TEC = "Technology"
    WorldLang = "Language Arts"
    GAME = "Game"


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


GENRE_REGEX_MAP = {
    TaxonomyGenre.adventure: re.compile(r"adventure", re.IGNORECASE),
    TaxonomyGenre.award_winners: re.compile(
        r"(book )?award((s?)|( winners))", re.IGNORECASE
    ),
    TaxonomyGenre.biography: re.compile(r"\b(biograph)((y)|(ical))", re.IGNORECASE),
    TaxonomyGenre.comics_graphic_novels: re.compile(
        r"comics?|graphic novels?", re.IGNORECASE
    ),
    TaxonomyGenre.coming_of_age: re.compile(
        r"(coming[- ]of[- ]age|bildungsromans?)", re.IGNORECASE
    ),
    TaxonomyGenre.fantasy: re.compile(r"fantasy", re.IGNORECASE),
    TaxonomyGenre.fiction: re.compile(r"(\bfiction(al)?\b)", re.IGNORECASE),
    TaxonomyGenre.folklore: re.compile(r"folklore", re.IGNORECASE),
    TaxonomyGenre.manga: re.compile(r"manga", re.IGNORECASE),
    TaxonomyGenre.memoir: re.compile(r"memoir|autobiograph((y)|(ical))", re.IGNORECASE),
    TaxonomyGenre.mystery: re.compile(r"(myster)((y)|(ies))", re.IGNORECASE),
    TaxonomyGenre.nonfiction: re.compile(r"(\bnonfiction(al)?\b)", re.IGNORECASE),
    TaxonomyGenre.poetry: re.compile(r"poetry|poems?", re.IGNORECASE),
    TaxonomyGenre.romance: re.compile(r"romance", re.IGNORECASE),
}

TOPIC_REGEX_MAP = {
    TaxonomyTopic.african_americans: re.compile(r"african americans?", re.IGNORECASE),
    TaxonomyTopic.ancient_civilization: re.compile(
        r"ancient civilizations?", re.IGNORECASE
    ),
    TaxonomyTopic.animals: re.compile(
        r"animals?|mammals?|reptiles?|birds?", re.IGNORECASE
    ),
    TaxonomyTopic.asian_americans: re.compile(r"asian americans?", re.IGNORECASE),
    TaxonomyTopic.astronomy: re.compile(r"astronomy|space(?! and time)", re.IGNORECASE),
    TaxonomyTopic.autism: re.compile(r"autism", re.IGNORECASE),
    TaxonomyTopic.behavior: re.compile(r"^behavior|^helping behavior", re.IGNORECASE),
    TaxonomyTopic.bullying: re.compile(r"bull((ying)|(ies))", re.IGNORECASE),
    TaxonomyTopic.chinese_americans: re.compile(r"chinese americans?", re.IGNORECASE),
    TaxonomyTopic.civil_rights: re.compile(r"civil rights", re.IGNORECASE),
    TaxonomyTopic.community: re.compile(r"communit((y)|(ies))", re.IGNORECASE),
    TaxonomyTopic.concepts: re.compile(r"(?<!philosophical )concepts?", re.IGNORECASE),
    TaxonomyTopic.cooking: re.compile(r"cooking", re.IGNORECASE),
    TaxonomyTopic.courage: re.compile(r"courage", re.IGNORECASE),
    TaxonomyTopic.cultural_heritage: re.compile(
        r"cultural ((heritage)|(property))", re.IGNORECASE
    ),
    TaxonomyTopic.dance: re.compile(r"dance", re.IGNORECASE),
    TaxonomyTopic.family: re.compile(r"family", re.IGNORECASE),
    TaxonomyTopic.health_wellness: re.compile(
        r"health|wellness|nutrition", re.IGNORECASE
    ),
    TaxonomyTopic.immigration: re.compile(r"immigra((tion)|(nt[s]?))", re.IGNORECASE),
    TaxonomyTopic.music: re.compile(r"music(ians)?", re.IGNORECASE),
    TaxonomyTopic.new_york_city: re.compile(
        r"(new york,? ?\(?n\.y\.\)?)|nyc|bronx|manhattan|brooklyn|staten island",
        re.IGNORECASE,
    ),
    TaxonomyTopic.plants: re.compile(r"plants", re.IGNORECASE),
    TaxonomyTopic.sports: re.compile(r"sports|athlet((es?)|ics)", re.IGNORECASE),
    TaxonomyTopic.weather: re.compile(r"weather|natural disasters", re.IGNORECASE),
}
