import datetime
import json
from typing import Any

import pytest


@pytest.fixture
def test_bib_data() -> dict[str, Any]:
    with open("tests/data/platform_bib.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def test_bib_multi_isbn() -> dict[str, Any]:
    with open("tests/data/platform_bib_multi_isbn.json", "r") as fh:
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
