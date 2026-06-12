import datetime
import json
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, TypeVar

import pandas as pd
from pydantic import ValidationError

from mln_data_transform.legacy import (
    LegacyTeacherSet,
    LegacyTeacherSetBatch,
    LegacyTeacherSetCopy,
)
from mln_data_transform.serialize import TeacherSetBib
from mln_data_transform.validate import TeacherSetCopyModel, TeacherSetModel

logger = logging.getLogger(__name__)

S = TypeVar("S")  # variable for `TeacherSetData` and `LegacyTeacherSet` types


class SetBuilder(ABC):
    @abstractmethod
    def create_set(self, *args, **kwargs) -> S: ...  # pragma: no branch

    @abstractmethod
    def validate_set(self, *args, **kwargs) -> S | None: ...  # pragma: no branch

    @abstractmethod
    def create_set_copy_batch(
        self, *args, **kwargs
    ) -> list[S]: ...  # pragma: no branch

    @abstractmethod
    def validate_set_copies(
        self, *args, **kwargs
    ) -> list[TeacherSetBib]: ...  # pragma: no branch

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


class LegacySetBuilder(SetBuilder):
    def __init__(self, file: str) -> None:
        self.file = file

    @cached_property
    def mapping_data(self) -> pd.DataFrame:
        df = pd.read_csv(
            self.file,
            sep="|",
            usecols=[
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
        bib_df = df[df["BIB_ID"] == bib_id].reindex()
        return bib_df["CONTROL_NUMBER"].iloc[0]

    def location_mapping(self, bib_id: str) -> dict[str, str]:
        df = self.mapping_data
        bib_df = df[df["BIB_ID"] == bib_id]
        locs = dict(zip(bib_df["BARCODE"], bib_df["LOCATION"]))
        return locs

    def create_set(self, bib_id: str) -> LegacyTeacherSet:
        logger.info(f"Creating base teacher set for {bib_id}.")
        legacy_set = LegacyTeacherSet(
            bib_id=bib_id, control_number=self.control_number(bib_id)
        )
        return legacy_set

    def create_set_copy_batch(
        self, legacy_set: LegacyTeacherSet
    ) -> list[LegacyTeacherSetCopy]:
        logger.info(f"Creating copies of legacy set: {legacy_set.bib_id}.")
        batch = LegacyTeacherSetBatch(
            legacy_set=legacy_set, item_mapping=self.location_mapping(legacy_set.bib_id)
        )
        return batch.create_set_copies()

    def validate_set(self, set: LegacyTeacherSet) -> LegacyTeacherSet | None:
        logger.info(f"Validating set for {set.bib_id}.")
        try:
            TeacherSetModel.model_validate(set, from_attributes=True)
            return set
        except ValidationError as e:
            logger.error(f"Validation errors for bib {set.bib_id}: {e.json()}.")
            self.write_errors_to_file(json.loads(e.json()))

    def validate_set_copies(
        self, legacy_set_copies: list[LegacyTeacherSetCopy]
    ) -> list[LegacyTeacherSetCopy]:
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
                    f"{set.copy_number} of {set.copies_of_set}"
                )
                error_data.append(json.loads(e.json()))
        if error_data:
            self.write_errors_to_file(error_data)
        return valid_bibs
