from typing import Any

import pytest

from mln_data_transform.build import TeacherSetBuilder


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


class TestTeacherSetBuilder:
    def test_create_teacher_sets(
        self, set_test_data, today_str, mock_responses, caplog
    ):
        builder = TeacherSetBuilder(file="data/foo_bar.csv")
        teacher_set = builder.create_teacher_set(**set_test_data)
        set_data = builder.validate_set(teacher_set)
        set_copies = builder.create_set_copies(set_data)
        valid_set_copies = builder.validate_set_copies(set_copies)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(caplog.records) == 10
        # should be 2 x the number of components + 6
        assert [i.msg for i in caplog.records] == [
            "Creating base teacher set for new set: 'Foo Bar Teacher Set'.",
            "Validating set.",
            "Record contains 2 ISBN(s) to query WorldCat.",
            "ISBN 9781234567890: retrieving brief bib record.",
            "ISBN 9781234567890: retrieving full bib record (OCLC number: ocn123456789).",
            "ISBN 9780987654321: retrieving brief bib record.",
            "ISBN 9780987654321: retrieving full bib record (OCLC number: "
            "ocn123456789).",
            "Creating 1 copy/copies of set.",
            "Creating copy 1 of teacher set: Foo Bar Teacher Set.",
            "Validating 1 copy/copies of set.",
        ]
        assert bibs[0].leader == "00000nac  2200000 a 4500"
        assert teacher_set.local_genre_term == ["Fiction"]
        assert teacher_set.local_topic_term == ["New York City"]
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a3 item(s)",
            '=500  \\\\$aSet consists of 1 copy of "This is New York", 2 copies of "This is New York".',
            "=520  \\\\$3This is New York$aFake description of book.",
            "=520  \\\\$3This is New York$aFake description of book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=651  \\0$aNew York (N.Y.)",
            "=655  \\7$aFake genre.$2lcgft",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9781234567890",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_create_teacher_sets_enhanced(
        self, set_test_data, today_str, mock_responses, caplog
    ):
        builder = TeacherSetBuilder(file="data/foo_bar.csv")
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        teacher_set = builder.create_teacher_set(**set_test_data)
        set_data = builder.validate_set(teacher_set)
        set_copies = builder.create_set_copies(set_data)
        valid_set_copies = builder.validate_set_copies(set_copies)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 3
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 1"]
        )
        assert len(bibs) == 1
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\\\\\|\\||eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB E$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 1 copy of "This is New York", 2 copies of "This is New York", 1 Cat puppet(s).',
            "=520  \\\\$3This is New York$aFake description of book.",
            "=520  \\\\$3This is New York$aFake description of book.",
            "=520  \\\\$3Cat puppet$aA puppet.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=651  \\0$aNew York (N.Y.)",
            "=655  \\7$aFake genre.$2lcgft",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9781234567890",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Cat puppet$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_create_teacher_sets_mocked(
        self, mock_teacher_set, today_str, set_test_data
    ):
        builder = TeacherSetBuilder(file="data/foo_bar.csv")
        teacher_set = builder.create_teacher_set(**set_test_data)
        set_data = builder.validate_set(teacher_set)
        set_copies = builder.create_set_copies(set_data)
        valid_set_copies = builder.validate_set_copies(set_copies)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20uu20uuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$nCopy 1 of 1",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 1 copy of "Foo", 1 copy of "Baz".',
            "=520  \\\\$3Foo$aA book.",
            "=520  \\\\$3Baz$aAnother book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=650  \\0$aFake subject.",
            "=655  \\7$aFake genre.$2lcgft",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBar$d1980-$tFoo$f20uu$x9781234567890",
            "=730  02$aBaz$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Baz$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]
