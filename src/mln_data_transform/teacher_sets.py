import logging
from typing import Any

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
        special_formats: list[dict[str, str]] | None = None,
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
        self.special_formats = (
            [TeacherSetSpecialFormat(**i) for i in special_formats]
            if special_formats
            else None
        )

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

    def get_worldcat_data_for_parts(self) -> list[dict[str, Any]]:
        parts = []
        data_parts = self.parts
        logger.info(f"Record contains {len(data_parts)} ISBN(s) to query WorldCat.")
        with WorldcatManager() as manager:
            for part in data_parts:
                worldcat_part = manager.get_worldcat_data_for_part(isbn=part.isbn)
                parts.append(worldcat_part.to_dict())
        return parts


class TeacherSet:
    def __init__(
        self, set_data: TeacherSetData, worldcat_parts: list[WorldcatSetPart]
    ) -> None:
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
        self.worldcat_parts = worldcat_parts

    @property
    def contents_note(self) -> str:
        part_list = []
        special_formats = []
        for part in self.parts:
            copies = str(part.copies)
            title = part.title.strip(".")
            if isinstance(part, TeacherSetSpecialFormat):
                special_formats.append("".join([copies, f" {title}(s), "]))
            elif part.copies > 1:
                part_list.append("".join([copies, ' copies of "', title, '", ']))
            else:
                part_list.append("".join([copies, ' copy of "', title, '", ']))
        if self._set_data.special_formats:
            part_list.extend(special_formats)
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @property
    def parts(self) -> list[WorldcatSetPart]:
        parts = []
        parts_dict = {i.isbn: i.copies for i in self._set_data.parts}
        for worldcat_part in self.worldcat_parts:
            parts.append(
                WorldcatSetPart(
                    isbn=worldcat_part["isbn"],
                    title=worldcat_part["title"],
                    author=worldcat_part["author_name"],
                    author_dates=worldcat_part["author_dates"],
                    pub_date=worldcat_part["pub_date"],
                    description=worldcat_part["description"],
                    copies=parts_dict[worldcat_part["isbn"]],
                    subjects=worldcat_part["subjects"],
                )
            )
        if self._set_data.special_formats:
            parts.extend(self._set_data.special_formats)
        return parts

    @property
    def physical_description(self) -> str:
        return f"{sum([i.copies for i in self.parts])} item(s)"
