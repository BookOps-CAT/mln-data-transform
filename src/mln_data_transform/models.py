from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield


class TeacherSetData:
    """A data model for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        leader: str,
        control_number: str,
        begin_pub_date: str | None,
        end_pub_date: str | None,
        language: str,
        call_number: str,
        title: str,
        name_of_part: str,
        physical_description: str,
        contents_note: str,
        detailed_contents_note: str,
        summary: list[str],
        reading_level: str,
        study_program_info: str,
        bib_id: str,
        local_set_type: str,
        local_topic_term: str,
        local_genre_term: str,
        items: list,
        subjects: list[str] | None = None,
    ) -> None:
        """
        Required components of TeacherSet bib records include:

        library
        leader
        control_number
        control_number_identifier
        begin_pub_date
        end_pub_date
        pub_place
        language
        cat_source
        call_number
        title
        name_of_part
        physical_description
        contents_note
        detailed_contents_note
        summary
        reading_level
        study_program_info
        subjects
        local_set_type
        local_topic_term
        local_genre_term
        catalogers_initials
        local_collection_code
        oclc_exclusion_note
        items
        location
        material_type
        bib_code
        """
        self.leader = leader
        self.control_number = control_number
        self.begin_pub_date = begin_pub_date
        self.end_pub_date = end_pub_date
        self.language = language
        self.call_number = call_number
        self.title = title
        self.name_of_part = name_of_part
        self.physical_description = physical_description
        self.contents_note = contents_note
        self.detailed_contents_note = detailed_contents_note
        self.summary = summary
        self.reading_level = reading_level
        self.study_program_info = study_program_info
        self.subjects = subjects
        self.local_set_type = local_set_type
        self.local_topic_term = local_topic_term
        self.local_genre_term = local_genre_term
        self.items = items
        self.bib_id = bib_id

    @property
    def library(self) -> str:
        return "nypl"

    @property
    def control_number_identifier(self) -> str:
        return "BookOps"

    @property
    def pub_place(self) -> str:
        return "xxu"

    @property
    def cat_source(self) -> str:
        return "d"

    @property
    def catalogers_initials(self) -> str:
        return "mlnyc-bot"

    @property
    def local_collection_code(self) -> str:
        return "BL"

    @property
    def oclc_exclusion_note(self) -> str:
        return "OCLC Holdings Exclusion"

    @property
    def location(self) -> str:
        return "ed"

    @property
    def material_type(self) -> str:
        return "8"

    @property
    def bib_code(self) -> str:
        return "e"


class TeacherSetBib:
    """A bib record for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(self, set_data: TeacherSetData) -> None:
        """Components of TeacherSet bib records"""
        self.set_data = set_data

    @property
    def library(self) -> str:
        return "nypl"

    @property
    def leader(self) -> str:
        return "00000nac a22      i 4500"

    @property
    def control_number(self) -> Field:
        return Field(tag="001", data="nn-mlnyc-0000000")

    @property
    def control_number_identifier(self) -> Field:
        return Field(tag="003", data="BookOps")

    # @property
    # def field_008(self) -> Field:
    #     return Field(tag="008", data="")

    # @property
    # def call_number(self) -> Field:
    #     return Field(
    #         tag="091",
    #         indicators=Indicators(" ", " "),
    #         subfields=[Subfield(code="", value=self.set_data.call_number)],
    #     )

    @property
    def title(self) -> Field:
        return Field(
            tag="245",
            indicators=Indicators("0", "0"),
            subfields=[
                Subfield(code="a", value=self.set_data.title),
                Subfield(code="a", value=self.set_data.name_of_part),
            ],
        )

    @property
    def physical_description(self) -> Field:
        return Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.set_data.physical_description)],
        )

    @property
    def note_500(self) -> Field:
        return Field(
            tag="500",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.set_data.contents_note)],
        )

    @property
    def note_521(self) -> Field:
        return Field(
            tag="521",
            indicators=Indicators("2", " "),
            subfields=[Subfield(code="a", value=self.set_data.reading_level)],
        )

    @property
    def note_526(self) -> Field:
        return Field(
            tag="526",
            indicators=Indicators("8", " "),
            subfields=[Subfield(code="a", value=self.set_data.study_program_info)],
        )

    @property
    def subject_690(self) -> Field:
        return Field(
            tag="690",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value=self.set_data.local_topic_term),
                Subfield(code="2", value="bookops"),
            ],
        )

    @property
    def catalogers_initials(self) -> Field:
        return Field(
            tag="901",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=self.set_data.catalogers_initials),
                Subfield(code="b", value="CATBL"),
            ],
        )

    @property
    def local_collection_code(self) -> Field:
        return Field(
            tag="910",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=self.set_data.local_collection_code),
            ],
        )

    @property
    def oclc_exclusion(self) -> Field:
        return Field(
            tag="909",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=self.set_data.oclc_exclusion_note),
            ],
        )

    def to_bib(self) -> Bib:
        bib = Bib()
        bib.library = self.library
        bib.leader = self.leader
        bib.add_field(self.control_number)
        bib.add_field(self.control_number_identifier)
        # add 008
        # add call number
        bib.add_field(self.title)
        bib.add_field(self.physical_description)
        bib.add_field(self.note_500)
        # add detailed contents note
        # add summary
        bib.add_field(self.note_521)
        bib.add_field(self.note_526)
        # add 6xx fields
        bib.add_field(self.subject_690)
        # add local topic
        # add local genre
        bib.add_field(self.catalogers_initials)
        bib.add_field(self.local_collection_code)
        bib.add_field(self.oclc_exclusion)
        # add items
        return bib
