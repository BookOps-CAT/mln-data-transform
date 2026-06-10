import datetime
import json
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, TypeVar

import pandas as pd
from pydantic import ValidationError

from mln_data_transform.legacy import LegacyTeacherSet, LegacyTeacherSetBatch
from mln_data_transform.serialize import TeacherSetBib
from mln_data_transform.validate import TeacherSetModel

logger = logging.getLogger(__name__)

S = TypeVar("S")  # variabe for `TeacherSetData` and `LegacyTeacherSet` types


class SetBuilder(ABC):
    @abstractmethod
    def create_sets(self, *args, **kwargs) -> list[S]: ...  # pragma: no branch

    @abstractmethod
    def validate_set_records(
        self, sets: list[S]
    ) -> list[TeacherSetBib]: ...  # pragma: no branch

    def write_errors_to_file(self, errors: list[dict[str, Any]]) -> None:
        today_str = datetime.datetime.strftime(datetime.date.today(), "%y%m%d")
        df = pd.DataFrame(errors)
        df.to_csv(f"data/{today_str}_validation_errors.csv", index=False, mode="a")

    def write_marc_to_file(self, out_file: str, set_bibs: list[TeacherSetBib]) -> None:
        with open(out_file, "ab") as fh:
            for set_bib in set_bibs:
                bib = set_bib.to_bib()
                fh.write(bib.as_marc())


class LegacySetBuilder(SetBuilder):
    def __init__(self, file: str) -> None:
        self.file = file

    @cached_property
    def mapping_data(self) -> pd.DataFrame:
        df = pd.read_csv(
            self.file,
            sep="|",
            names=[
                "SUBJECT",
                "BARCODE",
                "LOCATION",
                "BIB_ID",
                "ITEM_ID",
                "CONTROL_NUMBER",
            ],
            header=0,
            dtype=str,
        )
        df.fillna("", inplace=True)
        return df

    @property
    def all_bib_ids(self) -> list[str]:
        df = self.mapping_data
        return df["BIB_ID"].unique().tolist()

    def control_number(self, bib_id: str) -> str:
        df = self.mapping_data
        bib_df = df[df["BIB_ID"] == bib_id]
        control_numbers = bib_df["CONTROL_NUMBER"]
        if control_numbers.nunique() == 1:
            return control_numbers.iloc[0]
        return ValueError(f"Multiple control numbers present for {bib_id}.")

    def location_mapping(self, bib_id: str) -> dict[str, str]:
        df = self.mapping_data
        bib_df = df[df["BIB_ID"] == bib_id]
        locs = dict(zip(bib_df["BARCODE"], bib_df["LOCATION"]))
        return locs

    def subject(self, bib_id: str) -> str:
        df = self.mapping_data
        bib_df = df[df["BIB_ID"] == bib_id]
        subjects = bib_df["SUBJECT"]
        if subjects.nunique() == 1:
            return subjects[0]
        return ValueError(f"Multiple subjects present for {bib_id}.")

    def create_sets(self, bib_id: str) -> list[LegacyTeacherSet]:
        batch = LegacyTeacherSetBatch(
            bib_id=bib_id,
            control_number=self.control_number(bib_id),
            item_mapping=self.location_mapping(bib_id),
        )
        return batch.create_teacher_sets()

    def validate_set_records(self, sets: list[LegacyTeacherSet]) -> list[TeacherSetBib]:
        valid_bibs = []
        error_data = []
        for set in sets:
            try:
                set_model = TeacherSetModel.model_validate(set, from_attributes=True)
                valid_bibs.append(set_model.to_set_bib())
            except ValidationError as e:
                logger.error(
                    f"Validation errors for Bib ID{set.bib_id}, copy "
                    f"{set.copy_number} of {set.total_copies}"
                )
                error_data.append(json.loads(e.json()))
        if error_data:
            self.write_errors_to_file(error_data)
        return valid_bibs
