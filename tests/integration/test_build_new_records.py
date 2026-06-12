from typing import Any

import pytest

from mln_data_transform.components import TeacherSetBook, TeacherSetSpecialFormat
from mln_data_transform.models import TeacherSetData
from mln_data_transform.validate import TeacherSetCopyModel


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
        "copies_of_set": 1,
        "physical_description": "1 item",
        "study_program_info": "Arts & Music",
        "set_type": "Book Club",
        "local_topic_term": ["New York City"],
        "local_genre_term": ["Fiction"],
    }


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
        {
            "title": "Another Book",
            "copies": 2,
            "isbn": "9780000000000",
            "description": "Yet another book.",
            "pub_date": "2025",
        },
    ]


class TestNewTeacherSetFromModel:
    def test_teacher_set_bib(self, set_test_data, parts_test_data, today_str, caplog):
        parts_test_data[0]["subjects"] = [
            {"tag": "650", "ind1": " ", "ind2": "0", "subfields": [("a", "Robots")]}
        ]
        parts_test_data[1]["subjects"] = [
            {"tag": "650", "ind1": " ", "ind2": "0", "subfields": [("a", "Robots")]}
        ]
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSetCopyModel(**set_data.to_dict())
        set_bib = teacher_set.to_set_bib()
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert teacher_set.local_genre_term == ["Fiction"]
        assert teacher_set.local_topic_term == ["New York City"]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i20252025xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title", 2 copies of "Another Book".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=520  \\\\$3Another Book$aYet another book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=650  \\0$aRobots",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=730  02$aAnother Book$f2025$x9780000000000",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo Bar$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_bib_kit(self, set_test_data, parts_test_data, today_str):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_test_data["parts"].append(
            TeacherSetSpecialFormat(copies=1, description="A puppet", title="Puppet")
        )
        set_test_data["record_type"] = "o"
        set_test_data["enhanced"] = "E"
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSetCopyModel(**set_data.to_dict())
        set_bib = teacher_set.to_set_bib()
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000noc  2200000 a 4500"
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i20252025xxu\\\\\\\\\\\\\\\\\\\\\\\\\\|\\||eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB E$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title", 2 copies of "Another Book".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=520  \\\\$3Another Book$aYet another book.",
            "=520  \\\\$3Puppet$aA puppet.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=730  02$aAnother Book$f2025$x9780000000000",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo Bar$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Puppet$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_bib_no_pub_dates(
        self, set_test_data, parts_test_data, today_str
    ):
        parts_test_data[0]["pub_date"] = None
        parts_test_data[1]["pub_date"] = None
        parts_test_data[2]["pub_date"] = None
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSetCopyModel(**set_data.to_dict())
        set_bib = teacher_set.to_set_bib()
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
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title", 2 copies of "Another Book".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=520  \\\\$3Another Book$aYet another book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$x9781234567890",
            "=700  12$aFoo$tTest Title$x9780987654321",
            "=730  02$aAnother Book$x9780000000000",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo Bar$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_bib_no_local_subjects(
        self, set_test_data, parts_test_data, today_str
    ):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_test_data["local_topic_term"] = None
        set_test_data["local_genre_term"] = None
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSetCopyModel(**set_data.to_dict())
        set_bib = teacher_set.to_set_bib()
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert teacher_set.local_genre_term is None
        assert teacher_set.local_topic_term is None
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i20252025xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title", 2 copies of "Another Book".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=520  \\\\$3Another Book$aYet another book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=690  \\7$aBook Club$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=730  02$aAnother Book$f2025$x9780000000000",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo Bar$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_bib_with_local_subjects(
        self, set_test_data, parts_test_data, today_str
    ):
        set_test_data["local_topic_term"] = ["New York City"]
        set_test_data["local_genre_term"] = ["Fiction"]
        set_test_data["parts"] = [TeacherSetBook(**i) for i in parts_test_data]
        set_data = TeacherSetData(**set_test_data)
        teacher_set = TeacherSetCopyModel(**set_data.to_dict())
        set_bib = teacher_set.to_set_bib()
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert teacher_set.local_genre_term == ["Fiction"]
        assert teacher_set.local_topic_term == ["New York City"]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i20252025xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c10",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title", 2 copies of "Another Book".',
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=520  \\\\$3Another Book$aYet another book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=730  02$aAnother Book$f2025$x9780000000000",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo Bar$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Test Title$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Another Book$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]
