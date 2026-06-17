import pathlib
from typing import Any

import pandas as pd
import pytest
from bookops_nypl_platform import PlatformToken

from mln_data_transform.legacy import (
    LegacyBibData,
    LegacyItemData,
    LegacyTeacherSetData,
)
from mln_data_transform.teacher_sets import TeacherSetData


@pytest.fixture
def mock_control_number_file(monkeypatch) -> dict[str, Any]:
    def mock_path(*args, **kwargs):
        pass

    def mock_numbers(*args, **kwargs):
        return '{"used_numbers", ["1", "2"]}'

    monkeypatch.setattr(pathlib.Path, "write_text", mock_path)
    monkeypatch.setattr(pathlib.Path, "read_text", mock_numbers)


@pytest.fixture
def mock_location_mapping(monkeypatch, mock_control_number_file):
    def mock_read_csv(*args, **kwargs):
        return pd.DataFrame(
            data=[
                {"BARCODE": "33333987654321", "LOCATION": "1", "BIB_ID": "12345678"},
                {"BARCODE": "33333123456789", "LOCATION": "2", "BIB_ID": "12345678"},
            ]
        )

    monkeypatch.setattr("mln_data_transform.build.pd.read_csv", mock_read_csv)


@pytest.fixture
def set_test_data() -> dict[str, Any]:
    return {
        "copies_of_set": 2,
        "grade_level": "Pre-K",
        "language": "eng",
        "set_title": "Foo Bar Teacher Set",
        "parts": [
            {"isbn": "9781234567897", "copies": 2},
            {"copies": 2, "isbn": "9780987654328"},
        ],
        "set_type": "Book Club",
        "study_program_info": "Social Studies",
        "local_genre_term": ["Fiction"],
        "local_topic_term": ["New York City"],
    }


@pytest.fixture
def mock_worldcat_parts(*args, **kwargs):
    return [
        {
            "author_name": "Bar, Foo",
            "author_dates": "1980-",
            "description": "Fake description of book.",
            "isbn": "9781234567897",
            "pub_date": "2000",
            "subjects": [
                {
                    "tag": "651",
                    "ind1": " ",
                    "ind2": "0",
                    "subfields": [("a", "New York (N.Y.)")],
                },
                {
                    "tag": "655",
                    "ind1": " ",
                    "ind2": "7",
                    "subfields": [("a", "Historical fiction."), ("2", "lcgft")],
                },
            ],
            "title": "Fake book 1",
        },
        {
            "author_name": None,
            "author_dates": None,
            "description": "Another fake description of a book.",
            "isbn": "9780987654328",
            "pub_date": "20uu",
            "subjects": [],
            "title": "Fake book 2",
        },
    ]


@pytest.fixture
def mock_set(
    monkeypatch, mock_creds, caplog, mock_worldcat_parts, mock_control_number_file
) -> None:
    subject = "SOC"
    call_number = f"Teacher Set {subject} A Foo Bar Book Club 1"
    item_data = [
        {"barcode": "33333987654321", "item_id": "12345678"},
        {"barcode": "33333123456789", "item_id": "23456789"},
    ]
    bib_id = "12345678"

    def mock_parts(*args, **kwargs):
        return mock_worldcat_parts

    def mock_bib_data(*args, **kwargs):
        return LegacyBibData(
            bib_id=bib_id,
            language="eng",
            set_title="Foo Bar Teacher Set",
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
                    "subfields": [{"tag": "a", "content": "4 v."}],
                },
                {
                    "ind1": " ",
                    "ind2": " ",
                    "content": None,
                    "marcTag": "520",
                    "fieldTag": "n",
                    "subfields": [{"tag": "a", "content": "2 copies of 2 titles."}],
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
                    "subfields": [
                        {"tag": "a", "content": "9781234567897 9780987654328 "}
                    ],
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

    monkeypatch.setattr(LegacyTeacherSetData, "get_worldcat_data_for_parts", mock_parts)
    monkeypatch.setattr(TeacherSetData, "get_worldcat_data_for_parts", mock_parts)
    monkeypatch.setattr("mln_data_transform.build.pd.read_csv", mock_read_csv)
    monkeypatch.setattr(PlatformToken, "_get_token", fake_token)
    monkeypatch.setattr(LegacyTeacherSetData, "bib_data", property(mock_bib_data))
    monkeypatch.setattr(LegacyTeacherSetData, "item_data", property(mock_item_data))


@pytest.fixture
def mock_set_missing_info(monkeypatch, mock_set, mock_worldcat_parts) -> None:
    def mock_parts(*args, **kwargs):
        mock_worldcat_parts[0]["author_name"] = None
        mock_worldcat_parts[0]["author_dates"] = None
        mock_worldcat_parts[0]["pub_date"] = None
        mock_worldcat_parts[0]["subjects"] = []
        return mock_worldcat_parts

    monkeypatch.setattr(LegacyTeacherSetData, "get_worldcat_data_for_parts", mock_parts)
    monkeypatch.setattr(TeacherSetData, "get_worldcat_data_for_parts", mock_parts)


@pytest.fixture
def mock_set_no_dates(monkeypatch, mock_set, mock_worldcat_parts) -> None:
    def mock_parts(*args, **kwargs):
        mock_worldcat_parts[0]["author_name"] = None
        mock_worldcat_parts[0]["author_dates"] = None
        mock_worldcat_parts[0]["pub_date"] = None
        mock_worldcat_parts[1]["pub_date"] = None
        mock_worldcat_parts[0]["subjects"] = []
        return mock_worldcat_parts

    monkeypatch.setattr(LegacyTeacherSetData, "get_worldcat_data_for_parts", mock_parts)
    monkeypatch.setattr(TeacherSetData, "get_worldcat_data_for_parts", mock_parts)
