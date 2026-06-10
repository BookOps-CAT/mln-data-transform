from typing import Any

import pytest

from mln_data_transform.models import TeacherSetBook, TeacherSetData


@pytest.fixture
def set_test_data() -> dict[str, Any]:
    return {
        "record_type": "a",
        "control_number": "nn-mlnyc-0000001",
        "language": "eng",
        "grade_level": "Pre-K",
        "shelf_number": "10",
        "set_title": "Foo Bar Teacher Set",
        "copy_number": 1,
        "total_copies": 1,
        "physical_description": "1 item",
        "study_program_info": "Arts & Music",
        "set_type": "Book Club",
        "local_topic_term": ["New York City"],
        "local_genre_term": ["Fiction"],
    }


@pytest.fixture
def subject_test_data() -> list[dict[str, Any]]:
    return [
        {"tag": "650", "ind1": " ", "ind2": "0", "subfields": [("a", "Robots")]},
        {"tag": "650", "ind1": " ", "ind2": "0", "subfields": [("a", "LEGO toys")]},
    ]


@pytest.fixture
def parts_test_data() -> list[dict[str, Any]]:
    return [
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
    ]


class TestTeacherSetData:
    def test_teacher_set_data(self, set_test_data, parts_test_data, subject_test_data):
        parts_test_data[0]["subjects"] = subject_test_data
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        teacher_set = TeacherSetData(**set_test_data)
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Foo Bar", 2 copies of "Test Title".'
        )
        assert teacher_set.control_number == "nn-mlnyc-0000001"
        assert teacher_set.pub_dates == ["2025", "2025"]
        assert teacher_set.language == "eng"
        assert teacher_set.set_title == "Foo Bar Teacher Set"
        assert teacher_set.physical_description == "1 item"
        assert teacher_set.grade_level == "Pre-K"
        assert teacher_set.study_program_info == "Arts & Music"
        assert teacher_set.set_type == "Book Club"
        assert teacher_set.local_topic_term == ["New York City"]
        assert teacher_set.local_genre_term == ["Fiction"]
        assert len(teacher_set.subjects) == 2
        assert teacher_set.location == "ed"
        assert teacher_set.material_type == "8"
        assert teacher_set.bib_code == "e"

    @pytest.mark.parametrize(
        "pub_dates,output", [(("20uu", None), ["20uu"]), ((None, None), [])]
    )
    def test_teacher_set_data_pub_dates(
        self, set_test_data, parts_test_data, pub_dates, output
    ):
        parts_test_data[0]["pub_date"] = pub_dates[0]
        parts_test_data[1]["pub_date"] = pub_dates[1]
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.pub_dates == output
