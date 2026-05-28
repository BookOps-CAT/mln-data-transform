import datetime
from dataclasses import dataclass

from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield

from mln_data_transform.components import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectData,
    SubjectStudyProgram,
    TeacherSetBook,
    TeacherSetSpecialFormat,
)


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
        enumeration: str,
        grade_level: str | GradeReadingLevel,
        language: str,
        local_set_type: str | SetTypeFormat,
        parts: list[TeacherSetBook | TeacherSetSpecialFormat],
        physical_description: str,
        record_type: str,
        shelf_number: str,
        study_program_info: str | SubjectStudyProgram,
        set_title: str,
        begin_pub_date: str | None = "uuuu",
        control_number: str | None = None,
        end_pub_date: str | None = "uuuu",
        enhanced: str | None = None,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        subjects: list[SubjectData] | None = None,
    ) -> None:
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
        self.set_title = set_title
        self.shelf_number = shelf_number
        self.subjects = subjects
        self.study_program_info = (
            SubjectStudyProgram(study_program_info)
            if isinstance(study_program_info, str)
            else study_program_info
        )

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
    def field_001(self) -> Field:
        """Control number field"""
        return Field(tag="001", data=self.data.control_number)

    @property
    def field_003(self) -> Field:
        """Control number identifier field"""
        return Field(tag="003", data=self.data.control_number_identifier)

    @property
    def field_008(self) -> Field:
        """MARC 008 field"""
        today = datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")
        date_str = f"{today}i{self.data.begin_pub_date}{self.data.end_pub_date}"
        if self.data.leader[6] == "o":
            content = "             | ||"
        else:
            content = "           000 0 "
        return Field(tag="008", data=f"{date_str}xxu{content}{self.data.language} d")

    @property
    def field_091(self) -> Field:
        """Local MyLibraryNYC call number field"""
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
    def field_245(self) -> Field:
        """Title Field"""
        return Field(
            tag="245",
            indicators=Indicators("0", "0"),
            subfields=[
                Subfield(code="a", value=self.data.set_title),
                Subfield(code="c", value=self.data.copy_data),
            ],
        )

    @property
    def field_300(self) -> Field:
        """Physical description field"""
        return Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.physical_description)],
        )

    @property
    def field_500(self) -> Field:
        """General contents note field"""
        return Field(
            tag="500",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.contents_note)],
        )

    @property
    def field_505(self) -> Field:
        """Detailed contents note field"""
        subfield_list = []
        for n, part in enumerate(self.data.parts):
            subfield_list.append(Subfield(code="t", value=f"{part.title} /"))
            if isinstance(part, TeacherSetBook) and n + 1 < len(self.data.parts):
                subfield_list.append(Subfield(code="r", value=f"{part.author} --"))
            elif isinstance(part, TeacherSetBook) and n + 1 == len(self.data.parts):
                subfield_list.append(Subfield(code="r", value=f"{part.author}."))
        return Field(
            tag="505", indicators=Indicators("0", "0"), subfields=subfield_list
        )

    @property
    def field_520(self) -> list[Field]:
        """Summary description note field (REPEATABLE)"""
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
    def field_521(self) -> Field:
        """Reading level field"""
        return Field(
            tag="521",
            indicators=Indicators("2", " "),
            subfields=[Subfield(code="a", value=self.data.grade_level.value)],
        )

    @property
    def field_526(self) -> Field:
        """Study program information field"""
        return Field(
            tag="526",
            indicators=Indicators("8", " "),
            subfields=[Subfield(code="a", value=self.data.study_program_info.value)],
        )

    @property
    def field_6xx(self) -> list[Field]:
        """Subject fields (REPEATBLE)"""
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
    def field_690(self) -> Field:
        """Local set type field"""
        return Field(
            tag="690",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value=self.data.local_set_type.value),
                Subfield(code="2", value="bookops"),
            ],
        )

    @property
    def field_691(self) -> list[Field]:
        """Local topic term field (REPEATBLE)"""
        subject_list = []
        if self.data.local_topic_term:
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
    def field_695(self) -> list[Field]:
        """Local genre term field (REPEATBLE)"""
        subject_list = []
        if self.data.local_genre_term:
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
    def field_7xx(self) -> list[Field]:
        """Author/title/date of publication/ISBN information field (REPEATBLE)"""
        subject_list = []
        for term in self.data.parts:
            subfields = []
            if isinstance(term, TeacherSetBook) and term.author:
                tag = "700"
                ind1 = "1"
                subfields.append(Subfield(code="a", value=term.author))
                if isinstance(term, TeacherSetBook) and term.author_dates:
                    subfields.append(Subfield(code="d", value=term.author_dates))
                subfields.append(Subfield(code="t", value=term.title))
            else:
                tag = "730"
                ind1 = "0"
                subfields.append(Subfield(code="a", value=term.title))
            if term.pub_date:
                subfields.append(Subfield(code="f", value=term.pub_date))
            if isinstance(term, TeacherSetBook) and term.isbn:
                subfields.append(Subfield(code="x", value=term.isbn))
            subject_list.append(
                Field(tag=tag, indicators=Indicators(ind1, "2"), subfields=subfields)
            )
        return subject_list

    @property
    def field_901(self) -> Field:
        """Cataloger's initials field"""
        return Field(
            tag="901",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=self.data.catalogers_initials),
                Subfield(code="b", value="CATBL"),
            ],
        )

    @property
    def field_910(self) -> Field:
        """Local collection code field"""
        return Field(
            tag="910",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.local_collection_code)],
        )

    @property
    def field_909(self) -> Field:
        """Local OCLC exclusion note field"""
        return Field(
            tag="909",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.data.oclc_exclusion_note)],
        )

    def to_bib(self) -> Bib:
        bib = Bib()
        bib.library = self.data.library
        bib.leader = self.data.leader
        bib.add_field(self.field_001)
        bib.add_field(self.field_003)
        bib.add_field(self.field_008)
        bib.add_field(self.field_091)
        bib.add_field(self.field_245)
        bib.add_field(self.field_300)
        bib.add_field(self.field_500)
        bib.add_field(self.field_505)
        for field in self.field_520:
            bib.add_field(field)
        bib.add_field(self.field_521)
        bib.add_field(self.field_526)
        for field in self.field_6xx:
            bib.add_field(field)
        bib.add_field(self.field_690)
        for field in self.field_691:
            bib.add_field(field)
        for field in self.field_695:
            bib.add_field(field)
        for field in self.field_7xx:
            bib.add_field(field)
        bib.add_field(self.field_901)
        bib.add_field(self.field_910)
        bib.add_field(self.field_909)
        # add items
        return bib
