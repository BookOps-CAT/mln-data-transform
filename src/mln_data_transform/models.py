import datetime
from dataclasses import dataclass

from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield

from mln_data_transform.components import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
)


@dataclass
class SetPart:
    """A title or other item included within a Teacher Set."""

    author: str | None
    copies: int
    description: str
    isbn: str | None
    title: str


@dataclass
class SubjectData:
    """Data used to create a 6xx field."""

    tag: str
    ind1: str
    ind2: str
    subfields: list[tuple[str, str]]


@dataclass
class CallNumber:
    """The components that make up a call number for a Teacher Set bib."""

    enumeration: str
    format: str
    grade_level: str
    shelf_number: str
    subject_code: str
    set_title: str
    enhanced: str | None = None

    @property
    def sub_a(self) -> str:
        return f"MLNYC {self.subject_code}-{self.shelf_number}"

    @property
    def sub_c(self) -> str:
        split_title = [i for i in self.set_title.split(" ") if not i.isdigit()]
        if len(split_title) >= 2:
            cutter_title = " ".join(split_title[:2])
        else:
            cutter_title = " ".join(split_title)
        return f"{cutter_title} {self.enumeration}"

    @property
    def sub_f(self) -> str:
        if self.enhanced:
            return f"{self.format} {self.enhanced}"
        else:
            return self.format

    @property
    def sub_p(self) -> str:
        return self.grade_level

    def __str__(self) -> str:
        return f"{self.sub_a} {self.sub_f} {self.sub_p} {self.sub_c}"


class TeacherSetData:
    """A data model for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        bib_id: str,
        control_number: str,
        enumeration: str,
        grade_level: str | GradeReadingLevel,
        items: list,
        language: str,
        local_genre_term: list[str],
        local_set_type: str | SetTypeFormat,
        local_topic_term: list[str],
        parts: list[SetPart],
        physical_description: str,
        record_type: str,
        shelf_number: str,
        study_program_info: str | SubjectStudyProgram,
        set_title: str,
        begin_pub_date: str | None = "uuuu",
        end_pub_date: str | None = "uuuu",
        enhanced: str | None = None,
        subjects: list[SubjectData] | None = None,
    ) -> None:
        """
        Required components of TeacherSet bib records include:

        bib_code
        bib_id
        begin_pub_date
        call_number
        catalogers_initials
        contents_note
        control_number
        control_number_identifier
        detailed_contents_note
        end_pub_date
        enumeration
        items
        language
        library
        local_collection_code
        local_genre_term
        local_set_type
        local_topic_term
        location
        material_type
        oclc_exclusion_note
        physical_description
        pub_place
        record_type
        set_title
        subjects
        summary
        study_program_info
        """
        self.bib_id = bib_id
        self.begin_pub_date = begin_pub_date if begin_pub_date else "uuuu"
        self.control_number = control_number
        self.end_pub_date = end_pub_date if end_pub_date else "uuuu"
        self.enhanced = enhanced
        self.enumeration = enumeration
        self.grade_level = (
            GradeReadingLevel(grade_level)
            if isinstance(grade_level, str)
            else grade_level
        )
        self.items = items
        self.language = language
        self.local_genre_term = local_genre_term
        self.local_set_type = (
            SetTypeFormat(local_set_type)
            if isinstance(local_set_type, str)
            else local_set_type
        )
        self.local_topic_term = local_topic_term
        self.parts = parts
        self.physical_description = physical_description
        self.record_type = record_type
        self.shelf_number = shelf_number
        self.subjects = subjects
        self.study_program_info = (
            SubjectStudyProgram(study_program_info)
            if isinstance(study_program_info, str)
            else study_program_info
        )
        self.set_title = set_title

    @property
    def bib_code(self) -> str:
        return "e"

    @property
    def call_number(self) -> CallNumber:
        return CallNumber(
            enumeration=self.enumeration,
            format=self.local_set_type.name,
            grade_level=self.grade_level.name,
            shelf_number=self.shelf_number,
            subject_code=self.study_program_info.name,
            set_title=self.set_title.upper(),
            enhanced=self.enhanced,
        )

    @property
    def catalogers_initials(self) -> str:
        return "mlnyc-bot"

    @property
    def contents_note(self) -> str:
        part_list = []
        for part in self.parts:
            if part.copies > 1:
                copy_part = " copies of "
            else:
                copy_part = " copy of "
            part_list.append(
                "".join([str(part.copies), copy_part, '"', part.title, '", '])
            )
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @property
    def control_number_identifier(self) -> str:
        return "BookOps"

    @property
    def copy_data(self) -> str:
        parts = self.enumeration.split("-")
        return f"Copy {parts[0]} of {parts[1]}"

    @property
    def leader(self) -> str:
        return f"00000n{self.record_type}c  2200000 a 4500"

    @property
    def library(self) -> str:
        return "nypl"

    @property
    def local_collection_code(self) -> str:
        return "BL"

    @property
    def location(self) -> str:
        return "ed"

    @property
    def material_type(self) -> str:
        return "8"

    @property
    def oclc_exclusion_note(self) -> str:
        return "OCLC Holdings Exclusion"

    @property
    def pub_place(self) -> str:
        return "xxu"


class TeacherSetBib:
    """A bib record for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(self, data: TeacherSetData) -> None:
        """Components of TeacherSet bib records"""
        self.data = data

    @property
    def control_number_field(self) -> Field:
        return Field(tag="001", data=self.data.control_number)

    @property
    def control_number_identifier_field(self) -> Field:
        return Field(tag="003", data=self.data.control_number_identifier)

    @property
    def field_008(self) -> Field:
        today = datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")
        date_str = f"{today}i{self.data.begin_pub_date}{self.data.end_pub_date}"
        if self.data.leader[6] == "o":
            content = "             | ||"
        else:
            content = "           000 0 "
        return Field(tag="008", data=f"{date_str}xxu{content}{self.data.language} d")

    @property
    def call_number_field(self) -> Field:
        return Field(
            tag="091",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=self.data.call_number.sub_a),
                Subfield(code="f", value=self.data.call_number.sub_f),
                Subfield(code="p", value=self.data.call_number.sub_p),
                Subfield(code="c", value=self.data.call_number.sub_c),
            ],
        )

    @property
    def title_field(self) -> Field:
        return Field(
            tag="245",
            indicators=Indicators("0", "0"),
            subfields=[
                Subfield(code="a", value=self.data.set_title),
                Subfield(code="c", value=self.data.copy_data),
            ],
        )

    @property
    def physical_description_field(self) -> Field:
        return Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.physical_description)],
        )

    @property
    def note_500_field(self) -> Field:
        return Field(
            tag="500",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.contents_note)],
        )

    @property
    def note_505_field(self) -> Field:
        subfield_list = []
        for n, part in enumerate(self.data.parts):
            subfield_list.append(Subfield(code="t", value=f"{part.title} /"))
            if n + 1 < len(self.data.parts):
                subfield_list.append(Subfield(code="r", value=f"{part.author} --"))
            else:
                subfield_list.append(Subfield(code="r", value=f"{part.author}."))
        return Field(
            tag="505", indicators=Indicators("0", "0"), subfields=subfield_list
        )

    @property
    def note_520_field(self) -> list[Field]:
        field_list = []
        for part in self.data.parts:
            field_list.append(
                Field(
                    tag="520",
                    indicators=Indicators(" ", " "),
                    subfields=[
                        Subfield(code="3", value=part.title),
                        Subfield(code="a", value=part.description),
                    ],
                )
            )
        return field_list

    @property
    def note_521_field(self) -> Field:
        return Field(
            tag="521",
            indicators=Indicators("2", " "),
            subfields=[Subfield(code="a", value=self.data.grade_level.value)],
        )

    @property
    def note_526_field(self) -> Field:
        return Field(
            tag="526",
            indicators=Indicators("8", " "),
            subfields=[Subfield(code="a", value=self.data.study_program_info.value)],
        )

    @property
    def subjects(self) -> list[Field]:
        subject_list = []
        if not self.data.subjects:
            return []
        for subject in self.data.subjects:
            subject_list.append(
                Field(
                    tag=subject.tag,
                    indicators=Indicators(subject.ind1, subject.ind2),
                    subfields=[
                        Subfield(code=i[0], value=i[1]) for i in subject.subfields
                    ],
                )
            )
        return subject_list

    @property
    def subject_690_field(self) -> Field:
        return Field(
            tag="690",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value=self.data.local_set_type.value),
                Subfield(code="2", value="bookops"),
            ],
        )

    @property
    def subject_691_fields(self) -> list[Field]:
        subject_list = []
        for term in self.data.local_topic_term:
            subject_list.append(
                Field(
                    tag="691",
                    indicators=Indicators(" ", "7"),
                    subfields=[
                        Subfield(code="a", value=term),
                        Subfield(code="2", value="bookops"),
                    ],
                )
            )
        return subject_list

    @property
    def subject_695_fields(self) -> list[Field]:
        subject_list = []
        for term in self.data.local_genre_term:
            subject_list.append(
                Field(
                    tag="695",
                    indicators=Indicators(" ", "7"),
                    subfields=[
                        Subfield(code="a", value=term),
                        Subfield(code="2", value="bookops"),
                    ],
                )
            )
        return subject_list

    @property
    def catalogers_initials_field(self) -> Field:
        return Field(
            tag="901",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=self.data.catalogers_initials),
                Subfield(code="b", value="CATBL"),
            ],
        )

    @property
    def local_collection_code_field(self) -> Field:
        return Field(
            tag="910",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.local_collection_code)],
        )

    @property
    def oclc_exclusion_field(self) -> Field:
        return Field(
            tag="909",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.oclc_exclusion_note)],
        )

    def to_bib(self) -> Bib:
        bib = Bib()
        bib.library = self.data.library
        bib.leader = self.data.leader
        bib.add_field(self.control_number_field)
        bib.add_field(self.control_number_identifier_field)
        bib.add_field(self.field_008)
        bib.add_field(self.call_number_field)
        bib.add_field(self.title_field)
        bib.add_field(self.physical_description_field)
        bib.add_field(self.note_500_field)
        bib.add_field(self.note_505_field)
        for field in self.note_520_field:
            bib.add_field(field)
        bib.add_field(self.note_521_field)
        bib.add_field(self.note_526_field)
        for field in self.subjects:
            bib.add_field(field)
        bib.add_field(self.subject_690_field)
        for field in self.subject_691_fields:
            bib.add_field(field)
        for field in self.subject_695_fields:
            bib.add_field(field)
        bib.add_field(self.catalogers_initials_field)
        bib.add_field(self.local_collection_code_field)
        bib.add_field(self.oclc_exclusion_field)
        # add items
        return bib
