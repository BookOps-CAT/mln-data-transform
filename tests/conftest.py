import datetime
import json
import logging
import logging.config
from typing import Any

import pytest
from bookops_nypl_platform import PlatformSession
from bookops_worldcat import MetadataSession
from pymarc import Field, Indicators, Record, Subfield


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


class MockResponse:
    def __init__(self, data: dict[str, Any], marc: bytes) -> None:
        self.marc = marc
        self.data = data

    @property
    def content(self) -> bytes:
        return self.marc

    def json(self) -> dict[str, Any]:
        return self.data


@pytest.fixture
def stub_pymarc_record() -> Record:
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
    return record


@pytest.fixture
def mock_responses(
    monkeypatch, test_bib_data, test_item_data, stub_pymarc_record
) -> None:
    def platform_bib(*args, **kwargs):
        return MockResponse(data={"data": test_bib_data}, marc=b"")

    def platform_items(*args, **kwargs):
        return MockResponse(data={"data": [test_item_data]}, marc=b"")

    def oclc_num_response(*args, **kwargs):
        return MockResponse(
            data={
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
                ]
            },
            marc=b"",
        )

    def pymarc_record(*args, **kwargs) -> MockResponse:
        return MockResponse(data={}, marc=stub_pymarc_record.as_marc())

    monkeypatch.setattr(PlatformSession, "get_bib", platform_bib)
    monkeypatch.setattr(PlatformSession, "get_bib_items", platform_items)
    monkeypatch.setattr(MetadataSession, "brief_bibs_search", oclc_num_response)
    monkeypatch.setattr(MetadataSession, "bib_get", pymarc_record)
