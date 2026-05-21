import json
from typing import Any

import pytest


@pytest.fixture
def platform_test_data() -> dict[str, Any]:
    with open("tests/platform_bib.json", "r") as fh:
        json_data = json.load(fh)
        return json_data
