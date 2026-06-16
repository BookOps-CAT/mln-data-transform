from __future__ import annotations

import logging
import re
from functools import cached_property
from typing import Any

from mln_data_transform.components import SetBook, VarFieldData, WorldcatSetPart
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
)
from mln_data_transform.transform import PlatformManager, WorldcatManager
from mln_data_transform.utils import is_valid_isbn, normalize_isbn

logger = logging.getLogger(__name__)


class LegacyTeacherSetData:
    def __init__(self, bib_id: str, platform_manager: PlatformManager) -> None:
        self.platform_manager = platform_manager
        self.bib_id = bib_id
        self.parts = [
            SetBook(isbn=i, copies=self.bib_data.copy_count)
            for i in self.bib_data.isbns
        ]

    @cached_property
    def bib_data(self) -> LegacyBibData:
        bib_data = self.platform_manager.get_platform_bib(self.bib_id)
        return LegacyBibData(
            bib_id=self.bib_id,
            language=bib_data["lang"]["code"],
            set_title=bib_data["title"],
            var_fields=bib_data["varFields"],
        )

    @property
    def copies_of_set(self) -> int:
        return len(self.item_data)

    @cached_property
    def item_data(self) -> list[LegacyItemData]:
        item_data = self.platform_manager.get_platform_bib_items(self.bib_id)
        item_list = []
        for item in item_data:
            barcode = item["barcode"]
            legacy_item = LegacyItemData(
                call_number=item["callNumber"], item_id=item["id"], barcode=barcode
            )
            item_list.append(legacy_item)
        return item_list


class LegacyBibData:
    """Useful data from a legacy bib record for a MyLibraryNYC Teacher Set."""

    COPY_INFO_PATTERN = re.compile(
        r"((?P<copy_count>\d+|[A-z]+)(?:\s+(?:copy|copies))(\s+of\s+(?P<title_count>\d+|[A-z]+))(?:\s+[a-z]+))"
    )  # noqa: E501
    SECONDARY_COPY_INFO_PATTERN = re.compile(
        r"(?:(\d\s+)?(([Gg]ame)|([Tt]opic\s+[Ss]et)|([Bb]ook\s+[Cc]lub\s+[Ss]et))\s+(-\s+)?)\((?:en [a-z]+\s+)?(?P<copy_count>[0-9]+)([A-z0-9\+\.\s]+)(?<!Board Game)\){1}"  # noqa: E501
    )
    SINGLE_ITEM_COPY_INFO_PATTERN = re.compile(
        r"(((([Bb]oard)|([Vv]ideo)|([Tt]abletop))(\s[Gg]ame))|([Gg]ame)|([Dd][Vv][Dd]))(?:\s*\([A-z\s]+\))?(\s*-\s*)"  # noqa: E501
    )
    CALL_NUMBER_PATTERN = re.compile(
        r"Teacher\s*Set\s*(?P<subject>((Art[s]*)|(Math)|(Game[s]*)|(Science)|(Language\s*Arts)|(Social\s*Studies)|([A-Z]{3,4}))\s*(?P<lang>([A-Z]{3}))?)\s+(?P<grade_level>[A-Z]{1,2})\s*\s+(?P<set_type>(?P<enhanced>[Ee]nhanced)?([^\d].+?)?)\s*(\d+)(?:-)?(\d+)?$"  # noqa: E501
    )
    GRADE_LEVEL_MAPPING = {"E": "B", "J": "C", "MG": "D", "YA": "E"}
    SUBJECT_MAPPING = {
        "Language Arts ENG": "ELA",
        "Language Arts SPA": "SPLA",
        "Language Arts FRE": "SPLA",
        "Language Arts CHI": "CHLA",
        "Arts": "ART",
        "Math": "MAT",
        "Games": "GAME",
        "Social Studies": "SOC",
        "Science": "SCI",
    }
    DIGITS = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    def __init__(
        self,
        bib_id: str,
        language: str,
        set_title: str,
        var_fields: list[dict[str, Any]],
    ) -> None:
        self.bib_id = bib_id
        self.language = language
        self.set_title = set_title
        self.var_fields = [
            i
            for i in var_fields
            if i["marcTag"] not in ["901", "904", "908", "909", "910", "949"]
        ]

    @property
    def call_number(self) -> str:
        field_091 = [i for i in self.var_fields if i["marcTag"] == "091"]
        subfields_091 = field_091[0]["subfields"]
        return " ".join([i["content"] for i in subfields_091])

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
    def copy_count(self) -> int | None:
        fields = [i for i in self.var_fields if i["marcTag"] in ["500", "520"]]
        fields_5xx = [" ".join([i["content"] for i in j["subfields"]]) for j in fields]
        for content in fields_5xx:
            matched = self.COPY_INFO_PATTERN.match(content)
            if matched:
                copy_count = matched["copy_count"].casefold()
                if copy_count.isalpha():
                    copy_count = self.DIGITS[copy_count]
                return int(copy_count)

        for content in fields_5xx:
            matched = self.SINGLE_ITEM_COPY_INFO_PATTERN.match(content)
            if matched:
                return 1
        return None

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
    def isbns(self) -> list[str]:
        isbns = [i for i in self.var_fields if i["marcTag"] == "944"]
        if isbns:
            subfields_944 = isbns[0]["subfields"]
            isbn_string = " ".join([i["content"] for i in subfields_944])
            isbn_list = isbn_string.split()
            return [normalize_isbn(i) for i in isbn_list if is_valid_isbn(i)]
        return []

    @property
    def lang(self) -> str:
        """Parses language from call number if present."""
        return self.call_number_components["lang"]

    @property
    def physical_description(self) -> str | None:
        field_300 = [i for i in self.var_fields if i["marcTag"] == "300"]
        if field_300:
            subfields_300 = field_300[0]["subfields"]
            return " ".join([i["content"] for i in subfields_300]).replace(
                "v.", "item(s)"
            )
        return None

    @property
    def record_type(self) -> str:
        for field in self.var_fields:
            if not field["marcTag"]:
                return field["content"][6]
        return "a"

    @property
    def set_type(self) -> str:
        """Parses majority of call number string to identify set type."""
        set_type = self.call_number_components["set_type"].casefold()
        if (
            "book club".casefold() in set_type
            or "BC".casefold() in set_type
            or "club".casefold() in set_type
        ):
            return "CLUB"
        elif "game" in set_type or "game" in self.subject.casefold():
            return "GAME"
        elif "storytelling" in set_type:
            return "STORY"
        elif "audio" in set_type or ("digital" in set_type and "devices" in set_type):
            return "AUDIO"
        elif "lprint".casefold() in set_type or (
            "large".casefold() in set_type and "print".casefold() in set_type
        ):
            return "LPRINT"
        else:
            return "TOPIC"

    @property
    def subject(self) -> str:
        """Extracts subject from call number to map to study program info."""
        subject = self.call_number_components["subject"]
        if subject in self.SUBJECT_MAPPING.keys():
            return self.SUBJECT_MAPPING[subject]
        elif self.lang and subject.removesuffix(self.lang).strip() == "Language Arts":
            return "WorldLang"
        else:
            return subject.upper()


class LegacyItemData:
    """Useful data from a legacy item record for a MyLibraryNYC Teacher Set."""

    def __init__(self, barcode: str, call_number: str, item_id: str) -> None:
        self.barcode = barcode
        self.call_number = call_number.strip()
        self.item_id = item_id

    @property
    def bib_call_number(self) -> str:
        """Removes enumeration from end of item call number for validation."""
        if self.call_number[-3] == "-":
            return self.call_number[:-3]
        else:
            return self.call_number[:-2]


class LegacyTeacherSet:
    def __init__(self, set_data: LegacyTeacherSetData) -> None:
        self._set_data = set_data
        self.bib_id = self._set_data.bib_id
        self.legacy_call_number = self._set_data.bib_data.call_number.strip()

        self.copies_of_set = self._set_data.copies_of_set
        self.enhanced = self._set_data.bib_data.enhanced
        self.grade_level = GradeReadingLevel[self._set_data.bib_data.grade_level]
        self.language = self._set_data.bib_data.language
        self.local_genre_term = None
        self.local_topic_term = None
        self.physical_description = (
            self._set_data.bib_data.physical_description
            if self._set_data.bib_data.physical_description
            else f"{sum([i.copies for i in self.parts])} items"
        )
        self.record_type = self._set_data.bib_data.record_type
        self.set_title = self._set_data.bib_data.set_title
        self.set_type = SetTypeFormat[self._set_data.bib_data.set_type]
        self.study_program_info = SubjectStudyProgram[self._set_data.bib_data.subject]
        self.var_fields = self._set_data.bib_data.var_fields

    @property
    def contents_note(self) -> str:
        part_list = []
        for part in self.parts:
            if part.copies > 1:
                copy_part = " copies of "
            else:
                copy_part = " copy of "
            part_list.append(
                "".join(
                    [str(part.copies), copy_part, '"', part.title.strip("."), '", ']
                )
            )
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @property
    def legacy_barcodes(self) -> dict[str, str]:
        return {i.barcode: i.call_number for i in self._set_data.item_data}

    @cached_property
    def parts(self) -> list[WorldcatSetPart]:
        parts = []
        data_parts = self._set_data.parts
        logger.info(f"Record contains {len(data_parts)} ISBN(s) to query WorldCat.")
        with WorldcatManager() as manager:
            for part in data_parts:
                worldcat_part = manager.get_worldcat_data_for_part(isbn=part.isbn)
                parts.append(
                    WorldcatSetPart(
                        isbn=part.isbn,
                        title=worldcat_part.title,
                        author=worldcat_part.author_name,
                        author_dates=worldcat_part.author_dates,
                        pub_date=worldcat_part.pub_date,
                        description=worldcat_part.description,
                        copies=part.copies,
                        subjects=worldcat_part.subjects,
                    )
                )
        return parts

    @property
    def var_field_data(self) -> list[VarFieldData]:
        fields = []
        for field in self.var_fields:
            if field.get("subfields"):
                subfields = [(i["tag"], i["content"]) for i in field["subfields"]]
                fields.append(
                    VarFieldData(
                        tag=field["marcTag"],
                        ind1=field["ind1"],
                        ind2=field["ind2"],
                        subfields=subfields,
                    )
                )
        return fields
