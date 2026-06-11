import datetime
import logging
from typing import Any

from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield

from mln_data_transform.components import VarFieldData
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
)

logger = logging.getLogger(__name__)


class TeacherSetBib:
    """A bib record for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        added_entries: list[dict[str, Any]],
        components: list[tuple[str, str]],
        contents_note: str,
        copy_number: int,
        grade_level: GradeReadingLevel,
        language: str,
        physical_description: str,
        pub_dates: list[str],
        record_type: str,
        shelf_number: str,
        study_program_info: SubjectStudyProgram,
        set_title: str,
        set_type: SetTypeFormat,
        copies_of_set: int,
        control_number: str | None = None,
        enhanced: str | None = None,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        subjects: list[VarFieldData] | None = None,
        var_field_data: list[VarFieldData] | None = None,
    ) -> None:
        self.added_entries = added_entries
        self.components = components
        self.contents_note = contents_note
        self.copy_number = copy_number
        self.control_number = control_number
        self.enhanced = enhanced
        self.grade_level = grade_level
        self.language = language
        self.local_genre_term = local_genre_term
        self.local_topic_term = local_topic_term
        self.physical_description = physical_description
        self.pub_dates = pub_dates
        self.record_type = record_type
        self.set_title = set_title
        self.set_type = set_type
        self.shelf_number = shelf_number
        self.study_program_info = study_program_info
        self.subjects = subjects
        self.copies_of_set = copies_of_set
        self.var_field_data = var_field_data

    @property
    def field_001(self) -> Field:
        """Control number field"""
        return Field(tag="001", data=self.control_number)

    @property
    def field_003(self) -> Field:
        """Control number identifier field"""
        return Field(tag="003", data="BookOps")

    @property
    def field_008(self) -> Field:
        """MARC 008 field"""
        today = datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")
        if not self.pub_dates:
            pub_date_str = "nuuuuuuuu"
        else:
            pub_date_str = f"i{self.pub_dates[0]}{self.pub_dates[-1]}"
        date_str = f"{today}{pub_date_str}"
        if self.record_type == "o":
            content = "             | ||"
        else:
            content = "           000 0 "
        return Field(tag="008", data=f"{date_str}xxu{content}{self.language} d")

    @property
    def field_091(self) -> Field:
        """Local MyLibraryNYC call number field"""
        if self.enhanced:
            return Field(
                tag="091",
                indicators=Indicators(" ", " "),
                subfields=[
                    Subfield(code="a", value=f"MLNYC {self.study_program_info.name}"),
                    Subfield(code="f", value=f"{self.set_type.name} {self.enhanced}"),
                    Subfield(code="p", value=self.grade_level.name),
                    Subfield(code="c", value=self.shelf_number),
                ],
            )
        else:
            return Field(
                tag="091",
                indicators=Indicators(" ", " "),
                subfields=[
                    Subfield(code="a", value=f"MLNYC {self.study_program_info.name}"),
                    Subfield(code="f", value=self.set_type.name),
                    Subfield(code="p", value=self.grade_level.name),
                    Subfield(code="c", value=self.shelf_number),
                ],
            )

    @property
    def field_245(self) -> Field:
        """Title Field"""
        return Field(
            tag="245",
            indicators=Indicators("0", "0"),
            subfields=[
                Subfield(code="a", value=f"{self.set_title.strip('.')}."),
                Subfield(
                    code="n", value=f"Copy {self.copy_number} of {self.copies_of_set}"
                ),
            ],
        )

    @property
    def field_300(self) -> Field:
        """Physical description field"""
        return Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.physical_description)],
        )

    @property
    def field_500(self) -> Field:
        """General contents note field"""
        return Field(
            tag="500",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.contents_note)],
        )

    @property
    def field_520(self) -> list[Field]:
        """Summary description note field (REPEATABLE)"""
        return [
            Field(
                tag="520",
                indicators=Indicators(" ", " "),
                subfields=[
                    Subfield(code="3", value=i[0]),
                    Subfield(code="a", value=i[1]),
                ],
            )
            for i in self.components
        ]

    @property
    def field_521(self) -> Field:
        """Reading level field"""
        return Field(
            tag="521",
            indicators=Indicators("2", " "),
            subfields=[Subfield(code="a", value=self.grade_level.value)],
        )

    @property
    def field_526(self) -> Field:
        """Study program information field"""
        return Field(
            tag="526",
            indicators=Indicators("8", " "),
            subfields=[Subfield(code="a", value=self.study_program_info.value)],
        )

    @property
    def field_6xx(self) -> list[Field]:
        """Subject fields (REPEATBLE)"""
        subject_list = []
        subject_set = set()
        if not self.subjects:
            return []
        for subject in self.subjects:
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
                Subfield(code="a", value=self.set_type.value),
                Subfield(code="2", value="bookops"),
            ],
        )

    @property
    def field_691(self) -> list[Field]:
        """Local topic term field (REPEATBLE)"""
        subject_list = []
        if self.local_topic_term:
            for term in self.local_topic_term:
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
        if self.local_genre_term:
            for term in self.local_genre_term:
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
        return [
            Field(
                tag=i["tag"],
                indicators=Indicators(i["ind1"], i["ind2"]),
                subfields=[Subfield(code=j[0], value=j[1]) for j in i["subfields"]],
            )
            for i in self.added_entries
        ]

    @property
    def field_901(self) -> Field:
        """Cataloger's initials field"""
        return Field(
            tag="901",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value="mlnyc-bot"),
                Subfield(code="b", value="CATBL"),
            ],
        )

    @property
    def field_909(self) -> Field:
        """Local OCLC exclusion note field"""
        return Field(
            tag="909",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="OCLC Holdings Exclusion")],
        )

    @property
    def field_910(self) -> Field:
        """Local collection code field"""
        return Field(
            tag="910",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="BL")],
        )

    @property
    def command_line_field(self) -> Field:
        return Field(
            tag="949",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="*b2=8;b3=e;bn=ed;")],
        )

    @property
    def item_fields(self) -> list[Field]:
        """Missing: Funding Source"""
        fields = []
        for comp in self.components:
            for copy in range(0, comp[2]):
                fields.append(
                    Field(
                        tag="949",
                        indicators=Indicators(" ", " "),
                        subfields=[
                            Subfield(code="h", value="10"),
                            Subfield(code="i", value=f"[BARCODE]-{comp[0]}"),
                            Subfield(code="l", value="eduls"),
                            Subfield(code="m", value="m"),
                            Subfield(code="p", value="0.00"),
                            Subfield(code="q", value="30010"),
                            Subfield(code="t", value="252"),
                            Subfield(code="u", value="-"),
                            Subfield(code="v", value="LOGDOE/mlnyc-bot"),
                        ],
                    )
                )
        return fields

    @property
    def var_fields(self) -> list[Field]:
        fields = []
        if not self.var_field_data:
            return []
        for field in self.var_field_data:
            fields.append(
                Field(
                    tag=field.tag,
                    indicators=Indicators(field.ind1, field.ind2),
                    subfields=[
                        Subfield(code=i[0], value=i[1]) for i in field.subfields
                    ],
                )
            )
        return fields

    def add_var_fields(self, bib: Bib) -> None:
        field_tags = [i.tag for i in bib.fields]
        notes_fields = ["500", "520", "521", "526"]
        for field in self.var_fields:
            if field.tag == "901" and [i.code for i in field.subfields] == ["n", "o"]:
                bib.add_ordered_field(field)
            elif field.tag not in field_tags and field.tag in notes_fields:
                field.subfields.append(Subfield(code="x", value="legacy-data"))
                bib.add_ordered_field(field)

    def to_bib(self) -> Bib:
        bib = Bib()
        bib.library = "nypl"
        bib.leader = f"00000n{self.record_type}c  2200000 a 4500"
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
        bib.add_ordered_field(self.field_909)
        bib.add_ordered_field(self.field_910)
        bib.add_ordered_field(self.command_line_field)
        for field in self.item_fields:
            bib.add_ordered_field(field)
        self.add_var_fields(bib)
        return bib
