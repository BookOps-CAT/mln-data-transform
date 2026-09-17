import copy
import logging
from functools import cached_property
from typing import Any

import pandas as pd

from mln_data_transform.build import TeacherSetBuilder
from mln_data_transform.legacy import (
    LegacySetStub,
    LegacyTeacherSet,
    LegacyTeacherSetData,
)
from mln_data_transform.model import TeacherSetCopy

logger = logging.getLogger(__name__)


class LegacyTeacherSetBuilder(TeacherSetBuilder):
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

    def add_barcode_data(
        self, bib_id: str, copy_num: int, data: dict
    ) -> dict[str, Any]:
        mapping = self.location_mapping(bib_id)
        barcode = mapping[copy_num]["BARCODE"]
        call_num = data["legacy_barcodes"].get(barcode, "")
        subfields = [("n", barcode), ("o", call_num)]
        legacy_data = {"tag": "901", "ind1": " ", "ind2": " ", "subfields": subfields}
        data["var_field_data"].append(legacy_data)
        data["shelf_number"] = mapping[copy_num].get("LOCATION", "[SHELF-NUMBER]")
        return data

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

    def create_set_copies(
        self, set_dict: dict[str, Any], control_number: str
    ) -> list[TeacherSetCopy]:
        copies = []
        set_dict["control_number"] = control_number
        bib_id = set_dict.get("bib_id")
        for copy_num in range(0, set_dict["copies_of_set"]):
            set_copy_dict = copy.deepcopy(set_dict)
            set_copy_dict = self.add_barcode_data(
                bib_id=bib_id, copy_num=copy_num, data=set_copy_dict
            )
            set_copy_dict["copy_number"] = copy_num + 1
            copies.append(TeacherSetCopy(**set_copy_dict))
        return copies

    def location_mapping(self, bib_id: str) -> dict[str, list[str]]:
        df = self.mapping_data
        bib_df = df[df["BIB_ID"] == bib_id].reset_index()
        return bib_df.to_dict("index")
