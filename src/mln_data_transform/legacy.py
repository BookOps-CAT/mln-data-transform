import re
from typing import Any


class LegacyBibData:
    """Useful data from a legacy bib record for a MyLibraryNYC Teacher Set."""

    def __init__(
        self,
        bib_id: str,
        item_ids: list[str],
        language: str,
        fixed_fields: list[dict[str, Any]],
        set_title: str,
        var_fields: list[dict[str, Any]],
    ) -> None:
        self.bib_id = bib_id
        self.item_ids = item_ids
        self.fixed_fields = fixed_fields
        self.language = language
        self.set_title = set_title
        self.var_fields = var_fields

    @property
    def isbns(self) -> list[str]:
        isbns = [i for i in self.var_fields if i["marcTag"] == "944"]
        if isbns:
            subfields_944 = isbns[0]["subfields"]
            isbn_string = " ".join([i["content"] for i in subfields_944])
            return isbn_string.split()
        return []

    @property
    def leader(self) -> str | None:
        leader = [i["content"] for i in self.var_fields if not i["marcTag"]]
        if leader:
            return leader[0]
        return None

    @property
    def physical_description(self) -> str | None:
        field_300 = [i for i in self.var_fields if i["marcTag"] == "300"]
        if field_300:
            subfields_300 = field_300[0]["subfields"]
            return " ".join([i["content"] for i in subfields_300])
        return None


class LegacyItemData:
    """Useful data from a legacy item record for a MyLibraryNYC Teacher Set."""

    CALL_NUMBER_PATTERN = re.compile(
        r"Teacher\s*Set\s*(?P<study_program_info>((Art[s]*)|(Math)|(Game[s]*)|(Science)|(Language\s*Arts)|(Social\s*Studies)|([A-Z]{3,4}))(\s*([A-Z]{3}))?)\s+(?P<grade_level>[A-Z]{1,2})\s+(?P<local_set_type>([^\d].+?)?)\s*(?P<shelf_number>\d+)(?:-)?(?P<enumeration>\d+)?$"  # noqa: E501
    )
    AUDIO_PATTERN = re.compile(r"Audio & Digital Devices.+")
    BOOK_CLUB_PATTERN = re.compile(r"Book Club.+")
    GAME_PATTERN = re.compile(r"Game")
    LPRINT_PATTERN = re.compile(r"Large Print")
    PHONIC_PATTERN = re.compile(r"Phonics & Decodeables")
    STORY_PATTERN = re.compile(r"Storytelling")
    TOPIC_PATTERN = re.compile(r"Topic")

    def __init__(self, call_number: str, item_count: int, item_id: str) -> None:
        self.call_number = call_number.strip()
        self.item_count = item_count
        self.item_id = item_id

    @property
    def call_number_components(self) -> re.Match:
        components = self.CALL_NUMBER_PATTERN.match(self.call_number)
        if not components:
            raise ValueError(
                f"Call number '{self.call_number}' does not match pattern. "
                f"Cannot extract components."
            )
        return components

    @property
    def enumeration(self) -> str:
        return self.call_number_components["enumeration"]

    @property
    def grade_level(self) -> str:
        return self.call_number_components["grade_level"]

    @property
    def local_set_type(self) -> str:
        return self.call_number_components["local_set_type"]

    @property
    def shelf_number(self) -> str:
        return self.call_number_components["shelf_number"]

    @property
    def study_program_info(self) -> str:
        return self.call_number_components["study_program_info"]
