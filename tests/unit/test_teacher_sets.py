from typing import Any

import pytest

from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.teacher_sets import TeacherSetData, TeacherSetSpecialFormat


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
            TeacherSetSpecialFormat(
                title="Cat puppet", description="A puppet", copies=1
            )
        ]
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.enhanced == "E"
        assert teacher_set.record_type == "o"

    # @pytest.mark.parametrize(
    #     "pub_dates,output", [(("20uu", None), ["20uu"]), ((None, None), [])]
    # )
    # def test_teacher_set_data_pub_dates(
    #     self, set_test_data, parts_test_data, pub_dates, output
    # ):
    #     parts_test_data[0]["pub_date"] = pub_dates[0]
    #     parts_test_data[1]["pub_date"] = pub_dates[1]
    #     set_test_data["parts"] = [WorldcatSetPart(**i) for i in parts_test_data]
    #     teacher_set = TeacherSetData(**set_test_data)
    #     assert teacher_set.pub_dates == output

    # def test_teacher_set_data_no_subjects(self, set_test_data, parts_test_data):
    #     parts_test_data[0]["subjects"] = {}
    #     set_test_data["parts"] = [WorldcatSetPart(**i) for i in parts_test_data]
    #     teacher_set = TeacherSetData(**set_test_data)
    #     assert teacher_set.subjects == []
