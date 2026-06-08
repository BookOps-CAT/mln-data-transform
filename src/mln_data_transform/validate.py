import logging
from typing import Any, Sequence

from pydantic import BaseModel, computed_field, field_validator, model_serializer

from mln_data_transform.components import (
    TeacherSetBook,
    TeacherSetSpecialFormat,
    VarFieldData,
)
from mln_data_transform.serialize import TeacherSetBib
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)

logger = logging.getLogger(__name__)


class TeacherSetModel(BaseModel):
    copy_number: int
    grade_level: GradeReadingLevel
    language: str
    parts: Sequence[TeacherSetBook | TeacherSetSpecialFormat]
    physical_description: str
    record_type: str
    set_title: str
    set_type: SetTypeFormat
    shelf_number: str
    study_program_info: SubjectStudyProgram
    total_copies: int
    control_number: str | None = None
    enhanced: str | None = None
    local_genre_term: list[TaxonomyGenre] | None = None
    local_topic_term: list[TaxonomyTopic] | None = None
    var_field_data: list[VarFieldData] | None = None

    @field_validator("grade_level", mode="before")
    @classmethod
    def validate_reading_level(cls, value: Any) -> GradeReadingLevel:
        if isinstance(value, str):
            try:
                value = GradeReadingLevel[value]
            except KeyError:
                value = GradeReadingLevel(value)
        return value

    @field_validator("set_type", mode="before")
    @classmethod
    def validate_set_type(cls, value: Any) -> SetTypeFormat:
        if isinstance(value, str):
            try:
                value = SetTypeFormat[value]
            except KeyError:
                value = SetTypeFormat(value)
        return value

    @field_validator("study_program_info", mode="before")
    @classmethod
    def validate_subject(cls, value: Any) -> SubjectStudyProgram:
        if isinstance(value, str):
            try:
                value = SubjectStudyProgram[value]
            except KeyError:
                value = SubjectStudyProgram(value)
        return value

    @computed_field
    @property
    def contents_note(self) -> str:
        part_list = []
        for part in self.parts:
            if isinstance(part, TeacherSetSpecialFormat):
                continue
            elif part.copies > 1:
                copy_part = " copies of "
            else:
                copy_part = " copy of "
            part_list.append(
                "".join([str(part.copies), copy_part, '"', part.title, '", '])
            )
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @computed_field
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

    @computed_field
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

    @model_serializer
    def dump_model(self) -> dict[str, Any]:
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

    def to_set_bib(self) -> TeacherSetBib:
        data = self.model_dump()
        data["subjects"] = [
            VarFieldData(
                tag=i["tag"], ind1=i["ind1"], ind2=i["ind2"], subfields=i["subfields"]
            )
            for i in data["subjects"]
        ]
        if data["var_field_data"]:
            data["var_field_data"] = [
                VarFieldData(
                    tag=i["tag"],
                    ind1=i["ind1"],
                    ind2=i["ind2"],
                    subfields=i["subfields"],
                )
                for i in data["var_field_data"]
            ]
        return TeacherSetBib(**data)
