import logging
from functools import cached_property

import pandas as pd

from mln_data_transform.control_numbers import ControlNumberGenerator
from mln_data_transform.minimal import MinimalLegacySetStub, StubMinimalFromPlatform

logger = logging.getLogger(__name__)


class StubTeacherSetBuilder:
    def __init__(
        self, file: str, ctrl_number_file: str | None = "data/control_number_state.json"
    ) -> None:
        self.file = file
        self.ctrl_number_gen = ControlNumberGenerator(ctrl_number_file)

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

    def build_stub_legacy_sets(self, bib_id: str) -> list:
        logger.info(f"({bib_id}) Building teacher set from legacy data.")
        mapping = self.location_mapping(bib_id)
        set_stub = MinimalLegacySetStub(bib_id=bib_id, subject=mapping[0]["SUBJECT"])
        bib_data = set_stub.get_minimal_bib_data()
        item_data = set_stub.get_item_data()
        stub = StubMinimalFromPlatform(bib_data=bib_data)
        copies_of_set = len(item_data)
        legacy_barcodes = {i.barcode: i.call_number for i in item_data}
        copies = []
        control_number = self.ctrl_number_gen.next_control_number()
        logger.debug(f"({control_number}) Creating {copies_of_set} copy/copies of set.")
        for copy_num in range(0, copies_of_set):
            barcode = mapping[copy_num]["BARCODE"]
            call_num = legacy_barcodes.get(barcode, "")
            shelf_number = mapping[copy_num].get("LOCATION", "[SHELF-NUMBER]")
            stub.update_var_fields(
                copy_number=copy_num + 1,
                total=copies_of_set,
                call_number=call_num,
                barcode=barcode,
                shelf_number=shelf_number,
                subject=set_stub.subject,
                control_number=control_number,
            )
            stub_copy = stub.create_marc_from_platform()
            copies.append(stub_copy)
        return copies

    def write_stub_marc_to_file(self, out_file: str, set_bibs: list) -> None:
        logger.info("Writing records to file for set.")
        with open(out_file, "ab") as fh:
            for bib in set_bibs:
                fh.write(bib.as_marc())
