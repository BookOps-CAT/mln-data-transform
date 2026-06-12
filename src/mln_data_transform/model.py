import logging
from typing import Sequence

from mln_data_transform.components import (
    TeacherSetSpecialFormat,
    VarFieldData,
    WorldcatSetPart,
)
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
)

logger = logging.getLogger(__name__)


class TeacherSetCopy:
    """A data model for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        copies_of_set: int,
        copy_number: int,
        grade_level: str | GradeReadingLevel,
        language: str,
        parts: Sequence[WorldcatSetPart | TeacherSetSpecialFormat],
        physical_description: str,
        record_type: str,
        set_title: str,
        set_type: str | SetTypeFormat,
        shelf_number: str,
        study_program_info: str | SubjectStudyProgram,
        barcode: str | None = None,
        bib_id: str | None = None,
        enhanced: str | None = None,
        legacy_call_number: str | None = None,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        var_field_data: list[VarFieldData] | None = None,
    ) -> None:
        self.barcode = barcode
        self.bib_id = bib_id
        self.copy_number = copy_number
        self.copies_of_set = copies_of_set
        self.grade_level = grade_level
        self.enhanced = enhanced
        self.language = language
        self.legacy_call_number = legacy_call_number
        self.local_genre_term = local_genre_term
        self.local_topic_term = local_topic_term
        self.parts = [WorldcatSetPart(**i) for i in parts if "isbn" in i] + [
            TeacherSetSpecialFormat(**i) for i in parts if "isbn" not in i
        ]
        self.physical_description = physical_description
        self.record_type = record_type
        self.set_title = set_title
        self.set_type = set_type
        self.shelf_number = shelf_number
        self.study_program_info = study_program_info
        self.var_field_data = var_field_data

    @property
    def contents_note(self) -> str:
        part_list = []
        for part in self.parts:
            if not isinstance(part, WorldcatSetPart):
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
            if isinstance(part, WorldcatSetPart) and part.subjects:
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
