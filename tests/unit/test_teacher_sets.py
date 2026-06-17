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
            {"isbn": "9781234567897", "copies": 1},
            {"copies": 2, "isbn": "9780987654328"},
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
        assert teacher_set.parts[0].isbn == "9781234567897"
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

    def test_teacher_set_data_get_parts(self, set_test_data, stub_metadata_session):
        teacher_set = TeacherSetData(**set_test_data)
        worldcat_parts = teacher_set.get_worldcat_data_for_parts()
        assert len(worldcat_parts) == 2
        assert worldcat_parts[0]["author_name"] == "Bar, Foo"
        assert worldcat_parts[0]["author_dates"] == "1980-"
        assert worldcat_parts[0]["description"] == "Fake description of book."
        assert worldcat_parts[0]["isbn"] == "9781234567897"
        assert worldcat_parts[0]["pub_date"] == "2000"
        assert worldcat_parts[0]["subjects"] == [
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
        ]
        assert worldcat_parts[0]["title"] == "Fake book 1"


class TestTeacherSet:
    def test_teacher_set(self, set_test_data, mock_worldcat_response, caplog):
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        assert teacher_set.parts[0].author == "Bar, Foo"
        assert teacher_set.parts[0].author_dates == "1980-"
        assert teacher_set.parts[0].description == "Fake description of book."
        assert teacher_set.parts[0].pub_date == "2000"
        assert len(teacher_set.parts[0].subjects) == 2
        assert teacher_set.parts[0].subjects == [
            {
                "ind1": " ",
                "ind2": "0",
                "subfields": [("a", "New York (N.Y.)")],
                "tag": "651",
            },
            {
                "ind1": " ",
                "ind2": "7",
                "subfields": [("a", "Comics (Graphic works)."), ("2", "lcgft")],
                "tag": "655",
            },
        ]
        assert teacher_set.physical_description == "3 item(s)"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Fake book 1", 2 copies of "Fake book 2".'
        )

    def test_teacher_special_format(
        self, set_test_data, mock_worldcat_response, caplog
    ):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        assert teacher_set.parts[-1].title == "Cat puppet"
        assert teacher_set.parts[-1].description == "A puppet"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Fake book 1", 2 copies of "Fake book 2", 1 Cat puppet(s).'
        )
