import logging
from functools import cached_property

from mln_data_transform.components import (
    SetBook,
    TeacherSetSpecialFormat,
    WorldcatSetPart,
)
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.transform import WorldcatManager

logger = logging.getLogger(__name__)


class TeacherSetData:
    """A data model for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        copies_of_set: int,
        grade_level: str,
        language: str,
        parts: list[dict[str, str]],
        set_title: str,
        set_type: str,
        study_program_info: str,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        special_formats: list[TeacherSetSpecialFormat] | None = None,
    ) -> None:
        self.copies_of_set = copies_of_set
        self.grade_level = GradeReadingLevel(grade_level)
        self.language = language
        self.local_genre_term: list[TaxonomyGenre] = [
            TaxonomyGenre(i) for i in local_genre_term if local_genre_term
        ]
        self.local_topic_term: list[TaxonomyTopic] = [
            TaxonomyTopic(i) for i in local_topic_term if local_topic_term
        ]
        self.parts = [SetBook(**i) for i in parts]
        self.set_title = set_title
        self.set_type = SetTypeFormat(set_type)
        self.study_program_info = SubjectStudyProgram(study_program_info)
        self.special_formats = special_formats

    @property
    def enhanced(self) -> str | None:
        if self.special_formats:
            return "E"
        return None

    @property
    def record_type(self) -> str:
        if self.enhanced:
            return "o"
        return "a"


class TeacherSet:
    def __init__(
        self, set_data: TeacherSetData, worldcat_manager: WorldcatManager
    ) -> None:
        self.worldcat_manager = worldcat_manager
        self._set_data = set_data

        self.copies_of_set = self._set_data.copies_of_set
        self.enhanced = self._set_data.enhanced
        self.grade_level = self._set_data.grade_level
        self.language = self._set_data.language
        self.local_genre_term = self._set_data.local_genre_term
        self.local_topic_term = self._set_data.local_topic_term
        self.record_type = self._set_data.record_type
        self.set_title = self._set_data.set_title
        self.set_type = self._set_data.set_type
        self.study_program_info = self._set_data.study_program_info

    @cached_property
    def parts(self) -> list[WorldcatSetPart]:
        parts = []
        for isbn, copies in self._set_data.parts.items():
            worldcat_part = self.worldcat_manager.get_worldcat_data_for_part(isbn=isbn)
            parts.append(
                WorldcatSetPart(
                    isbn=isbn,
                    title=worldcat_part.title,
                    author=worldcat_part.author_name,
                    author_dates=worldcat_part.author_dates,
                    pub_date=worldcat_part.pub_date,
                    description=worldcat_part.description,
                    copies=copies,
                    subjects=worldcat_part.subjects,
                )
            )
        parts.extend(self._set_data.special_formats)
        return parts

    @property
    def physical_description(self) -> str:
        return f"{sum([i.copies for i in self.parts])} item(s)"
