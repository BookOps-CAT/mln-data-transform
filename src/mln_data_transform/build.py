import copy
import datetime
import json
import logging
from functools import cached_property
from typing import Any

import pandas as pd
from pydantic import ValidationError

from mln_data_transform.control_numbers import ControlNumberGenerator
from mln_data_transform.legacy import (
    LegacySetStub,
    LegacyTeacherSet,
    LegacyTeacherSetData,
)
from mln_data_transform.model import TeacherSetCopy
from mln_data_transform.serialize import TeacherSetBib
from mln_data_transform.teacher_sets import TeacherSet, TeacherSetData
from mln_data_transform.validate import TeacherSetCopyModel, TeacherSetModel

logger = logging.getLogger(__name__)


class TeacherSetBuilder:
    def __init__(self, file: str) -> None:
        self.file = file
        self.ctrl_number_gen = ControlNumberGenerator("data/control_number_state.json")

    @cached_property
    def mapping_data(self) -> pd.DataFrame:
        df = pd.read_csv(
            self.file,
            sep="|",
            usecols=["SUBJECT", "BARCODE", "LOCATION", "BIB_ID"],
            header=0,
            dtype=str,
        )
        df.fillna("", inplace=True)
        return df

    @property
    def all_bib_ids(self) -> list[str]:
        df = self.mapping_data
        return df["BIB_ID"].unique().tolist()

    def location_mapping(self, bib_id: str) -> dict[str, list[str]]:
        df = self.mapping_data
        bib_df = df[df["BIB_ID"] == bib_id].reset_index()
        return bib_df.to_dict("index")

    def build_legacy_set(self, bib_id: str) -> dict[str, Any]:
        logger.info(f"({bib_id}) Building teacher set from legacy data.")
        set_stub = LegacySetStub(bib_id=bib_id)
        bib_data = set_stub.get_bib_data()
        item_data = set_stub.get_item_data()
        set_data = LegacyTeacherSetData.from_bib_item_data(bib_data, item_data)
        worldcat_parts = set_data.get_worldcat_data_for_parts()
        legacy_set = LegacyTeacherSet(set_data=set_data, worldcat_parts=worldcat_parts)
        validated_set = self.validate_set(legacy_set)
        return validated_set

    def build_teacher_set(
        self,
        copies_of_set: int,
        grade_level: str,
        language: str,
        parts: list[dict[str, str]],
        set_title: str,
        set_type: str,
        study_program_info: str,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        special_formats: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        logger.info(f"Building teacher set from new data: '{set_title}'.")
        set_data = TeacherSetData(
            copies_of_set=copies_of_set,
            grade_level=grade_level,
            language=language,
            parts=parts,
            set_title=set_title,
            set_type=set_type,
            study_program_info=study_program_info,
            local_genre_term=local_genre_term,
            local_topic_term=local_topic_term,
            special_formats=special_formats,
        )
        worldcat_parts = set_data.get_worldcat_data_for_parts()
        teacher_set = TeacherSet(set_data=set_data, worldcat_parts=worldcat_parts)
        validated_set = self.validate_set(teacher_set)
        return validated_set

    def build_set_copies(self, set_data: dict[str, Any]) -> dict[str, Any]:
        control_number = self.ctrl_number_gen.next_control_number()
        log_id = (
            set_data["bib_id"] if set_data["bib_id"] is not None else control_number
        )
        logger.debug(
            f"({log_id}) Creating {set_data['copies_of_set']} copy/copies of set."
        )
        try:
            set_copies = self.create_set_copies(
                teacher_set_dict=set_data, control_number=control_number
            )
            valid_set_copies = self.validate_set_copies(set_copies)
            self.ctrl_number_gen.save_state()
            logger.info(
                f"({log_id}) Created {len(valid_set_copies)} valid copy/copies of set."
            )
            return valid_set_copies
        except ValidationError as e:
            logger.error(f"Validation errors for set copies: {json.loads(e.json())}")

    def create_set_copies(
        self, teacher_set_dict: dict[str, Any], control_number: str
    ) -> list[TeacherSetCopy]:
        copies = []
        teacher_set_dict["control_number"] = control_number
        bib_id = teacher_set_dict.get("bib_id")
        for copy_num in range(0, teacher_set_dict["copies_of_set"]):
            set_copy_dict = copy.deepcopy(teacher_set_dict)
            if bib_id:
                mapping = self.location_mapping(bib_id)
                barcode = mapping[copy_num]["BARCODE"]
                set_copy_dict["var_field_data"].append(
                    {
                        "tag": "901",
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [
                            ("n", barcode),
                            ("o", set_copy_dict["legacy_barcodes"].get(barcode, "")),
                        ],
                    }
                )
                set_copy_dict["shelf_number"] = mapping[copy_num].get(
                    "LOCATION", "[SHELF-NUMBER]"
                )
            else:
                set_copy_dict["shelf_number"] = "[SHELF-NUMBER]"
            set_copy_dict["copy_number"] = copy_num + 1
            copies.append(TeacherSetCopy(**set_copy_dict))
        return copies

    def validate_set(self, set: LegacyTeacherSet | TeacherSet) -> dict[str, Any]:
        try:
            teacher_set = TeacherSetModel.model_validate(set, from_attributes=True)
            return teacher_set.model_dump()
        except ValidationError as e:
            logger.error(f"Validation errors for set: {e.json()}.")

    def validate_set_copies(
        self, legacy_set_copies: list[TeacherSetCopy]
    ) -> list[TeacherSetCopy]:
        valid_bibs = []
        for set in legacy_set_copies:
            set_copy = TeacherSetCopyModel.model_validate(set, from_attributes=True)
            valid_bibs.append(set_copy.to_set_bib())
        return valid_bibs

    def write_errors_to_file(self, errors: list[dict[str, Any]]) -> None:
        today_str = datetime.datetime.strftime(datetime.date.today(), "%y%m%d")
        df = pd.DataFrame(errors)
        df.to_csv(f"data/{today_str}_validation_errors.csv", index=False, mode="a")

    def write_marc_to_file(self, out_file: str, set_bibs: list[TeacherSetBib]) -> None:
        logger.info(f"({set_bibs[0].control_number}) Writing records to file for set.")
        with open(out_file, "ab") as fh:
            for set_bib in set_bibs:
                bib = set_bib.to_bib()
                fh.write(bib.as_marc())
