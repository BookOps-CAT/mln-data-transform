import logging
from typing import Any, Sequence

from pydantic import BaseModel, field_validator, model_serializer

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
    contents_note: str
    control_number: str
    grade_level: GradeReadingLevel
    language: str
    parts: Sequence[TeacherSetBook | TeacherSetSpecialFormat]
    physical_description: str
    pub_dates: list[str]
    record_type: str
    set_title: str
    set_type: SetTypeFormat
    study_program_info: SubjectStudyProgram
    subjects: list[VarFieldData]
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


class TeacherSetCopyModel(TeacherSetModel):
    copy_number: int
    shelf_number: str
    copies_of_set: int

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
            "copies_of_set": self.copies_of_set,
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
