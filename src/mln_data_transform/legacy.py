from __future__ import annotations

import logging
import re
from enum import StrEnum
from itertools import zip_longest
from typing import Any

from mln_data_transform.components import SetBook, VarFieldData, WorldcatSetPart
from mln_data_transform.taxonomy import (
    GENRE_REGEX_MAP,
    TOPIC_REGEX_MAP,
    ComponentFormat,
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.transform import PlatformManager, WorldcatManager
from mln_data_transform.utils import is_valid_isbn, is_valid_upc, normalize_isbn

logger = logging.getLogger(__name__)


class LegacyBibData:
    """Useful data from a legacy bib record for a MyLibraryNYC Teacher Set."""

    GENERAL_COPY_INFO_PATTERN = re.compile(
        r"^((([Tt]opic)|([Bb]ook [Cc]lub))( [Ss]et)? \()? ?(((\d+|\b\w+\b)(?:\s+(?:copy|copies))(\s+of\s+))?(\d+|\b\w+\b))(?:\s+\b(?![Bb]ookpack\b)\w+\b)((?: \+ )((\d+)|(\b\w+\b)) (\d+|(\b\w+\b\s?)+)((?:\+ )((\d+)|([A-z]+)) (\d+|(\b\w+\b\s?)+))?)?"  # noqa: E501
    )
    PRIMARY_COPY_INFO_PATTERN = re.compile(
        r"^(?![Tt]opic)(?![Bb]ook [Cc]lub)(((?P<copy_count>\d+|\b\w+\b)(?:\s+(?:copy|copies))(\s+of\s+))?(?P<title_count>\d+|\b\w+\b))(?:\s+\b(?![Bb]ookpack\b)\w+\b)((?: \+ )(?P<enhanced_item_count_1>(\d+)|(\b\w+\b)) (?P<enhanced_item_type_1>\d+|(\b\w+\b\s?)+)((?:\+ )(?P<enhanced_item_count_2>(\d+)|([A-z]+)) (?P<enhanced_item_type_2>\d+|(\b\w+\b\s?)+))?)?"  # noqa: E501
    )
    BOOK_CLUB_COPY_INFO_PATTERN = re.compile(
        r"^(?:[Bb]ook [Cc]lub( [Ss]et)? \() ?(?P<copy_count>(\d+)|\b\w+\b)(?:\s+\b\w+\b)((?: \+ )(?P<enhanced_item_count_1>(\d+)|(\b\w+\b)) (?P<enhanced_item_type_1>\d+|(\b\w+\b\s?)+)((?:\+ )(?P<enhanced_item_count_2>(\d+)|([A-z]+)) (?P<enhanced_item_type_2>\d+|(\b\w+\b\s?)+))?)?"  # noqa: E501
    )
    MINIMAL_COPY_INFO_PATTERN = re.compile(r"^(?P<copy_count>\d{1,2})\s?v\.$")
    TOPIC_SET_COPY_INFO_PATTERN = re.compile(
        r"^(?:[Tt]opic( [Ss]et)? \() ?(?P<title_count>(\d+)|\b\w+\b)(?:\s+\b\w+\b)((?: \+ )(?P<enhanced_item_count_1>(\d+)|(\b\w+\b)) (?P<enhanced_item_type_1>\d+|(\b\w+\b\s?)+)((?:\+ )(?P<enhanced_item_count_2>(\d+)|([A-z]+)) (?P<enhanced_item_type_2>\d+|(\b\w+\b\s?)+))?)?"  # noqa: E501
    )
    CALL_NUMBER_PATTERN = re.compile(
        r"Teacher\s*Set\s*(?P<subject>((Art[s]*)|(Math)|(Game[s]*)|(Education)|(Science)|(Language\s*Arts)|(Social\s*Studies)|([A-Z]{3,4}))\s*(?P<lang>([A-Z]{3}))?)\s+(?P<grade_level>[A-Z]{1,2})\s*\s+(?P<set_type>(?P<enhanced>[Ee]nhanced)?([^\d].+?)?)\s*(\d+)(?:-)?(\d+)?$"  # noqa: E501
    )
    ALT_CALL_NUMBER_PATTERN = re.compile(
        r"Teacher\s*Set\s*(?: Assorted )?(?P<subject>((Art[s]*)|(Math)|(Game[s]*)|(Science)|(Education)|(Language\s*Arts)|(Social\s*Studies)|([A-z]{3,4}( (eng)|(spa)|(fre)|(chi))?))\s*)\s+(?P<set_type>(?P<enhanced>[Ee]nhanced)?([^\d].+?)?)\s*(\d+)(?:-)?(\d+)?$"  # noqa: E501
    )
    GRADE_LEVEL_MAPPING = {"E": "B", "J": "C", "MG": "D", "YA": "E"}
    SUBJECT_MAPPING = {
        "Language Arts ENG": "ELA",
        "Language Arts SPA": "SPLA",
        "Language Arts FRE": "SPLA",
        "Language Arts CHI": "CHLA",
        "Language Arts": "ELA",
        "Arts": "ART",
        "ARTS": "ART",
        "Math": "MAT",
        "MATH": "MAT",
        "Games": "GAME",
        "Social Studies": "SOC",
        "Science": "SCI",
        "ELA ENG": "ELA",
        "ELA SPA": "SPLA",
        "ELA FRE": "FRLA",
        "ELA CHI": "CHLA",
        "ENG": "ELA",
        "SPA": "SPLA",
        "FRE": "FRLA",
        "CHI": "CHLA",
        "Education": "PDE",
        "EDU": "PDE",
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
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
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
        return " ".join([i["content"] for i in subfields_091]).strip()

    @property
    def call_number_components(self) -> re.Match:
        """Matches legacy call number str from item record to extract parts."""
        components = self.CALL_NUMBER_PATTERN.match(self.call_number)
        if not components:
            components = self.ALT_CALL_NUMBER_PATTERN.match(self.call_number)
        if not components:
            raise ValueError(
                f"Call number '{self.call_number}' does not match pattern. "
                f"Cannot extract components."
            )
        return components

    @property
    def copy_info_field(self) -> str:
        fields = [i for i in self.var_fields if i["marcTag"] in ["500", "505", "520"]]
        fields_5xx = []
        for field in fields:
            content = [
                i["content"]
                for i in field["subfields"]
                if i["content"][0].isnumeric()
                or i["content"].split()[0].lower() in self.DIGITS.keys()
            ]
            fields_5xx.extend(content)
        for field in fields_5xx:
            matched = self.GENERAL_COPY_INFO_PATTERN.match(field)
            if matched:
                return field
        if self.set_type == "CLUB":
            for field in fields_5xx:
                matched = self.MINIMAL_COPY_INFO_PATTERN.match(field)
                if matched:
                    return field
        fields = [i for i in self.var_fields if i["marcTag"] in ["500", "505", "520"]]
        fields_5xx = []
        for field in fields:
            content = [
                i["content"]
                for i in field["subfields"]
                if i["content"].lower().startswith("topic")
                or i["content"].lower().startswith("book club")
            ]
            fields_5xx.extend(content)
        for field in fields_5xx:
            matched = self.GENERAL_COPY_INFO_PATTERN.match(field)
            if matched:
                return field
        if self.set_type == "CLUB":
            for field in fields_5xx:
                matched = self.MINIMAL_COPY_INFO_PATTERN.match(field)
                if matched:
                    return field
        raise ValueError(f"Copy info pattern does not match for {self.bib_id}.")

    @property
    def copy_info_components(self) -> re.Match:
        matched = self.PRIMARY_COPY_INFO_PATTERN.match(self.copy_info_field)
        if matched:
            return matched
        bookclub_match = self.BOOK_CLUB_COPY_INFO_PATTERN.match(self.copy_info_field)
        if bookclub_match:
            return bookclub_match
        topic_match = self.TOPIC_SET_COPY_INFO_PATTERN.match(self.copy_info_field)
        if topic_match:
            return topic_match
        minimal_match = self.MINIMAL_COPY_INFO_PATTERN.match(self.copy_info_field)
        if minimal_match:
            return minimal_match
        raise ValueError(f"Copy info pattern does not match for {self.bib_id}.")

    @property
    def copy_count(self) -> int:
        if "copy_count" not in self.copy_info_components.groupdict():
            return 1
        copy_count = self.copy_info_components["copy_count"]
        if copy_count.isalpha():
            copy_count = self.DIGITS[copy_count.casefold()]
        return int(copy_count)

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
        grade_level = [i for i in self.var_fields if i["marcTag"] == "521"]
        if grade_level:
            subfields_521 = grade_level[0]["subfields"]
            grade_level_string = " ".join([i["content"].strip() for i in subfields_521])
            matches = self.map_to_closest_enum(grade_level_string)
            return matches
        grade_level = self.call_number_components["grade_level"]
        if self.lang:
            return self.GRADE_LEVEL_MAPPING[grade_level]
        else:
            return grade_level

    @property
    def ids(self) -> list[str]:
        ids = [i for i in self.var_fields if i["marcTag"] == "944"]
        if ids:
            id_string = " ".join([i["content"] for i in ids[0]["subfields"]])
            id_list = [normalize_isbn(i) for i in id_string.split()]
            validated_ids = [i for i in id_list if is_valid_isbn(i) or is_valid_upc(i)]
            if len(validated_ids) < len(id_list):
                errors = [i for i in id_list if i not in validated_ids]
                raise ValueError(
                    f"({self.bib_id}) Record contains {len(id_list)} ISBN/UPC(s). "
                    f"{len(errors)}/{len(id_list)} are invalid: {errors}"
                )
            return id_list
        if self.title_fields and not ids:
            return []
        raise ValueError(f"({self.bib_id}) Record does not contain ISBNs.")

    @property
    def title_fields(self) -> list[str]:
        title_list = []
        if self.title_count == 1 and self.set_type == "CLUB":
            return [self.set_title.split("by")[0]]
        for field in self.var_fields:
            if field["marcTag"] == "505":
                subfields = [
                    i["content"] for i in field["subfields"] if i["tag"] in ["a", "t"]
                ]
                title_list.extend(subfields)
        if len(title_list) == 1:
            return [
                i.strip() for i in title_list[0].split("--") if "--" in title_list[0]
            ]
        return []

    @property
    def lang(self) -> str | None:
        """Parses language from call number if present."""
        if "lang" in self.call_number_components.groupdict():
            return self.call_number_components["lang"]

    @property
    def physical_description(self) -> str | None:
        field_300 = [i for i in self.var_fields if i["marcTag"] == "300"]
        if field_300:
            subfields_300 = field_300[0]["subfields"]
            phys_desc = (
                " ".join([i["content"] for i in subfields_300])
                .replace("v.", " item(s)")
                .replace("  ", " ")
            )
            if phys_desc.isnumeric():
                return f"{phys_desc} item(s)"
            return phys_desc
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
        if "game" in set_type or "game" in self.subject.casefold():
            return "GAME"
        elif "storytelling" in set_type:
            return "STORY"
        elif "audio" in set_type or ("digital" in set_type and "devices" in set_type):
            return "AUDIO"
        elif "lprint".casefold() in set_type or (
            "large".casefold() in set_type and "print".casefold() in set_type
        ):
            return "LPRINT"
        elif (
            "book club".casefold() in set_type
            or "BC".casefold() in set_type
            or "club".casefold() in set_type
        ):
            return "CLUB"
        else:
            return "TOPIC"

    @property
    def special_formats(self) -> list[tuple[str, int]] | None:
        if (
            "enhanced_item_count_1" not in self.copy_info_components.groupdict()
            or not self.copy_info_components["enhanced_item_count_1"]
        ):
            return None
        enhanced_types = {
            "playaway": re.compile(r"playaway", re.IGNORECASE),
            "lprint": re.compile(r"large[ ]?print", re.IGNORECASE),
            "dvd": re.compile(r"dvd", re.IGNORECASE),
        }
        out = []
        item_type_1 = self.copy_info_components["enhanced_item_type_1"]
        for item_type, regex in enhanced_types.items():
            match = regex.match(item_type_1)
            if match:
                out.append(
                    (item_type, int(self.copy_info_components["enhanced_item_count_1"]))
                )

        item_type_2 = self.copy_info_components["enhanced_item_type_2"]
        if not item_type_2:
            return out
        for item_type, regex in enhanced_types.items():
            match = regex.match(item_type_2)
            if match:
                out.append(
                    (item_type, int(self.copy_info_components["enhanced_item_count_2"]))
                )
        return out

    @property
    def subject(self) -> str:
        """Extracts subject from call number to map to study program info."""
        subject = self.call_number_components["subject"]
        if subject in self.SUBJECT_MAPPING.keys():
            return self.SUBJECT_MAPPING[subject]
        elif self.lang and subject.removesuffix(self.lang).strip() == "Language Arts":
            return "WorldLang"
        elif (
            self.lang
            and subject.removesuffix(self.lang).strip() in self.SUBJECT_MAPPING
        ):
            return self.SUBJECT_MAPPING[subject.removesuffix(self.lang).strip()]
        else:
            return subject.upper()

    @property
    def title_count(self) -> int:
        if "title_count" not in self.copy_info_components.groupdict():
            return 1
        title_count = self.copy_info_components["title_count"]
        if title_count.isalpha():
            title_count = self.DIGITS[title_count.casefold()]
        return int(title_count)

    def map_to_closest_enum(self, grade_str: str) -> str:
        """Applies explicit overrides, then falls back to Euclidean distance."""
        clean_str = grade_str.strip(".")
        if clean_str in ["1-12", "k-12", "K-12"]:
            return "E"
        if clean_str.startswith(("0", "Pre")):
            return "A"
        if clean_str.startswith("K") or clean_str.endswith(("-2", "-3")):
            return "B"
        match = re.match(r"^(\d{1,2})\-(\d{1,2})$", clean_str)
        start, end = match.groups()
        start = int(start)
        end = int(end)
        best_match = None
        min_distance = float("inf")
        bounds = {"C": (3, 5), "D": (6, 8), "E": (9, 12)}
        for enum_val, (enum_start, enum_end) in bounds.items():
            distance = (start - enum_start) ** 2 + (end - enum_end) ** 2

            if distance < min_distance:
                min_distance = distance
                best_match = enum_val

        return best_match


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
            f"({self.bib_id}) Retrieved bib and "
            f"{len(item_data)} item record(s) from platform."
        )
        for n, item in enumerate(item_data):
            if item["status"]["code"] not in ["-", "k"]:
                continue
            legacy_item = LegacyItemData(
                call_number=item["callNumber"],
                item_id=item["id"],
                barcode=item["barcode"],
            )
            item_list.append(legacy_item)
        if not item_list:
            raise ValueError(f"({self.bib_id}) Item status issue.")
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
        cls, bib_data: LegacyBibData, item_data: list[LegacyItemData]
    ) -> "LegacyTeacherSetData":
        zipped_ids = list(zip_longest(bib_data.ids, bib_data.title_fields))
        if not bib_data.special_formats:
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
                    {
                        "id": i[0],
                        "copies": bib_data.copy_count,
                        "title": i[1],
                        "format": "book",
                    }
                    for i in zipped_ids
                ],
                set_title=bib_data.set_title,
                set_type=bib_data.set_type,
                study_program_info=bib_data.subject,
                var_fields=bib_data.var_fields,
            )
        book_ids = zipped_ids[: bib_data.title_count]
        other_ids = zipped_ids[bib_data.title_count :]
        parts = [
            {"id": i[0], "title": i[1], "copies": bib_data.copy_count, "format": "book"}
            for i in book_ids
        ]
        if len(other_ids) < sum([i[1] for i in bib_data.special_formats]):
            added = [(None, None)] * (
                sum([i[1] for i in bib_data.special_formats]) - len(other_ids)
            )

            other_ids = other_ids + added
        zipped_items = [
            (format, count, id, title)
            for (format, count), (id, title) in zip(bib_data.special_formats, other_ids)
        ]
        for item in zipped_items:
            parts.append(
                {"format": item[0], "copies": item[1], "id": item[2], "title": item[3]}
            )
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
            set_parts=parts,
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
            for n, part in enumerate(self.set_parts):
                if part.id:
                    worldcat_part = manager.get_worldcat_data_for_part(
                        id=part.id, index="sn", format=part.format, title=part.title
                    )
                elif not part.id and part.title:
                    worldcat_part = manager.get_worldcat_data_for_part(
                        id=part.title, index="ti", format=part.format
                    )
                else:
                    raise ValueError(
                        f"Item {n + 1} of {len(self.set_parts)} missing ID ({part})."
                    )
                part.id = worldcat_part["id"]
                worldcat_part.update(
                    {"id": part.id, "format": part.format, "copies": part.copies}
                )
                parts.append(worldcat_part)
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
            title = part.title.strip(".")
            if part.format != "book":
                title = f"{title} [{part.format}]"
            part_list.append("".join([str(part.copies), copy_part, '"', title, '", ']))
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @property
    def local_genre_term(self) -> list[TaxonomyGenre]:
        genre_terms = []
        for subject in self.subject_strings:
            close_matches = self.compare_terms(term=subject, regex_map=GENRE_REGEX_MAP)
            for genre in close_matches:
                genre_terms.append(genre)
        title_matches = self.compare_terms(
            term=self.set_title, regex_map=GENRE_REGEX_MAP
        )
        call_num_matches = self.compare_terms(
            term=self.call_number, regex_map=GENRE_REGEX_MAP
        )
        for genre in call_num_matches + title_matches:
            genre_terms.append(genre)
        return list(set(genre_terms))

    @property
    def local_topic_term(self) -> list[TaxonomyTopic]:
        topic_terms = []
        for subject in self.subject_strings:
            close_matches = self.compare_terms(term=subject, regex_map=TOPIC_REGEX_MAP)
            for topic in close_matches:
                topic_terms.append(topic)
        title_matches = self.compare_terms(
            term=self.set_title, regex_map=TOPIC_REGEX_MAP
        )
        call_num_matches = self.compare_terms(
            term=self.call_number, regex_map=TOPIC_REGEX_MAP
        )
        for topic in call_num_matches + title_matches:
            topic_terms.append(topic)
        return list(set(topic_terms))

    @property
    def parts(self) -> list[WorldcatSetPart]:
        parts = []
        for worldcat_part in self.worldcat_parts:
            parts.append(
                WorldcatSetPart(
                    id=worldcat_part["id"],
                    title=worldcat_part["title"],
                    author=worldcat_part.get("author_name"),
                    author_dates=worldcat_part.get("author_dates"),
                    pub_date=worldcat_part.get("pub_date"),
                    description=worldcat_part["description"],
                    copies=worldcat_part["copies"],
                    subjects=worldcat_part.get("subjects", []),
                    format=ComponentFormat[worldcat_part["format"]],
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

    def compare_terms(self, term: str, regex_map: dict) -> list[StrEnum]:
        matched_terms = []
        for taxonomy_item, pattern in regex_map.items():
            if pattern.search(term):
                matched_terms.append(taxonomy_item)

        return matched_terms
