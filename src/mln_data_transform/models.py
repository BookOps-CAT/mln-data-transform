import datetime
import logging
from typing import Sequence

from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield

from mln_data_transform.components import (
    CallNumber,
    SubjectData,
    TeacherSetBook,
    TeacherSetSpecialFormat,
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
        grade_level: GradeReadingLevel,
        language: str,
        parts: Sequence[TeacherSetBook | TeacherSetSpecialFormat],
        physical_description: str,
        record_type: str,
        shelf_number: str,
        study_program_info: SubjectStudyProgram,
        set_title: str,
        set_type: SetTypeFormat,
        total_copies: int,
        control_number: str | None = None,
        enhanced: str | None = None,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
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
        self.set_type = (
            SetTypeFormat(set_type) if isinstance(set_type, str) else set_type
        )
        self.local_topic_term = local_topic_term
        self.parts = parts
        self.physical_description = physical_description
        self.record_type = record_type
        self.set_title = set_title
        self.shelf_number = shelf_number
        self.study_program_info = (
            SubjectStudyProgram(study_program_info)
            if isinstance(study_program_info, str)
            else study_program_info
        )
        self.total_copies = total_copies

    @property
    def bib_code(self) -> str:
        return "e"

    @property
    def call_number(self) -> CallNumber:
        return CallNumber(
            format=self.set_type.name,
            grade_level=self.grade_level.name,
            shelf_number=self.shelf_number,
            subject_code=self.study_program_info.name,
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
        return f"Copy {self.copy_number} of {self.total_copies}"

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
    def pub_place(self) -> str:
        return "xxu"

    @property
    def subjects(self) -> list[SubjectData]:
        subjects = []
        for part in self.parts:
            if isinstance(part, TeacherSetBook) and part.subjects:
                subjects.extend(
                    [
                        SubjectData(
                            tag=i["tag"],
                            ind1=i["ind1"],
                            ind2=i["ind2"],
                            subfields=i["subfields"],
                        )
                        for i in part.subjects
                    ]
                )
        return subjects


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
        if not self.data.pub_dates:
            pub_date_str = "nuuuuuuuu"
        else:
            pub_date_str = f"i{self.data.pub_dates[0]}{self.data.pub_dates[-1]}"
        date_str = f"{today}{pub_date_str}"
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
                Subfield(code="a", value=f"{self.data.set_title.strip('.')}."),
                Subfield(code="n", value=self.data.copy_data),
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
                        Subfield(code="a", value=f"{part.description.strip('.')}."),
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
        subject_set = set()
        if not self.data.subjects:
            return []
        for subject in self.data.subjects:
            subject_field = Field(
                tag=subject.tag,
                indicators=Indicators(subject.ind1, subject.ind2),
                subfields=[Subfield(code=i[0], value=i[1]) for i in subject.subfields],
            )
            subject_str = subject_field.format_field()
            if subject_str not in subject_set:
                subject_set.add(subject_str)
                subject_list.append(subject_field)
        return subject_list

    @property
    def field_690(self) -> Field:
        """Local set type field"""
        return Field(
            tag="690",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value=self.data.set_type.value),
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
        bib.add_ordered_field(self.field_001)
        bib.add_ordered_field(self.field_003)
        bib.add_ordered_field(self.field_008)
        bib.add_ordered_field(self.field_091)
        bib.add_ordered_field(self.field_245)
        bib.add_ordered_field(self.field_300)
        bib.add_ordered_field(self.field_500)
        for field in self.field_520:
            bib.add_ordered_field(field)
        bib.add_ordered_field(self.field_521)
        bib.add_ordered_field(self.field_526)
        for field in self.field_6xx:
            bib.add_ordered_field(field)
        bib.add_ordered_field(self.field_690)
        for field in self.field_691:
            bib.add_ordered_field(field)
        for field in self.field_695:
            bib.add_ordered_field(field)
        for field in self.field_7xx:
            bib.add_ordered_field(field)
        bib.add_ordered_field(self.field_901)
        bib.add_ordered_field(self.field_910)
        bib.add_ordered_field(self.field_909)
        # add items
        return bib
