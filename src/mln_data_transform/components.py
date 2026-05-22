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
    TEC = "Technology"
