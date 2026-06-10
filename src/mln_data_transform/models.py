import logging
from typing import Any, Sequence

from mln_data_transform.components import (
    TeacherSetBook,
    TeacherSetSpecialFormat,
    VarFieldData,
)
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
)

logger = logging.getLogger(__name__)


class TeacherSetData:
    """A data model for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        copy_number: int,
        grade_level: str | GradeReadingLevel,
        language: str,
        parts: Sequence[TeacherSetBook | TeacherSetSpecialFormat],
        physical_description: str,
        record_type: str,
        shelf_number: str,
        study_program_info: str | SubjectStudyProgram,
        set_title: str,
        set_type: str | SetTypeFormat,
        total_copies: int,
        control_number: str | None = None,
        enhanced: str | None = None,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        var_field_data: list[VarFieldData] | None = None,
    ) -> None:
        self.copy_number = copy_number
        self.control_number = control_number
        self.enhanced = enhanced
        self.grade_level = (
            GradeReadingLevel(grade_level)
            if isinstance(grade_level, str)
            else grade_level
        )
        self.language = language
        self.local_genre_term = local_genre_term
        self.local_topic_term = local_topic_term
        self.parts = parts
        self.physical_description = physical_description
        self.record_type = record_type
        self.set_title = set_title
        self.set_type = (
            SetTypeFormat(set_type) if isinstance(set_type, str) else set_type
        )
        self.shelf_number = shelf_number
        self.study_program_info = (
            SubjectStudyProgram(study_program_info)
            if isinstance(study_program_info, str)
            else study_program_info
        )
        self.total_copies = total_copies
        self.var_field_data = var_field_data

    @property
    def bib_code(self) -> str:
        return "e"

    @property
    def contents_note(self) -> str:
        part_list = []
        for part in self.parts:
            if not isinstance(part, TeacherSetBook):
                continue
            elif part.copies > 1:
                copy_part = " copies of "
            else:
                copy_part = " copy of "
            part_list.append(
                "".join([str(part.copies), copy_part, '"', part.title, '", '])
            )
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @property
    def location(self) -> str:
        return "ed"

    @property
    def material_type(self) -> str:
        return "8"

    @property
    def pub_dates(self) -> list[str]:
        all_pub_dates = []
        fuzzy_dates = []
        for part in self.parts:
            date = part.pub_date
            if isinstance(date, str) and date.isdigit():
                all_pub_dates.append(date)
            elif isinstance(date, str) and date.isalnum():
                fuzzy_dates.append(date)
        if all_pub_dates:
            return sorted([str(i) for i in all_pub_dates])
        elif fuzzy_dates:
            return sorted(fuzzy_dates)
        return all_pub_dates

    @property
    def subjects(self) -> list[VarFieldData]:
        subjects = []
        for part in self.parts:
            if isinstance(part, TeacherSetBook) and part.subjects:
                subjects.extend(
                    [
                        VarFieldData(
                            tag=i["tag"],
                            ind1=i["ind1"],
                            ind2=i["ind2"],
                            subfields=i["subfields"],
                        )
                        for i in part.subjects
                    ]
                )
        return subjects

    def to_dict(self) -> dict[str, Any]:
        return {
            "added_entries": [i.entry_dict() for i in self.parts if i.entry_dict()],
            "components": [
                i.summary_component() for i in self.parts if i.summary_component()
            ],
            "contents_note": self.contents_note,
            "control_number": self.control_number,
            "copy_number": self.copy_number,
            "grade_level": self.grade_level,
            "enhanced": self.enhanced,
            "language": self.language,
            "local_genre_term": self.local_genre_term,
            "local_topic_term": self.local_topic_term,
            "parts": self.parts,
            "physical_description": self.physical_description,
            "pub_dates": self.pub_dates,
            "record_type": self.record_type,
            "set_title": self.set_title,
            "set_type": self.set_type,
            "shelf_number": self.shelf_number,
            "study_program_info": self.study_program_info,
            "subjects": self.subjects,
            "total_copies": self.total_copies,
            "var_field_data": self.var_field_data,
        }
