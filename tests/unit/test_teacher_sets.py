from typing import Any

import pytest

from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.teacher_sets import TeacherSet, TeacherSetData


@pytest.fixture
def set_test_data() -> dict[str, Any]:
    return {
        "copies_of_set": 1,
        "grade_level": "Pre-K",
        "language": "eng",
        "set_title": "Foo Bar Teacher Set",
        "parts": [
            {"isbn": "9781234567890", "copies": 1},
            {"copies": 2, "isbn": "9780987654321"},
        ],
        "set_type": "Book Club",
        "study_program_info": "Arts & Music",
        "local_genre_term": ["Fiction"],
        "local_topic_term": ["New York City"],
    }


class TestTeacherSetData:
    def test_teacher_set_data(self, set_test_data):
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.grade_level == GradeReadingLevel("Pre-K")
        assert teacher_set.language == "eng"
        assert teacher_set.local_topic_term == [TaxonomyTopic("New York City")]
        assert teacher_set.local_genre_term == [TaxonomyGenre("Fiction")]
        assert teacher_set.parts[0].isbn == "9781234567890"
        assert len(teacher_set.parts) == 2
        assert teacher_set.record_type == "a"
        assert teacher_set.set_title == "Foo Bar Teacher Set"
        assert teacher_set.set_type == SetTypeFormat("Book Club")
        assert teacher_set.study_program_info == SubjectStudyProgram("Arts & Music")

    def test_teacher_set_data_special_format(self, set_test_data):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.enhanced == "E"
        assert teacher_set.record_type == "o"


class TestTeacherSet:
    def test_create_teacher_set_data(self, mock_responses, caplog, set_test_data):
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(set_data=set_data)
        assert teacher_set.parts[0].author == "Sasek, M."
        assert teacher_set.parts[0].author_dates == "1916-1980"
        assert teacher_set.parts[0].description == "Fake description of book."
        assert teacher_set.parts[0].pub_date == "2003"
        assert len(teacher_set.parts[0].subjects) == 2
        assert teacher_set.physical_description == "3 item(s)"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "This is New York", 2 copies of "This is New York".'
        )

    def test_create_teacher_set_missing_data(
        self, mock_worldcat_response_missing_data, caplog, set_test_data
    ):
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(set_data=set_data)
        assert teacher_set.parts[0].author is None
        assert teacher_set.parts[0].author_dates is None
        assert teacher_set.parts[0].description == ""
        assert teacher_set.parts[0].pub_date == "20uu"
        assert teacher_set.parts[0].subjects == []

    def test_create_teacher_sets_no_pub_dates(
        self, mock_worldcat_response_no_pub_dates, caplog, set_test_data
    ):
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(set_data=set_data)
        assert teacher_set.parts[0].pub_date is None

    def test_create_teacher_special_format(self, mock_responses, caplog, set_test_data):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(set_data=set_data)
        assert teacher_set.parts[-1].title == "Cat puppet"
        assert teacher_set.parts[-1].description == "A puppet"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "This is New York", 2 copies of "This is New York", 1 Cat puppet(s).'
        )
