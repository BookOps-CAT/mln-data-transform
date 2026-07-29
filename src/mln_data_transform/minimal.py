from __future__ import annotations

import datetime
import logging
import re
from enum import StrEnum
from itertools import zip_longest
from typing import Any

from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield

from mln_data_transform.components import SetBook, VarFieldData, WorldcatSetPart
from mln_data_transform.legacy import LegacyItemData
from mln_data_transform.taxonomy import (
    GENRE_REGEX_MAP,
    TOPIC_REGEX_MAP,
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.transform import PlatformManager, WorldcatManager
from mln_data_transform.utils import map_to_closest_grade_enum, normalize_isbn

logger = logging.getLogger(__name__)


class MinimalLegacyBibData:
    def __init__(
        self,
        bib_id: str,
        language: str,
        set_title: str,
        subject: str,
        var_fields: list[dict[str, Any]],
    ) -> None:
        self.bib_id = bib_id
        self.language = language
        self.set_title = set_title
        self.subject = subject
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
    def enhanced(self) -> str | None:
        if "enhanced" in self.call_number.lower():
            return "E"

    @property
    def copy_info_field(self) -> str:
        fields = [i for i in self.var_fields if i["marcTag"].startswith("5")]
        fields_5xx = []
        for field in fields:
            content = [i["content"] for i in field["subfields"]]
            fields_5xx.extend(content)
        return fields_5xx

    @property
    def grade_level(self) -> str:
        grade_level = [i for i in self.var_fields if i["marcTag"] == "521"]
        if grade_level:
            subfields_521 = grade_level[0]["subfields"]
            grade_level_string = " ".join([i["content"].strip() for i in subfields_521])
            matches = map_to_closest_grade_enum(grade_level_string)
            return matches
        return None

    @property
    def ids(self) -> list[str]:
        ids = [i for i in self.var_fields if i["marcTag"] == "944"]
        if ids:
            id_string = " ".join([i["content"] for i in ids[0]["subfields"]])
            return [normalize_isbn(i) for i in id_string.split()]
        return []

    @property
    def title_fields(self) -> list[str]:
        title_list = []
        if self.set_type == "CLUB":
            return [self.set_title.split("by")[0]]
        if self.set_type == "GAME":
            return [self.set_title.split("[game]")[0].strip()]
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
    def description(self) -> str | None:
        if self.subject == "GAME":
            field_520 = [i for i in self.var_fields if i["marcTag"] == "520"]
            subfields_520 = field_520[0]["subfields"]
            desc = (
                " ".join([i["content"] for i in subfields_520])
                .replace("v.", " item(s)")
                .replace("  ", " ")
            )
            return desc

    @property
    def set_type(self) -> str:
        """Parses majority of call number string to identify set type."""
        if self.subject == "GAME":
            return "GAME"
        set_types = {
            "GAME": re.compile(r"game", re.IGNORECASE),
            "CLUB": re.compile(r"book\s*club( set)?", re.IGNORECASE),
            "STORY": re.compile(r"story\s*telling", re.IGNORECASE),
            "AUDIO": re.compile(r"(audio)|(digital\s*devices?)", re.IGNORECASE),
            "LPRINT": re.compile(r"(large\s*print)|(lprint)", re.IGNORECASE),
            "TOPIC": re.compile(r"topic( set)?", re.IGNORECASE),
        }
        for item_type, regex in set_types.items():
            match = regex.match(self.call_number)
            if match:
                return item_type
        return "TOPIC"


class MinimalLegacySetStub:
    def __init__(self, bib_id: str, subject: str) -> None:
        self.bib_id = bib_id
        self.subject = subject

    def get_minimal_bib_data(self) -> MinimalLegacyBibData:
        manager = PlatformManager()
        bib_data = manager.get_platform_bib(self.bib_id)
        logger.debug(f"({self.bib_id}) Bib record retrieved from platform.")
        return MinimalLegacyBibData(
            bib_id=self.bib_id,
            language=bib_data["lang"]["code"],
            set_title=bib_data["title"],
            var_fields=bib_data["varFields"],
            subject=self.subject,
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


class MinimalLegacyTeacherSetData:
    def __init__(
        self,
        bib_id: MinimalLegacyBibData,
        copies_of_set: int,
        description: str | None,
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
        self.description = description
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
        cls, bib_data: MinimalLegacyBibData, item_data: list[LegacyItemData]
    ) -> "MinimalLegacyTeacherSetData":
        zipped_ids = list(zip_longest(bib_data.ids, bib_data.title_fields))
        if bib_data.subject == "GAME":
            return MinimalLegacyTeacherSetData(
                bib_id=bib_data.bib_id,
                copies_of_set=len(item_data),
                description=bib_data.description,
                enhanced=bib_data.enhanced,
                grade_level=bib_data.grade_level,
                language=bib_data.language,
                legacy_barcodes={i.barcode: i.call_number for i in item_data},
                call_number=bib_data.call_number.strip(),
                physical_description=bib_data.physical_description,
                record_type=bib_data.record_type,
                set_parts=[
                    {"id": i[0], "copies": 1, "title": i[1], "format": "game"}
                    for i in zipped_ids
                ],
                set_title=bib_data.set_title,
                set_type=bib_data.set_type,
                study_program_info=bib_data.subject,
                var_fields=bib_data.var_fields,
            )
        return MinimalLegacyTeacherSetData(
            bib_id=bib_data.bib_id,
            copies_of_set=len(item_data),
            enhanced=bib_data.enhanced,
            grade_level=bib_data.grade_level,
            language=bib_data.language,
            legacy_barcodes={i.barcode: i.call_number for i in item_data},
            call_number=bib_data.call_number.strip(),
            physical_description=bib_data.physical_description,
            record_type=bib_data.record_type,
            set_parts=[{"id": i[0], "copies": 1, "title": i[1]} for i in zipped_ids],
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
                    logger.warning(
                        f"Item {n + 1} of {len(self.set_parts)} missing ID ({part})."
                    )
                    part.id = input(
                        f"Please provide ID for part {n + 1} of {self.bib_id}\n"
                    )
                    index = input("Please provide index for search\n")
                    worldcat_part = manager.get_worldcat_data_for_part(
                        id=part.id, index=index, format=part.format
                    )
                part.id = worldcat_part["id"]
                worldcat_part.update(
                    {"id": part.id, "format": part.format, "copies": part.copies}
                )
                if "title" not in worldcat_part:
                    worldcat_part["title"] = part.title
                if not worldcat_part["description"] and self.description:
                    worldcat_part["description"] = self.description
                parts.append(worldcat_part)
        return parts


class MinimalLegacyTeacherSet:
    def __init__(
        self,
        set_data: MinimalLegacyTeacherSetData,
        worldcat_parts: list[dict[str, Any]],
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
                    format=worldcat_part["format"],
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


class StubMinimalFromPlatform:
    def __init__(self, bib_data: MinimalLegacyBibData) -> None:
        self.bib_data = bib_data
        self.ids = bib_data.ids
        self.title = bib_data.set_title
        self.title_fields = bib_data.title_fields
        self.var_fields = bib_data.var_fields

    def update_var_fields(
        self,
        copy_number: int,
        total: int,
        call_number: str,
        barcode: str,
        subject: str,
        control_number: str,
        shelf_number: str | None,
    ) -> None:
        new_fields = []
        new_fields.append({"marcTag": "001", "content": control_number})
        new_fields.append(
            {
                "marcTag": "901",
                "ind1": " ",
                "ind2": " ",
                "subfields": [
                    {"tag": "n", "content": barcode},
                    {"tag": "o", "content": call_number},
                ],
            }
        )
        call_number_subfields = [{"tag": "a", "content": f"MLNYC {subject}"}]
        if self.bib_data.set_type:
            call_number_subfields.append(
                {"tag": "f", "content": self.bib_data.set_type}
            )
        if self.bib_data.grade_level:
            call_number_subfields.append(
                {"tag": "p", "content": self.bib_data.grade_level}
            )
        call_number_subfields.append({"tag": "c", "content": shelf_number})
        new_fields.append(
            {
                "marcTag": "091",
                "ind1": " ",
                "ind2": " ",
                "subfields": call_number_subfields,
            }
        )
        zipped_ids = list(zip_longest(self.ids, self.title_fields))
        for zipped_set in zipped_ids:
            id_field = {"marcTag": "730", "ind1": "0", "ind2": "2", "subfields": []}
            if zipped_set[1]:
                id_field["subfields"].append({"tag": "a", "content": zipped_set[1]})
            if zipped_set[0]:
                id_field["subfields"].append({"tag": "x", "content": zipped_set[0]})
            if zipped_set[1]:
                id = zipped_set[1]
            elif zipped_set[0] and not zipped_set[1]:
                id = zipped_set[1]
            if zipped_set[0] or zipped_set[1]:
                item_field = {
                    "marcTag": "949",
                    "ind1": " ",
                    "ind2": " ",
                    "subfields": [
                        {"tag": "h", "content": "10"},
                        {"tag": "i", "content": f"[BARCODE]-{id}"},
                        {"tag": "n", "content": id},
                        {"tag": "l", "content": "eduls"},
                        {"tag": "o", "content": "m"},
                        {"tag": "q", "content": "30010"},
                        {"tag": "t", "content": "252"},
                        {"tag": "u", "content": "-"},
                        {"tag": "v", "content": "LOGDOE/mlnyc-bot"},
                    ],
                }
                new_fields.append(id_field)
                new_fields.append(item_field)

        for field in self.var_fields:
            if field["marcTag"] == "008":
                today = datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")
                field_008 = f"{today}nuuuuuuuu{field['content'][15:40]}"
                field["content"] = field_008
                new_fields.append(field)
            elif field["marcTag"] in ["091", "246", "490", "856", "944"]:
                continue
            elif field["marcTag"] == "300":
                for subfield in field["subfields"]:
                    if subfield["tag"] == "a":
                        subfield["content"].replace("v.", "item(s)")
                new_fields.append(field)
            elif field["marcTag"] == "245":
                field["subfields"].append(
                    {"tag": "p", "content": f"Copy {copy_number} of {total}"}
                )
                new_fields.append(field)
            elif field["marcTag"] == "505" and (self.title_fields or self.ids):
                subfields = " ".join([i["content"] for i in field["subfields"]])
                if "--" in subfields:
                    continue
                else:
                    new_fields.append(field)
            else:
                new_fields.append(field)
        self.var_fields = new_fields

    def create_marc_from_platform(self) -> Bib:
        record_type = "a"
        for field in self.var_fields:
            if field["marcTag"] is None:
                record_type = field["content"][6]
        bib = Bib()
        bib.library = "nypl"
        bib.leader = f"00000n{record_type}c a2200000za 4500"
        for field in self.var_fields:
            if field.get("content") and field.get("marcTag"):
                bib.add_ordered_field(
                    Field(tag=field["marcTag"], data=field["content"])
                )
            elif field.get("marcTag") and not field.get("content"):
                bib.add_ordered_field(
                    Field(
                        tag=field["marcTag"],
                        indicators=Indicators(field["ind1"], field["ind2"]),
                        subfields=[
                            Subfield(code=i["tag"], value=i["content"])
                            for i in field["subfields"]
                        ],
                    )
                )
        return bib
