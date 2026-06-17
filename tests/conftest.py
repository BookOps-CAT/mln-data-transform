import datetime
import json
import logging
import logging.config
import os
from typing import Any

import pytest
from bookops_nypl_platform import PlatformToken
from bookops_worldcat import WorldcatAccessToken
from pymarc import Field, Indicators, Record, Subfield

from mln_data_transform.transform import PlatformManager, WorldcatManager


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
def test_bib_data() -> dict[str, Any]:
    with open("tests/data/platform_bib.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def today_str() -> str:
    return datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")


@pytest.fixture
def stub_metadata_session(monkeypatch, mock_creds) -> None:
    def fake_token(*args, **kwargs) -> None:
        pass

    def fake_bib(*args, **kwargs) -> dict[str, Any]:
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
                subfields=[
                    Subfield(code="a", value="Fake book 1 :"),
                    Subfield(code="b", value="fake subtitle /"),
                    Subfield(code="c", value="by Foo Bar."),
                ],
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

    def fake_brief_bib(*args, **kwargs) -> str:
        return "ocn123456789"

    monkeypatch.setattr(WorldcatManager, "get_full_record", fake_bib)
    monkeypatch.setattr(WorldcatManager, "get_oclc_number_from_isbn", fake_brief_bib)
    monkeypatch.setattr(WorldcatAccessToken, "_request_token", fake_token)


@pytest.fixture
def stub_platform_session(monkeypatch, mock_creds, test_bib_data) -> None:
    def token(*args, **kwargs) -> None:
        pass

    def bib_data(*args, **kwargs) -> dict[str, Any]:
        return test_bib_data

    def item_data(*args, **kwargs):
        return [
            {
                "id": "31187496",
                "callNumber": "Teacher Set SOC A Foo Bar Book Club 1-1   ",
                "barcode": "33333987654321",
            },
            {
                "id": "31187496",
                "callNumber": "Teacher Set SOC A Foo Bar Book Club 1-2   ",
                "barcode": "33333123456789",
            },
        ]

    monkeypatch.setattr(PlatformToken, "_get_token", token)
    monkeypatch.setattr(PlatformManager, "get_platform_bib", bib_data)
    monkeypatch.setattr(PlatformManager, "get_platform_bib_items", item_data)


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


@pytest.fixture
def stub_platform_session_single_copy(
    monkeypatch, stub_platform_session, test_bib_data
) -> None:
    def fake_platform_bib_data(*args, **kwargs) -> dict[str, Any]:
        bib_data = test_bib_data
        bib_data["varFields"] = [
            i for i in bib_data["varFields"] if i["marcTag"] != "500"
        ]
        bib_data["varFields"].append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "500",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": "1 copy of 1 title."}],
            }
        )
        return bib_data

    monkeypatch.setattr(PlatformManager, "get_platform_bib", fake_platform_bib_data)


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


class FakeSession:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs) -> "FakeSession":
        return self

    def __exit__(self, *args, **kwargs) -> None:
        pass

    def close(self, *args, **kwargs) -> None:
        pass


class FakePlatformSession(FakeSession):
    def get_bib(self, id: str) -> dict[str, Any]:
        with open("tests/data/platform_bib.json", "r") as fh:
            json_data = json.load(fh)
            json_data["id"] = id
            return MockJsonResponse({"data": json_data})

    def get_bib_items(self, id: str) -> dict[str, Any]:
        item_data = [
            {
                "id": "31187496",
                "callNumber": "Teacher Set SOC A Foo Bar Book Club 1-1   ",
                "barcode": "33333987654321",
            },
            {
                "id": "31187496",
                "callNumber": "Teacher Set SOC A Foo Bar Book Club 1-2   ",
                "barcode": "33333123456789",
            },
        ]
        return MockJsonResponse({"data": item_data})


class FakeMetadataSession(FakeSession):
    def bib_get(self, *args, **kwargs) -> dict[str, Any]:
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
                subfields=[
                    Subfield(code="a", value="Fake book 1 :"),
                    Subfield(code="b", value="fake subtitle /"),
                    Subfield(code="c", value="by Foo Bar."),
                ],
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
        return MockMarcResponse(record.as_marc())

    def brief_bibs_search(self, *args, **kwargs) -> dict[str, Any]:
        records = [
            {"oclcNumber": "ocn123456789", "catalogingInfo": {"levelOfCataloging": i}}
            for i in [" ", "7", "M"]
        ]
        records.append({"oclcNumber": "123"})
        return MockJsonResponse({"briefRecords": records})


@pytest.fixture
def mock_platform_session(monkeypatch, mock_creds) -> None:
    def fake_token(*args, **kwargs) -> None:
        pass

    def fake_platform_session(*args, **kwargs) -> FakePlatformSession:
        return FakePlatformSession()

    monkeypatch.setattr("mln_data_transform.transform.PlatformToken", fake_token)
    monkeypatch.setattr(
        "mln_data_transform.transform.PlatformSession", fake_platform_session
    )


@pytest.fixture
def mock_metadata_session(monkeypatch, mock_creds) -> None:
    def fake_token(*args, **kwargs) -> None:
        pass

    def fake_metadata_session(*args, **kwargs) -> FakeMetadataSession:
        return FakeMetadataSession()

    monkeypatch.setattr("mln_data_transform.transform.WorldcatAccessToken", fake_token)
    monkeypatch.setattr(
        "mln_data_transform.transform.MetadataSession", fake_metadata_session
    )


@pytest.fixture
def mock_metadata_session_missing_data(monkeypatch, mock_metadata_session) -> None:
    def fake_marc_record(self, *args, **kwargs) -> dict[str, Any]:
        record = Record()
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
                subfields=[Subfield(code="a", value="New York.")],
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
                tag="650",
                indicators=Indicators(" ", "7"),
                subfields=[
                    Subfield(code="a", value="Fake fast term."),
                    Subfield(code="2", value="fast"),
                ],
            )
        )
        return MockMarcResponse(record.as_marc())

    monkeypatch.setattr(FakeMetadataSession, "bib_get", fake_marc_record)
