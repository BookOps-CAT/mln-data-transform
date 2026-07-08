from mln_data_transform.taxonomy import (
    GradeReadingLevel,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mln_data_transform.teacher_sets import TeacherSet, TeacherSetData


class TestTeacherSetData:
    def test_teacher_set_data(self, set_test_data):
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.grade_level == GradeReadingLevel("Pre-K")
        assert teacher_set.language == "eng"
        assert teacher_set.local_topic_term == [TaxonomyTopic("New York City")]
        assert teacher_set.local_genre_term == [TaxonomyGenre("Fiction")]
        assert teacher_set.parts[0].id == "9781234567897"
        assert len(teacher_set.parts) == 2
        assert teacher_set.record_type == "a"
        assert teacher_set.set_title == "Foo Bar Teacher Set"
        assert teacher_set.set_type == SetTypeFormat("Book Club")
        assert teacher_set.study_program_info == SubjectStudyProgram("Social Studies")

    def test_teacher_set_data_special_format(self, set_test_data):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.enhanced == "E"
        assert teacher_set.record_type == "o"

    def test_teacher_set_data_get_parts(self, set_test_data, mock_session_managers):
        teacher_set = TeacherSetData(**set_test_data)
        worldcat_parts = teacher_set.get_worldcat_data_for_parts()
        assert len(worldcat_parts) == 2
        assert worldcat_parts[0]["author_name"] == "Bar, Foo"
        assert worldcat_parts[0]["author_dates"] == "1980-"
        assert worldcat_parts[0]["description"] == "Fake description of book."
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
        assert len(teacher_set.parts) == 2
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
        assert teacher_set.physical_description == "4 item(s)"
        assert (
            teacher_set.contents_note
            == 'Set consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".'
        )

    def test_teacher_set_special_format(
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
            == 'Set consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2", 1 Cat puppet(s).'
        )

    def test_teacher_set_single_copy(
        self, set_test_data, mock_worldcat_response, caplog
    ):
        mock_worldcat_response[0]["copies"] = 1
        mock_worldcat_response[1]["copies"] = 1
        set_test_data["parts"][0]["copies"] = 1
        set_test_data["parts"][1]["copies"] = 1
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        assert len(teacher_set.parts) == 2
        assert teacher_set.physical_description == "2 item(s)"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Fake book 1", 1 copy of "Fake book 2".'
        )
