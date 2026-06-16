import datetime
import json
import logging
import logging.config
import os
from typing import Any

import pandas as pd
import pytest
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
def test_bib_data() -> dict[str, Any]:
    with open("tests/data/platform_bib.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def test_item_data() -> dict[str, Any]:
    with open("tests/data/platform_item.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def today_str() -> str:
    return datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")


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
        with open("tests/data/platform_item.json", "r") as fh:
            json_data = json.load(fh)
            return MockJsonResponse({"data": [json_data]})


class FakeMetadataSession(FakeSession):
    def bib_get(self, *args, **kwargs) -> dict[str, Any]:
        record = Record()
        record.add_field(
            Field(
                tag="100",
                indicators=Indicators("1", " "),
                subfields=[
                    Subfield(code="a", value="Sasek, M."),
                    Subfield(code="d", value="1916-1980"),
                ],
            )
        )
        record.add_field(
            Field(
                tag="245",
                indicators=Indicators("0", "0"),
                subfields=[
                    Subfield(code="a", value="This is New York :"),
                    Subfield(code="b", value="fake subtitle /"),
                    Subfield(code="c", value="by M. Sasek."),
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
                    Subfield(code="c", value="2003."),
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
                    Subfield(code="a", value="Fake genre."),
                    Subfield(code="2", value="lcgft"),
                ],
            )
        )
        return MockMarcResponse(record.as_marc())

    def brief_bibs_search(self, *args, **kwargs) -> dict[str, Any]:
        return MockJsonResponse(
            {
                "briefRecords": [
                    {
                        "oclcNumber": "ocn123456789",
                        "catalogingInfo": {"levelOfCataloging": " "},
                    },
                    {"oclcNumber": "123"},
                    {
                        "oclcNumber": "ocn123456789",
                        "catalogingInfo": {"levelOfCataloging": "7"},
                    },
                    {
                        "oclcNumber": "ocn123456789",
                        "catalogingInfo": {"levelOfCataloging": "M"},
                    },
                ]
            }
        )


@pytest.fixture
def mock_responses(monkeypatch, mock_creds) -> None:
    def fake_token(*args, **kwargs) -> None:
        pass

    def fake_platform_session(*args, **kwargs) -> FakePlatformSession:
        return FakePlatformSession()

    def fake_metadata_session(*args, **kwargs) -> FakeMetadataSession:
        return FakeMetadataSession()

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

    monkeypatch.setattr("mln_data_transform.build.pd.read_csv", mock_read_csv)
    monkeypatch.setattr("mln_data_transform.transform.PlatformToken", fake_token)
    monkeypatch.setattr(
        "mln_data_transform.transform.PlatformSession", fake_platform_session
    )
    monkeypatch.setattr(
        "mln_data_transform.transform.MetadataSession", fake_metadata_session
    )
    monkeypatch.setattr("mln_data_transform.transform.WorldcatAccessToken", fake_token)


@pytest.fixture
def mock_worldcat_response_missing_data(monkeypatch, mock_responses) -> None:
    def fake_marc_record(*args, **kwargs) -> None:
        record = Record()
        record.add_field(
            Field(
                tag="245",
                indicators=Indicators("1", "0"),
                subfields=[Subfield(code="a", value="This is New York.")],
            )
        )
        record.add_field(
            Field(
                tag="264",
                indicators=Indicators(" ", "1"),
                subfields=[
                    Subfield(code="a", value="New York :"),
                    Subfield(code="b", value="Universe,"),
                    Subfield(code="c", value="20uu."),
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
        return MockMarcResponse(record.as_marc())

    monkeypatch.setattr(FakeMetadataSession, "bib_get", fake_marc_record)


@pytest.fixture
def mock_worldcat_response_no_pub_dates(monkeypatch, mock_responses) -> None:
    def fake_marc_record(*args, **kwargs) -> None:
        record = Record()
        record.add_field(
            Field(
                tag="245",
                indicators=Indicators("1", "0"),
                subfields=[Subfield(code="a", value="This is New York.")],
            )
        )
        record.add_field(
            Field(
                tag="264",
                indicators=Indicators(" ", "1"),
                subfields=[Subfield(code="a", value="New York")],
            )
        )
        return MockMarcResponse(record.as_marc())

    monkeypatch.setattr(FakeMetadataSession, "bib_get", fake_marc_record)


@pytest.fixture
def mock_legacy_mapping_data(monkeypatch) -> None:
    def mock_read_csv(*args, **kwargs):
        return pd.DataFrame(
            data=[
                {
                    "SUBJECT": "ELA",
                    "BARCODE": "33333402207449",
                    "LOCATION": "1",
                    "BIB_ID": "12345678",
                    "ITEM_ID": "23456789",
                    "CONTROL_NUMBER": "nn-mlnyc-0000001",
                }
            ]
        )

    monkeypatch.setattr("mln_data_transform.build.pd.read_csv", mock_read_csv)
