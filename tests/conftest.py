import datetime
import json
from typing import Any

import pytest


@pytest.fixture
def platform_test_data() -> dict[str, Any]:
    with open("tests/data/platform_bib.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def test_data() -> dict[str, Any]:
    with open("tests/data/test_data.json", "r") as fh:
        json_data = json.load(fh)
        return json_data


@pytest.fixture
def set_test_data() -> dict[str, Any]:
    return {
        "record_type": "a",
        "control_number": "nn-mlnyc-0000001",
        "begin_pub_date": "200101",
        "end_pub_date": "200102",
        "language": "eng",
        "grade_level": "Pre-K",
        "shelf_number": "10",
        "set_title": "Foo Bar Teacher Set",
        "enumeration": "1-1",
        "physical_description": "1 item",
        "study_program_info": "Arts & Music",
        "bib_id": "b123456789",
        "local_set_type": "Book Club",
        "local_topic_term": ["New York City"],
        "local_genre_term": ["Fiction"],
        "items": [],
        "subjects": [],
        "parts": [
            {
                "title": "Foo Bar",
                "author": "Baz",
                "copies": 1,
                "isbn": "9781234567890",
                "description": "A book.",
                "author_dates": "2020-",
                "pub_date": "2025",
            },
            {
                "title": "Test Title",
                "author": "Foo",
                "copies": 2,
                "isbn": "9780987654321",
                "description": "Another book.",
                "pub_date": "2025",
            },
        ],
    }


@pytest.fixture
def today_str() -> str:
    return datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")
