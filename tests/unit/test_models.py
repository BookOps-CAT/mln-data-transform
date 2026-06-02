from typing import Any

import pytest

from mln_data_transform.models import (
    TeacherSetBib,
    TeacherSetBook,
    TeacherSetData,
    TeacherSetSpecialFormat,
)


@pytest.fixture
def set_test_data() -> dict[str, Any]:
    return {
        "record_type": "a",
        "control_number": "nn-mlnyc-0000001",
        "language": "eng",
        "grade_level": "Pre-K",
        "shelf_number": "10",
        "set_title": "Foo Bar Teacher Set",
        "enumeration": "1-1",
        "physical_description": "1 item",
        "study_program_info": "Arts & Music",
        "set_type": "Book Club",
        "local_topic_term": ["New York City"],
        "local_genre_term": ["Fiction"],
    }


@pytest.fixture
def subject_test_data() -> list[dict[str, Any]]:
    return [
        {
            "tag": "690",
            "ind1": " ",
            "ind2": "7",
            "subfields": [("a", "Topic"), ("2", "bookops")],
        },
        {
            "tag": "691",
            "ind1": " ",
            "ind2": "7",
            "subfields": [("a", "Language Arts"), ("2", "bookops")],
        },
    ]


@pytest.fixture
def parts_test_data() -> list[dict[str, Any]]:
    return [
        {
            "full_title": "Foo Bar : Baz",
            "title": "Foo Bar",
            "author": "Baz",
            "copies": 1,
            "isbn": "9781234567890",
            "description": "A book.",
            "author_dates": "2020-",
            "pub_date": "2025",
        },
        {
            "full_title": "Test Title : Subtitle",
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
        assert teacher_set.leader == "00000nac  2200000 a 4500"
        assert teacher_set.control_number == "nn-mlnyc-0000001"
        assert teacher_set.pub_dates == ["2025", "2025"]
        assert teacher_set.language == "eng"
        assert str(teacher_set.call_number) == "MLNYC ART CLUB A 10"
        assert teacher_set.set_title == "Foo Bar Teacher Set"
        assert teacher_set.copy_data == "Copy 1 of 1"
        assert teacher_set.physical_description == "1 item"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Foo Bar", 2 copies of "Test Title".'
        )
        assert teacher_set.grade_level == "Pre-K"
        assert teacher_set.study_program_info == "Arts & Music"
        assert teacher_set.set_type == "Book Club"
        assert teacher_set.local_topic_term == ["New York City"]
        assert teacher_set.local_genre_term == ["Fiction"]
        assert len(teacher_set.subjects) == 2
        assert teacher_set.library == "nypl"
        assert teacher_set.control_number_identifier == "BookOps"
        assert teacher_set.pub_place == "xxu"
        assert teacher_set.catalogers_initials == "mlnyc-bot"
        assert teacher_set.local_collection_code == "BL"
        assert teacher_set.oclc_exclusion_note == "OCLC Holdings Exclusion"
        assert teacher_set.location == "ed"
        assert teacher_set.material_type == "8"
        assert teacher_set.bib_code == "e"
        assert teacher_set.call_number.format == "CLUB"
        assert teacher_set.call_number.grade_level == "A"
        assert teacher_set.call_number.shelf_number == "10"
        assert teacher_set.call_number.subject_code == "ART"
        assert teacher_set.call_number.enhanced is None

    def test_teacher_set_data_enhanced(self, set_test_data, parts_test_data):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_test_data["parts"].append(
            TeacherSetSpecialFormat(
                title="Sock puppet", copies=1, description="A puppet."
            )
        )
        set_test_data["enhanced"] = "E"
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert str(teacher_set.call_number) == "MLNYC ART CLUB E A 10"
        assert teacher_set.call_number.sub_f == "CLUB E"
        assert "=730  02$aSock puppet" in field_strings

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

    def test_teacher_set_bib(self, set_test_data, parts_test_data, today_str):
        parts_test_data[0]["subjects"] = [
            {"tag": "650", "ind1": " ", "ind2": "0", "subfields": [("a", "Robots")]}
        ]
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i20252025xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=650  \\0$aRobots",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=910  \\\\$aBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
        ]

    def test_teacher_set_bib_kit(self, set_test_data, parts_test_data):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_test_data["record_type"] = "o"
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        assert bib.leader == "00000noc  2200000 a 4500"

    def test_teacher_set_bib_no_pub_dates(
        self, set_test_data, parts_test_data, today_str
    ):
        parts_test_data[0]["pub_date"] = None
        parts_test_data[1]["pub_date"] = None
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$x9781234567890",
            "=700  12$aFoo$tTest Title$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=910  \\\\$aBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
        ]

    def test_teacher_set_bib_no_local_subjects(
        self, set_test_data, parts_test_data, today_str
    ):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_test_data["local_topic_term"] = None
        set_test_data["local_genre_term"] = None
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i20252025xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=690  \\7$aBook Club$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=910  \\\\$aBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
        ]
