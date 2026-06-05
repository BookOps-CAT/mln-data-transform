import pandas as pd

from mln_data_transform.legacy import LegacyTeacherSetBatch
from mln_data_transform.models import TeacherSetBib, TeacherSetData
from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
)


def create_sets_from_data(
    bib_id: str, item_mapping: dict[str, dict[str, str]]
) -> list[TeacherSetBib]:
    batch = LegacyTeacherSetBatch(bib_id=bib_id, item_mapping=item_mapping)
    set_list = batch.create_teacher_sets()
    bibs = []
    for set in set_list:
        bib = TeacherSetData(
            copy_number=set.copy_number,
            grade_level=GradeReadingLevel[set.grade_level],
            language=set.language,
            parts=set.parts,
            physical_description=set.physical_description,
            record_type=set.record_type,
            shelf_number=set.shelf_number,
            study_program_info=SubjectStudyProgram[set.study_program_info],
            set_title=set.set_title,
            total_copies=set.total_copies,
            enhanced=set.enhanced,
            local_genre_term=set.local_genre_term,
            local_topic_term=set.local_topic_term,
            set_type=SetTypeFormat[set.set_type],
        )
        bibs.append(TeacherSetBib(bib))
    return bibs


def write_sets_to_marc(set_bibs: list[TeacherSetBib], file: str) -> None:
    bibs = [i.to_bib() for i in set_bibs]
    with open(file, "ab") as fh:
        for bib in bibs:
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
