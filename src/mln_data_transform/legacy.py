import re
from typing import Any


class LegacyBibData:
    """Useful data from a legacy bib record for a MyLibraryNYC Teacher Set."""

    COPY_INFO_PATTERN = re.compile(
        r"((\d+|[A-z]+)(?:\s+(?:copy|copies))(\s+of\s+(\d+|[A-z]+))(?:\s+[a-z]+))|(?:(\d\s+)?(([Bb]ookpack)|([Gg]ame)|([Tt]opic\s+[Ss]et)|([Bb]ook\s+[Cc]lub\s+[Ss]et))\s+(-\s+)?)\((?:en [a-z]+\s+)?([A-z0-9\+\.\s]+)(?<!Board Game)\){1}"  # noqa: E501
    )
    SECONDARY_COPY_INFO_PATTERN = re.compile(
        r"((([Vv]ideo\s+)|([Tt]abletop\s+)|([Bb]oard\s+))?[Gg]ame\s+(\([Bb]oard [Gg]ame\)\s+)?- )|([Dd][Vv][Dd] - )"  # noqa: E501
    )

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
    def copy_info(self) -> str:
        fields_5xx = [i for i in self.var_fields if i["marcTag"] in ["500", "520"]]
        matched_notes = []
        for note in fields_5xx:
            content = " ".join([i["content"] for i in note["subfields"]])
            matched = self.COPY_INFO_PATTERN.match(content)
            if matched:
                matched_notes.append(matched[0])
                return matched[0]
        for note in fields_5xx:
            content = " ".join([i["content"] for i in note["subfields"]])
            matched = self.SECONDARY_COPY_INFO_PATTERN.match(content)
            if matched:
                matched_notes.append(matched[0])
                return matched[0]
        raise ValueError(
            f"500 and 520 fields do not match pattern. Cannot extract copy info. "
            f"500 fields: {fields_5xx}. 520 fields: {fields_5xx}"
        )

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

    @property
    def record_type(self) -> str | None:
        if self.leader:
            return self.leader[6]
        return "a"


class LegacyItemData:
    """Useful data from a legacy item record for a MyLibraryNYC Teacher Set."""

    CALL_NUMBER_PATTERN = re.compile(
        r"Teacher\s*Set\s*(?P<subject>((Art[s]*)|(Math)|(Game[s]*)|(Science)|(Language\s*Arts)|(Social\s*Studies)|([A-Z]{3,4}))\s*(?P<lang>([A-Z]{3}))?)\s+(?P<grade_level>[A-Z]{1,2})\s*\s+(?P<set_type>(?P<enhanced>[Ee]nhanced)?([^\d].+?)?)\s*(?P<shelf_number>\d+)(?:-)?(?P<set_copy_number>\d+)?$"  # noqa: E501
    )
    GRADE_LEVEL_MAPPING = {"E": "B", "J": "C", "MG": "D", "YA": "E"}
    SUBJECT_MAPPING = {
        "Language Arts ENG": "ELA",
        "Language Arts": "LA",
        "Arts": "ART",
        "Games": "GAME",
        "Social Studies": "SOC",
        "Science": "SCI",
    }

    def __init__(self, call_number: str, legacy_item_count: int, item_id: str) -> None:
        self.call_number = call_number.strip()
        self.legacy_item_count = legacy_item_count
        self.item_id = item_id

    @property
    def call_number_components(self) -> re.Match:
        """Matches legacy call number str from item record to extract parts."""
        components = self.CALL_NUMBER_PATTERN.match(self.call_number)
        if not components:
            raise ValueError(
                f"Call number '{self.call_number}' does not match pattern. "
                f"Cannot extract components."
            )
        return components

    @property
    def enhanced(self) -> str | None:
        """Extracts 'enhanced' from legacy call number for sets with special formats."""
        if self.call_number_components["enhanced"]:
            return "E"
        return None

    @property
    def grade_level(self) -> str:
        """
        Parses grade level from call number.

        If language is present in call number converts legacy grade level (eg. 'YA')
        to current grade level formatting formatting.
        """
        grade_level = self.call_number_components["grade_level"]
        if self.lang:
            return self.GRADE_LEVEL_MAPPING[grade_level]
        else:
            return grade_level

    @property
    def lang(self) -> str:
        """Parses language from call number if present."""
        return self.call_number_components["lang"]

    @property
    def set_copy_number(self) -> str:
        """Parses copy number for set from legacy item record."""
        return self.call_number_components["set_copy_number"]

    @property
    def set_type(self) -> str:
        """Parses majority of call number string to identify set type."""
        set_type = self.call_number_components["set_type"].casefold()
        if "book club".casefold() in set_type or "BC".casefold() in set_type:
            return "CLUB"
        elif "game" in set_type or "game" in self.subject.casefold():
            return "GAME"
        elif "storytelling" in set_type:
            return "STORY"
        elif "audio" in set_type or ("digital" in set_type and "devices" in set_type):
            return "AUDIO"
        elif "large print".casefold() in set_type:
            return "LPRINT"
        else:
            return "TOPIC"

    @property
    def shelf_number(self) -> str:
        """Extracts shelf number from end of legacy call number"""
        return self.call_number_components["shelf_number"]

    @property
    def subject(self) -> str:
        """Extracts subject from call number to map to study program info."""
        subject = self.call_number_components["subject"]
        if not self.lang and subject not in self.SUBJECT_MAPPING.keys():
            return subject.upper()
        elif subject in self.SUBJECT_MAPPING.keys():
            return self.SUBJECT_MAPPING[subject]
        subject_no_lang = self.SUBJECT_MAPPING[subject.removesuffix(self.lang).strip()]
        if len(subject_no_lang) == 2:
            return f"{self.lang[:2]}{subject_no_lang}"
        return subject_no_lang
