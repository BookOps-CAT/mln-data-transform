import datetime
import json
import logging
from functools import cached_property
from typing import Any

import pandas as pd
from pydantic import ValidationError

from mln_data_transform.legacy import LegacyTeacherSet, LegacyTeacherSetData
from mln_data_transform.model import TeacherSetCopy
from mln_data_transform.serialize import TeacherSetBib
from mln_data_transform.teacher_sets import TeacherSet, TeacherSetData
from mln_data_transform.transform import PlatformManager
from mln_data_transform.validate import TeacherSetCopyModel, TeacherSetModel

logger = logging.getLogger(__name__)


class TeacherSetBuilder:
    def __init__(self, file: str) -> None:
        self.file = file

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

    def create_legacy_set(self, bib_id: str) -> LegacyTeacherSet:
        logger.info(f"Creating base teacher set for {bib_id}.")
        platform_manager = PlatformManager()
        set_data = LegacyTeacherSetData(
            bib_id=bib_id, platform_manager=platform_manager
        )
        legacy_set = LegacyTeacherSet(set_data=set_data)
        return legacy_set

    def create_teacher_set(
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
    ) -> TeacherSet:
        logger.info(f"Creating base teacher set for new set: '{set_title}'.")
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
        return TeacherSet(set_data=set_data)

    def create_set_copies(
        self, teacher_set_dict: dict[str, Any]
    ) -> list[TeacherSetCopy]:
        copies = []
        bib_id = teacher_set_dict.get("bib_id")
        for copy_num in range(0, teacher_set_dict["copies_of_set"]):
            if bib_id:
                logger.info(f"Creating copies of legacy set: {bib_id}.")
                mapping = self.location_mapping(bib_id)
                teacher_set_dict["var_field_data"].append(
                    {
                        "tag": "901",
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [("n", mapping[copy_num]["BARCODE"])],
                    }
                )
                teacher_set_dict["shelf_number"] = mapping[copy_num]["LOCATION"]
            else:
                teacher_set_dict["shelf_number"] = "[SHELF-NUMBER]"
            teacher_set_dict["copy_number"] = copy_num + 1
            print(teacher_set_dict)
            copies.append(TeacherSetCopy(**teacher_set_dict))
        return copies

    def validate_set(self, set: LegacyTeacherSet | TeacherSet) -> TeacherSetCopy:
        logger.info("Validating set.")
        try:
            teacher_set = TeacherSetModel.model_validate(set, from_attributes=True)
            return teacher_set.model_dump()
        except ValidationError as e:
            logger.error(f"Validation errors for set: {e.json()}.")
            self.write_errors_to_file(json.loads(e.json()))

    def validate_set_copies(
        self, legacy_set_copies: list[TeacherSetCopy]
    ) -> list[TeacherSetCopy]:
        valid_bibs = []
        error_data = []
        logger.info(
            f"Validating {len(legacy_set_copies)} set copies for "
            f"{legacy_set_copies[0].bib_id}."
        )
        for set in legacy_set_copies:
            try:
                set_copy = TeacherSetCopyModel.model_validate(set, from_attributes=True)
                valid_bibs.append(set_copy.to_set_bib())
            except ValidationError as e:
                logger.error(
                    f"Validation errors for bib {set.bib_id}, copy "
                    f"{set.copy_number + 1} of {set.copies_of_set}: {e.json()}"
                )
                error_data.append(json.loads(e.json()))
        if error_data:
            self.write_errors_to_file(error_data)
        return valid_bibs

    def write_errors_to_file(self, errors: list[dict[str, Any]]) -> None:
        today_str = datetime.datetime.strftime(datetime.date.today(), "%y%m%d")
        df = pd.DataFrame(errors)
        df.to_csv(f"data/{today_str}_validation_errors.csv", index=False, mode="a")

    def write_marc_to_file(self, out_file: str, set_bibs: list[TeacherSetBib]) -> None:
        logger.info(f"Writing records to file for {set_bibs[0].control_number}.")
        with open(out_file, "ab") as fh:
            for set_bib in set_bibs:
                bib = set_bib.to_bib()
                fh.write(bib.as_marc())
