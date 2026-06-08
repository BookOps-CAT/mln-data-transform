import logging

import pandas as pd
from bookops_marc import Bib
from pydantic import ValidationError

from mln_data_transform.legacy import LegacyTeacherSetBatch
from mln_data_transform.serialize import TeacherSetBib
from mln_data_transform.validate import TeacherSetModel

logger = logging.getLogger(__name__)


def create_sets_from_data(
    bib_id: str, item_mapping: dict[str, str]
) -> list[TeacherSetBib]:
    batch = LegacyTeacherSetBatch(bib_id=bib_id, item_mapping=item_mapping)
    set_list = batch.create_teacher_sets()
    bibs = []
    errors = []
    for set in set_list:
        try:
            set_model = TeacherSetModel.model_validate(set, from_attributes=True)
            bibs.append(set_model.to_set_bib())
        except ValidationError as e:
            logger.info(e.json())
            errors.append(e.json())

    return bibs


def write_sets_to_marc(set_bibs: list[Bib], file: str) -> None:
    with open(file, "ab") as fh:
        for bib in set_bibs:
            fh.write(bib.as_marc())


def build_item_mapping(file: str) -> dict[str, dict[str, str]]:
    df = pd.read_csv(
        file, sep="|", usecols=["BIB_ID", "BARCODE", "LOCATION"], header=0, dtype=str
    )
    result = (
        df.groupby("BIB_ID")
        .apply(lambda g: dict(zip(g["BARCODE"], g["LOCATION"])))
        .to_dict()
    )
    return result  # type: ignore
