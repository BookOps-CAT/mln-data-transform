import logging

import pandas as pd
import pytest

from mln_data_transform.components import WorldcatSetPart
from mln_data_transform.legacy import LegacyBibData, LegacyItemData

logger = logging.getLogger(__name__)


@pytest.fixture
def mock_teacher_set(monkeypatch, mock_creds) -> None:
    def mock_parts(*args, **kwargs):
        return [
            WorldcatSetPart(
                isbn="9781234567890",
                title="Foo",
                author="Bar",
                description="A book",
                copies=1,
                subjects=[
                    {
                        "tag": "650",
                        "ind1": " ",
                        "ind2": "0",
                        "subfields": [("a", "Fake subject.")],
                    },
                    {
                        "tag": "655",
                        "ind1": " ",
                        "ind2": "7",
                        "subfields": [("a", "Fake genre."), ("2", "lcgft")],
                    },
                ],
            )
        ]

    def mock_read_csv(*args, **kwargs):
        return pd.DataFrame(
            data=[
                {
                    "SUBJECT": "ELA",
                    "BARCODE": "33333987654321",
                    "LOCATION": "1",
                    "BIB_ID": "12345678",
                    "ITEM_ID": "12345678",
                    "CONTROL_NUMBER": "nn-mlnyc-0000001",
                },
                {
                    "SUBJECT": "ELA",
                    "BARCODE": "33333123456789",
                    "LOCATION": "2",
                    "BIB_ID": "12345678",
                    "ITEM_ID": "23456789",
                    "CONTROL_NUMBER": "nn-mlnyc-0000001",
                },
            ]
        )

    monkeypatch.setattr(
        "mln_data_transform.teacher_sets.TeacherSet.parts", property(mock_parts)
    )
    monkeypatch.setattr("mln_data_transform.build.pd.read_csv", mock_read_csv)


@pytest.fixture
def mock_legacy_set(monkeypatch, mock_creds, caplog) -> None:
    subject = "SOC"
    call_number = f"Teacher Set {subject} A Foo Bar 1"
    item_data = [
        {"barcode": "33333987654321", "item_id": "12345678"},
        {"barcode": "33333123456789", "item_id": "23456789"},
    ]
    bib_id = "12345678"

    def mock_parts(*args, **kwargs):
        return [
            WorldcatSetPart(
                isbn="9781234567890",
                title="Foo",
                author="Bar",
                description="A book",
                copies=2,
                subjects=[
                    {
                        "tag": "650",
                        "ind1": " ",
                        "ind2": "0",
                        "subfields": [("a", "Fake subject.")],
                    },
                    {
                        "tag": "655",
                        "ind1": " ",
                        "ind2": "7",
                        "subfields": [("a", "Fake genre."), ("2", "lcgft")],
                    },
                ],
            )
        ]

    def mock_bib_data(*args, **kwargs):
        return LegacyBibData(
            bib_id=bib_id,
            language="eng",
            set_title="Teacher Set",
            var_fields=[
                {
                    "ind1": " ",
                    "ind2": " ",
                    "content": None,
                    "marcTag": "091",
                    "fieldTag": "c",
                    "subfields": [{"tag": "a", "content": call_number}],
                },
                {
                    "ind1": " ",
                    "ind2": " ",
                    "content": None,
                    "marcTag": "300",
                    "fieldTag": "n",
                    "subfields": [{"tag": "a", "content": "2 v."}],
                },
                {
                    "ind1": " ",
                    "ind2": " ",
                    "content": None,
                    "marcTag": "520",
                    "fieldTag": "n",
                    "subfields": [{"tag": "a", "content": "2 copies of 1 title."}],
                },
                {
                    "ind1": " ",
                    "ind2": " ",
                    "content": "00000nam  2200000 a 4500",
                    "marcTag": None,
                    "fieldTag": "n",
                    "subfields": None,
                },
                {
                    "ind1": " ",
                    "ind2": " ",
                    "content": None,
                    "marcTag": "944",
                    "fieldTag": "y",
                    "subfields": [{"tag": "a", "content": "9781234567890"}],
                },
            ],
        )

    def mock_item_data(*args, **kwargs):
        items = []
        for n, item in enumerate(item_data):
            items.append(
                LegacyItemData(
                    call_number=f"{call_number}-{str(n + 1)}",
                    item_id=item["item_id"],
                    barcode=item["barcode"],
                )
            )
        return items

    def mock_read_csv(*args, **kwargs):
        data = []
        for n, item in enumerate(item_data):
            data.append(
                {
                    "SUBJECT": subject,
                    "BARCODE": item["barcode"],
                    "LOCATION": str(n + 1),
                    "BIB_ID": bib_id,
                    "ITEM_ID": item["item_id"],
                    "CONTROL_NUMBER": "nn-mlnyc-0000001",
                }
            )
        return pd.DataFrame(data=data)

    def fake_token(*args, **kwargs) -> None:
        pass

    monkeypatch.setattr("mln_data_transform.transform.PlatformToken", fake_token)
    monkeypatch.setattr(
        "mln_data_transform.legacy.LegacyTeacherSet.parts", property(mock_parts)
    )
    monkeypatch.setattr(
        "mln_data_transform.legacy.LegacyTeacherSetData.bib_data",
        property(mock_bib_data),
    )
    monkeypatch.setattr(
        "mln_data_transform.legacy.LegacyTeacherSetData.item_data",
        property(mock_item_data),
    )
    monkeypatch.setattr("mln_data_transform.build.pd.read_csv", mock_read_csv)
