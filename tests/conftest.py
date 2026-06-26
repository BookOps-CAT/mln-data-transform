import json
import logging
import logging.config
import os
from typing import Any

import pytest
from bookops_nypl_platform import PlatformSession, PlatformToken
from bookops_worldcat import MetadataSession, WorldcatAccessToken
from pymarc import Field, Indicators, Record, Subfield


@pytest.fixture()
def mock_creds() -> None:
    os.environ["NYPL_PLATFORM_CLIENT"] = "platform_client"
    os.environ["NYPL_PLATFORM_SECRET"] = "platform_secret"
    os.environ["NYPL_PLATFORM_OAUTH"] = "fakeurl"
    os.environ["WORLDCAT_KEY"] = "worldcat_key"
    os.environ["WORLDCAT_SECRET"] = "worldcat_secret"


@pytest.fixture(autouse=True)
def setup_logging(caplog) -> None:
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "basic": {
                "format": "%(app)s-%(asctime)s-%(filename)s-%(lineno)d-%(levelname)s-%(message)s",
                "defaults": {"app": "mln_transform"},
            }
        },
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
                "formatter": "basic",
                "level": "INFO",
            }
        },
        "loggers": {
            "mln_transform": {
                "handlers": ["stream"],
                "level": "INFO",
                "propagate": True,
            }
        },
    }
    logging.config.dictConfig(config)
    caplog.set_level(logging.INFO)


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
def legacy_set_test_data(test_bib_data) -> dict[str, Any]:
    return {
        "bib_id": "12345",
        "copies_of_set": 2,
        "grade_level": "A",
        "enhanced": None,
        "record_type": "a",
        "language": "eng",
        "legacy_barcodes": {
            "33333987654321": "Teacher Set SOC A Foo Bar Book Club 1-1",
            "33333123456789": "Teacher Set SOC A Foo Bar Book Club 1-2",
        },
        "call_number": "Teacher Set SOC A Foo Bar Book Club 1",
        "physical_description": "4 item(s)",
        "set_title": "Foo Bar Teacher Set",
        "set_type": "CLUB",
        "study_program_info": "SOC",
        "var_fields": test_bib_data["varFields"],
        "set_parts": [
            {"isbn": "9781234567897", "copies": 2},
            {"copies": 2, "isbn": "9780987654328"},
        ],
    }


@pytest.fixture
def test_bib_data() -> dict[str, Any]:
    with open("tests/data/platform_bib.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def test_item_data() -> dict[str, Any]:
    return [
        {
            "id": "31187496",
            "callNumber": "Teacher Set SOC A Foo Bar Book Club 1-1   ",
            "barcode": "33333987654321",
            "status": {"code": "-", "display": "AVAILABLE", "duedate": None},
            "varFields": [],
        },
        {
            "id": "31187496",
            "callNumber": "Teacher Set SOC A Foo Bar Book Club 1-2   ",
            "barcode": "33333123456789",
            "status": {"code": "-", "display": "AVAILABLE", "duedate": None},
            "varFields": [],
        },
    ]


@pytest.fixture
def stub_bib() -> Record:
    record = Record()
    record.add_field(
        Field(
            tag="100",
            indicators=Indicators("1", " "),
            subfields=[
                Subfield(code="a", value="Bar, Foo"),
                Subfield(code="d", value="1980-"),
            ],
        )
    )
    record.add_field(
        Field(
            tag="245",
            indicators=Indicators("0", "0"),
            subfields=[Subfield(code="a", value="Fake book 1.")],
        )
    )
    record.add_field(
        Field(
            tag="264",
            indicators=Indicators(" ", "1"),
            subfields=[
                Subfield(code="a", value="New York :"),
                Subfield(code="b", value="Universe,"),
                Subfield(code="c", value="2000."),
            ],
        )
    )
    record.add_field(
        Field(
            tag="520",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="Fake description of book.")],
        )
    )
    record.add_field(
        Field(
            tag="650",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value="Fake fast term."),
                Subfield(code="2", value="fast"),
            ],
        )
    )
    record.add_field(
        Field(
            tag="650",
            indicators=Indicators(" ", "4"),
            subfields=[Subfield(code="a", value="NYC")],
        )
    )
    record.add_field(
        Field(
            tag="651",
            indicators=Indicators(" ", "0"),
            subfields=[Subfield(code="a", value="New York (N.Y.)")],
        )
    )
    record.add_field(
        Field(
            tag="655",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value="Comics (Graphic works)."),
                Subfield(code="2", value="lcgft"),
            ],
        )
    )
    return record


@pytest.fixture()
def mock_worldcat_response() -> list[dict[str, Any]]:
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
                    "subfields": [("a", "Comics (Graphic works)."), ("2", "lcgft")],
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
def mock_worldcat_response_no_pub_dates() -> None:
    return [
        {
            "author_name": "Sasek, M.",
            "author_dates": "1916-1980",
            "description": "Fake description of book.",
            "isbn": "9781234567897",
            "pub_date": None,
            "subjects": [],
            "title": "This is New York",
        }
    ]


class MockJsonResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def json(self) -> dict[str, Any]:
        return self.data


class MockMarcResponse:
    def __init__(self, data: bytes) -> None:
        self.data = data

    @property
    def content(self) -> bytes:
        return self.data


@pytest.fixture
def mock_session_managers(
    monkeypatch, mock_creds, stub_bib, test_bib_data, test_item_data
) -> None:
    def get_platform_bib(*args, **kwargs):
        return MockJsonResponse({"data": test_bib_data})

    def get_platform_items(*args, **kwargs):
        return MockJsonResponse({"data": test_item_data})

    def get_worldcat_bib(*args, **kwargs):
        return MockMarcResponse(stub_bib.as_marc())

    def get_worldcat_brief_bib(*args, **kwargs):
        return MockJsonResponse(
            {
                "briefRecords": [
                    {
                        "oclcNumber": "ocn123456789",
                        "catalogingInfo": {"levelOfCataloging": " "},
                    }
                ]
            }
        )

    def fake_token(*args, **kwargs) -> None:
        pass

    monkeypatch.setattr(WorldcatAccessToken, "_request_token", fake_token)
    monkeypatch.setattr(PlatformToken, "_get_token", fake_token)
    monkeypatch.setattr(PlatformSession, "_update_authorization", fake_token)
    monkeypatch.setattr(MetadataSession, "brief_bibs_search", get_worldcat_brief_bib)
    monkeypatch.setattr(MetadataSession, "bib_get", get_worldcat_bib)
    monkeypatch.setattr(PlatformSession, "get_bib", get_platform_bib)
    monkeypatch.setattr(PlatformSession, "get_bib_items", get_platform_items)


@pytest.fixture
def mock_session_managers_missing_data(
    monkeypatch, mock_session_managers, stub_bib, test_item_data
) -> None:
    def get_worldcat_bib_no_description(*args, **kwargs):
        bib = stub_bib
        bib.remove_fields("520")
        return MockMarcResponse(bib.as_marc())

    def get_platform_items(*args, **kwargs):
        test_item_data[0]["varFields"] = [
            {
                "fieldTag": "x",
                "content": "Below 75%. Missing 6/10 vol, 4 vol in INC-238",
            }
        ]
        return MockJsonResponse({"data": test_item_data})

    monkeypatch.setattr(MetadataSession, "bib_get", get_worldcat_bib_no_description)
    monkeypatch.setattr(PlatformSession, "get_bib_items", get_platform_items)
