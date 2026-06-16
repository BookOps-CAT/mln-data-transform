import logging
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, model_serializer

from mln_data_transform.components import (
    TeacherSetSpecialFormat,
    VarFieldData,
    WorldcatSetPart,
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
    model_config = ConfigDict(extra="allow")

    contents_note: str
    copies_of_set: int
    enhanced: str | None
    grade_level: GradeReadingLevel
    language: str
    local_genre_term: list[TaxonomyGenre] | None
    local_topic_term: list[TaxonomyTopic] | None
    parts: Sequence[WorldcatSetPart | TeacherSetSpecialFormat]
    physical_description: str
    record_type: str
    set_title: str
    set_type: SetTypeFormat
    study_program_info: SubjectStudyProgram

    bib_id: str | None = None
    legacy_barcodes: dict[str, str] | None = None
    var_field_data: list[VarFieldData] | None = None


class TeacherSetCopyModel(TeacherSetModel):
    control_number: str
    copy_number: int
    subjects: list[VarFieldData]
    pub_dates: list[str]
    shelf_number: str | None = None

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
        if data.get("var_field_data"):
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
