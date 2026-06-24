from __future__ import annotations

import difflib
import logging
import re
from typing import Any

from mln_data_transform.components import SetBook, VarFieldData, WorldcatSetPart
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.transform import PlatformManager, WorldcatManager
from mln_data_transform.utils import is_valid_isbn, normalize_isbn

logger = logging.getLogger(__name__)


class LegacyBibData:
    """Useful data from a legacy bib record for a MyLibraryNYC Teacher Set."""

    COPY_INFO_PATTERN = re.compile(
        r"((?P<copy_count>\d+|[A-z]+)(?:\s+(?:copy|copies))(\s+of\s+(?P<title_count>\d+|[A-z]+))(?:\s+[a-z]+))"
    )  # noqa: E501
    SECONDARY_COPY_INFO_PATTERN = re.compile(
        r"(?:(\d\s+)?((game)|(topic\s+[Ss]et)|(book\s+club\s+set))\s+(-\s+)?)\((?:en [a-z]+\s+)?(?P<copy_count>[0-9]+)([A-z0-9\+\.\s]+)(?<!Board Game)\){1}",  # noqa: E501
        re.IGNORECASE,
    )
    SINGLE_ITEM_COPY_INFO_PATTERN = re.compile(
        r"((((board)|(video)|(tabletop))(\sgame))|(game)|(dvd))(?:\s*\([A-z\s]+\))?(\s*-\s*)",  # noqa: E501
        re.IGNORECASE,
    )
    CALL_NUMBER_PATTERN = re.compile(
        r"Teacher\s*Set\s*(?P<subject>((Art[s]*)|(Math)|(Game[s]*)|(Science)|(Language\s*Arts)|(Social\s*Studies)|([A-Z]{3,4}))\s*(?P<lang>([A-Z]{3}))?)\s+(?P<grade_level>[A-Z]{1,2})\s*\s+(?P<set_type>(?P<enhanced>enhanced)?([^\d].+?)?)\s*(\d+)(?:-)?(\d+)?$",  # noqa: E501
        re.IGNORECASE,
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
    def copy_count(self) -> int:
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
        return 1

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


class LegacySetStub:
    def __init__(self, bib_id: str) -> None:
        self.bib_id = bib_id

    def get_bib_data(self) -> LegacyBibData:
        manager = PlatformManager()
        bib_data = manager.get_platform_bib(self.bib_id)
        logger.debug(f"({self.bib_id}) Bib record retrieved from platform.")
        return LegacyBibData(
            bib_id=self.bib_id,
            language=bib_data["lang"]["code"],
            set_title=bib_data["title"],
            var_fields=bib_data["varFields"],
        )

    def get_item_data(self) -> list[LegacyItemData]:
        item_list = []
        manager = PlatformManager()
        item_data = manager.get_platform_bib_items(self.bib_id)
        logger.debug(
            f"({self.bib_id}) {len(item_data)} item record(s) retrieved from platform."
        )
        for item in item_data:
            barcode = item["barcode"]
            legacy_item = LegacyItemData(
                call_number=item["callNumber"], item_id=item["id"], barcode=barcode
            )
            item_list.append(legacy_item)
        return item_list


class LegacyTeacherSetData:
    def __init__(
        self,
        bib_id: LegacyBibData,
        copies_of_set: int,
        enhanced: str | None,
        grade_level: str,
        language: str,
        legacy_barcodes: dict[str, str],
        set_parts: list[dict[str, str]],
        physical_description: str,
        call_number: str,
        record_type: str,
        set_title: str,
        set_type: str,
        study_program_info: str,
        var_fields: list[VarFieldData],
    ) -> None:
        self.bib_id = bib_id
        self.copies_of_set = copies_of_set
        self.enhanced = enhanced
        self.grade_level = grade_level
        self.language = language
        self.legacy_barcodes = legacy_barcodes
        self.call_number = call_number
        self.physical_description = physical_description
        self.record_type = record_type
        self.set_parts = [SetBook(**i) for i in set_parts]
        self.set_title = set_title
        self.set_type = set_type
        self.study_program_info = study_program_info
        self.var_fields = var_fields

    @classmethod
    def from_bib_item_data(
        cls, bib_data: LegacyBibData, item_data: LegacyItemData
    ) -> "LegacyTeacherSetData":
        return LegacyTeacherSetData(
            bib_id=bib_data.bib_id,
            copies_of_set=len(item_data),
            enhanced=bib_data.enhanced,
            grade_level=bib_data.grade_level,
            language=bib_data.language,
            legacy_barcodes={i.barcode: i.call_number for i in item_data},
            call_number=bib_data.call_number.strip(),
            physical_description=bib_data.physical_description,
            record_type=bib_data.record_type,
            set_parts=[
                {"isbn": i, "copies": bib_data.copy_count} for i in bib_data.isbns
            ],
            set_title=bib_data.set_title,
            set_type=bib_data.set_type,
            study_program_info=bib_data.subject,
            var_fields=bib_data.var_fields,
        )

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

    def get_worldcat_data_for_parts(self) -> list[dict[str, Any]]:
        parts = []
        with WorldcatManager() as manager:
            for part in self.set_parts:
                worldcat_part = manager.get_worldcat_data_for_part(isbn=part.isbn)
                parts.append(worldcat_part.to_dict())
        return parts


class LegacyTeacherSet:
    def __init__(
        self, set_data: LegacyTeacherSetData, worldcat_parts: list[dict[str, Any]]
    ) -> None:
        self.bib_id = set_data.bib_id
        self.call_number = set_data.call_number
        self.legacy_barcodes = set_data.legacy_barcodes
        self.copies_of_set = set_data.copies_of_set
        self.enhanced = set_data.enhanced
        self.grade_level = GradeReadingLevel[set_data.grade_level]
        self.language = set_data.language
        self.physical_description = (
            set_data.physical_description
            if set_data.physical_description
            else f"{sum([i.copies for i in self.parts])} items"
        )
        self.record_type = set_data.record_type
        self.set_parts = set_data.set_parts
        self.set_title = set_data.set_title
        self.set_type = SetTypeFormat[set_data.set_type]
        self.study_program_info = SubjectStudyProgram[set_data.study_program_info]
        self.var_field_data = set_data.var_field_data
        self.worldcat_parts = worldcat_parts

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
    def local_genre_term(self) -> list[TaxonomyGenre]:
        genre_terms = []
        choices = [
            i.value for i in TaxonomyGenre if i.value not in ["Fiction", "Nonfiction"]
        ]
        for subject in self.subject_strings:
            close_matches = difflib.get_close_matches(subject, choices)
            for genre in close_matches:
                genre_terms.append(genre)
            if "nonfiction".casefold() not in subject and (
                "fiction".casefold() in subject or "literature".casefold() in subject
            ):
                genre_terms.append("Fiction")
            elif "nonfiction".casefold() in subject:
                genre_terms.append("Nonfiction")
        call_num_matches = difflib.get_close_matches(self.call_number, choices)
        for genre in call_num_matches:
            genre_terms.append(genre)
        return list(set([TaxonomyGenre(i) for i in genre_terms]))

    @property
    def local_topic_term(self) -> list[TaxonomyTopic]:
        topic_terms = []
        choices = [i.value for i in TaxonomyTopic]
        for subject in self.subject_strings:
            close_matches = difflib.get_close_matches(subject, choices)
            for topic in close_matches:
                topic_terms.append(topic)
        call_num_matches = difflib.get_close_matches(self.call_number, choices)
        for topic in call_num_matches:
            topic_terms.append(topic)
        return list(set([TaxonomyTopic(i) for i in topic_terms]))

    @property
    def parts(self) -> list[WorldcatSetPart]:
        parts = []
        parts_dict = {i.isbn: i.copies for i in self.set_parts}
        for worldcat_part in self.worldcat_parts:
            parts.append(
                WorldcatSetPart(
                    isbn=worldcat_part["isbn"],
                    title=worldcat_part["title"],
                    author=worldcat_part["author_name"],
                    author_dates=worldcat_part["author_dates"],
                    pub_date=worldcat_part["pub_date"],
                    description=worldcat_part["description"],
                    copies=parts_dict[worldcat_part["isbn"]],
                    subjects=worldcat_part["subjects"],
                )
            )
        return parts

    @property
    def subject_strings(self) -> list[str]:
        subjects = []
        for part in self.parts:
            if part.subjects:
                part_subjects = part.subjects
                for subject in part_subjects:
                    subjects.append(
                        " ".join([i[1] for i in subject["subfields"] if i[0].isalpha()])
                    )
        return subjects
