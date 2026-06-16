import os
from typing import Any, Generator

import pytest
from dotenv import load_dotenv

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

    def test_create_teacher_sets_mocked_parts(
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

    def test_create_legacy_sets(self, mock_legacy_set, today_str):
        builder = TeacherSetBuilder(file="data/foo_bar.csv")
        legacy_set = builder.create_legacy_set(bib_id="12345678")
        set_data = builder.validate_set(legacy_set)
        set_copies = builder.create_set_copies(set_data)
        valid_set_copies = builder.validate_set_copies(set_copies)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 1
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Teacher Set. Copy 1 of 2", "Teacher Set. Copy 2 of 2"]
        )
        assert len(bibs) == 2
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fTOPIC$pA$c1",
            "=245  00$aTeacher Set.$nCopy 1 of 2",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Foo".',
            "=520  \\\\$3Foo$aA book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=650  \\0$aFake subject.",
            "=655  \\7$aFake genre.$2lcgft",
            "=690  \\7$aTopic$2bookops",
            "=700  12$aBar$tFoo$x9781234567890",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Foo$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_legacy_set_no_subjects(
        self, mock_legacy_set_no_subjects, today_str, caplog
    ):
        builder = TeacherSetBuilder(file="data/foo_bar.csv")
        legacy_set = builder.create_legacy_set(bib_id="12345678")
        set_data = builder.validate_set(legacy_set)
        set_copies = builder.create_set_copies(set_data)
        valid_set_copies = builder.validate_set_copies(set_copies)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 1
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Teacher Set. Copy 1 of 2", "Teacher Set. Copy 2 of 2"]
        )
        assert len(bibs) == 2
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fTOPIC$pA$c1",
            "=245  00$aTeacher Set.$nCopy 1 of 2",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Foo".',
            "=520  \\\\$3Foo$aA book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aTopic$2bookops",
            "=700  12$aBar$tFoo$x9781234567890",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Foo$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Foo$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]


@pytest.fixture(scope="class")
def live_creds() -> Generator[None, None, None]:
    load_dotenv()
    yield
    os.environ["NYPL_PLATFORM_CLIENT"] = "platform_client"
    os.environ["NYPL_PLATFORM_SECRET"] = "platform_secret"
    os.environ["NYPL_PLATFORM_OAUTH"] = "fakeurl"
    os.environ["WORLDCAT_KEY"] = "worldcat_key"
    os.environ["WORLDCAT_SECRET"] = "worldcat_secret"


@pytest.mark.livetest
class TestLiveTeacherSetBuilder:
    BUILDER = TeacherSetBuilder(file="tests/data/high_circ.csv")

    def test_legacy_set_builder_this_is_ny(self, today_str, caplog, live_creds):
        teacher_set = self.BUILDER.create_legacy_set(bib_id="19538471")
        valid_set_bib = self.BUILDER.validate_set(teacher_set)
        set_copies = self.BUILDER.create_set_copies(valid_set_bib)
        valid_set_copies = self.BUILDER.validate_set_copies(set_copies)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert len(valid_set_copies[0].components) == 1
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            [
                "This is New York by M. Sasek. Copy 1 of 7",
                "This is New York by M. Sasek. Copy 2 of 7",
                "This is New York by M. Sasek. Copy 3 of 7",
                "This is New York by M. Sasek. Copy 4 of 7",
                "This is New York by M. Sasek. Copy 5 of 7",
                "This is New York by M. Sasek. Copy 6 of 7",
                "This is New York by M. Sasek. Copy 7 of 7",
            ]
        )
        assert len(bib_records) == 7
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c358",
            "=245  00$aThis is New York by M. Sasek.$nCopy 1 of 7",
            "=300  \\\\$a10 item(s)",
            '=500  \\\\$aSet consists of 10 copies of "This is New York".',
            "=520  \\\\$3This is New York$aA pictorial tour of Manhattan Island presenting drawings of its neighborhoods, transportation and traffic, buildings, and the city's activities, from the local shoeshine stall to Wall Street.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=651  \\0$aNew York (N.Y.)$xDescription and travel$vJuvenile literature.",
            "=655  \\0$aPicture books for children.$5NZ-WeK",
            "=655  \\7$aLiterature.$2lcgft",
            "=655  \\7$aIllustrated works.$2lcgft",
            "=690  \\7$aBook Club$2bookops",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9780789308849",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333402207449$oTeacher Set SOC A Book Club Set NYC History - This Is New York 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-This is New York$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]
        assert len(caplog.records) == 17
        assert [i.msg for i in caplog.records] == [
            "Creating base teacher set for 19538471.",
            "Getting bib record from platform for 19538471.",
            "Getting items from platform for 19538471.",
            "7 item records found for bib b19538471a.",
            "Validating set.",
            "Record contains 1 ISBN(s) to query WorldCat.",
            "ISBN 9780789308849: retrieving brief bib record.",
            "ISBN 9780789308849: retrieving full bib record (OCLC number: 52510777).",
            "Creating 7 copy/copies of set.",
            "Creating copy 1 of legacy set: 19538471.",
            "Creating copy 2 of legacy set: 19538471.",
            "Creating copy 3 of legacy set: 19538471.",
            "Creating copy 4 of legacy set: 19538471.",
            "Creating copy 5 of legacy set: 19538471.",
            "Creating copy 6 of legacy set: 19538471.",
            "Creating copy 7 of legacy set: 19538471.",
            "Validating 7 copy/copies of set.",
        ]

    def test_legacy_set_builder_ancient_civ(self, today_str, caplog, live_creds):
        teacher_set = self.BUILDER.create_legacy_set(bib_id="20895133")
        valid_set_bib = self.BUILDER.validate_set(teacher_set)
        set_copies = self.BUILDER.create_set_copies(valid_set_bib)
        valid_set_copies = self.BUILDER.validate_set_copies(set_copies)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert len(valid_set_copies[0].components) == 8
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            [
                "Ancient Civilizations. Copy 1 of 8",
                "Ancient Civilizations. Copy 2 of 8",
                "Ancient Civilizations. Copy 3 of 8",
                "Ancient Civilizations. Copy 4 of 8",
                "Ancient Civilizations. Copy 5 of 8",
                "Ancient Civilizations. Copy 6 of 8",
                "Ancient Civilizations. Copy 7 of 8",
                "Ancient Civilizations. Copy 8 of 8",
            ]
        )
        assert len(bib_records) == 8
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20152015xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fTOPIC$pC$c1072",
            "=245  00$aAncient Civilizations.$nCopy 1 of 8",
            "=300  \\\\$a8 item(s)",
            '=500  \\\\$aSet consists of 1 copy of "Ancient Rome", 1 copy of "Ancient Mesopotamia", 1 copy of "Ancient Maya", 1 copy of "Ancient India", 1 copy of "Ancient Greece", 1 copy of "Ancient Egypt", 1 copy of "Ancient China", 1 copy of "Ancient Aztecs".',
            "=520  \\\\$3Ancient Rome$aIn Ancient Rome, readers discover the history and impressive accomplishments of the ancient Romans, including their military power and feats of engineering. Text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.",
            "=520  \\\\$3Ancient Mesopotamia$a\"In Ancient Mesopotamia, readers discover the history and impressive accomplishments of the ancient Mesopotamians, including their extraordinary cultural achievements and technological wonders. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
            "=520  \\\\$3Ancient Maya$a\"In Ancient Maya, readers discover the history and impressive accomplishments of the Maya people, including their advanced mathematics and massive stone cities. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
            "=520  \\\\$3Ancient India$a\"In Ancient India, readers discover the history and impressive accomplishments of the people of ancient India, including their enduring religions and rich literary traditions. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
            "=520  \\\\$3Ancient Greece$aReaders will discover the history and accomplishments of the people of ancient Greece, including their cultural achievements and feats of construction.",
            "=520  \\\\$3Ancient Egypt$a\"In Ancient Egypt, readers discover the history and impressive accomplishments of the people of ancient Egypt, including their extraordinary cultural achievements and feats of construction. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
            "=520  \\\\$3Ancient China$a\"In Ancient China, readers discover the history and impressive accomplishments of the people of ancient China, including their technological wonders and feats of construction. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
            "=520  \\\\$3Ancient Aztecs$a\"In Ancient Aztecs, readers discover the history and impressive accomplishments of the Aztec civilization, including their military power and feats of engineering. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
            "=521  2\\$a3-5",
            "=526  8\\$aSocial Studies",
            "=650  \\0$aMayas$vJuvenile literature.",
            "=650  \\0$aAztecs$vJuvenile literature.",
            "=651  \\0$aRome$xCivilization.",
            "=651  \\0$aRome$xHistory.",
            "=651  \\0$aRome$xSocial life and customs.",
            "=651  \\0$aIraq$xCivilization$yTo 634$vJuvenile literature.",
            "=651  \\0$aMexico$xCivilization$vJuvenile literature.",
            "=651  \\0$aCentral America$xCivilization$vJuvenile literature.",
            "=651  \\0$aIndia$xCivilization$yTo 1200$vJuvenile literature.",
            "=651  \\0$aGreece$xCivilization$yTo 146 B.C.$vJuvenile literature.",
            "=651  \\0$aEgypt$xCivilization$yTo 332 B.C.$vJuvenile literature.",
            "=651  \\0$aChina$xCivilization$yTo 221 B.C.$vJuvenile literature.",
            "=651  \\0$aChina$xCivilization$y221 B.C.-960 A.D.$vJuvenile literature.",
            "=655  \\7$aLiterature.$2lcgft",
            "=655  \\7$aHistory.$0(OCoLC)fst01411628$2lcgft",
            "=655  \\7$aJuvenile works.$0(OCoLC)fst01411637$2lcgft",
            "=690  \\7$aTopic$2bookops",
            "=700  12$aHamen, Susan E.$tAncient Rome$f2015$x9781624035425",
            "=700  12$aHead, Tom$tAncient Mesopotamia$f2015$x9781624035418",
            "=700  12$aEdwards, Sue Bradford$tAncient Maya$f2015$x9781624035401",
            "=700  12$aRowell, Rebecca$tAncient India$f2015$x9781624035395",
            "=700  12$aBailey, Diane$d1966-$tAncient Greece$f2015$x9781624035388",
            "=700  12$aAmstutz, Lisa J.$tAncient Egypt$f2015$x9781624035371",
            "=700  12$aAtkins, Marcie Flinchum$tAncient China$f2015$x9781624035364",
            "=700  12$aKenney, Karen Latchana$tAncient Aztecs$f2015$x9781624035357",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333408154165$oTeacher Set SOC C Ancient Civilizations 2-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Ancient Rome$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient Mesopotamia$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient Maya$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient India$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient Greece$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient Egypt$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient China$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Ancient Aztecs$leduls$mm$p0.00$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]
        assert len(caplog.records) == 32
        assert [i.msg for i in caplog.records] == [
            "Creating base teacher set for 20895133.",
            "Getting bib record from platform for 20895133.",
            "Getting items from platform for 20895133.",
            "8 item records found for bib b20895133a.",
            "Validating set.",
            "Record contains 8 ISBN(s) to query WorldCat.",
            "ISBN 9781624035425: retrieving brief bib record.",
            "ISBN 9781624035425: retrieving full bib record (OCLC number: 911497614).",
            "ISBN 9781624035418: retrieving brief bib record.",
            "ISBN 9781624035418: retrieving full bib record (OCLC number: 904347324).",
            "ISBN 9781624035401: retrieving brief bib record.",
            "ISBN 9781624035401: retrieving full bib record (OCLC number: 904346699).",
            "ISBN 9781624035395: retrieving brief bib record.",
            "ISBN 9781624035395: retrieving full bib record (OCLC number: 891122638).",
            "ISBN 9781624035388: retrieving brief bib record.",
            "ISBN 9781624035388: retrieving full bib record (OCLC number: 914136830).",
            "ISBN 9781624035371: retrieving brief bib record.",
            "ISBN 9781624035371: retrieving full bib record (OCLC number: 914136829).",
            "ISBN 9781624035364: retrieving brief bib record.",
            "ISBN 9781624035364: retrieving full bib record (OCLC number: 891122570).",
            "ISBN 9781624035357: retrieving brief bib record.",
            "ISBN 9781624035357: retrieving full bib record (OCLC number: 891122602).",
            "Creating 8 copy/copies of set.",
            "Creating copy 1 of legacy set: 20895133.",
            "Creating copy 2 of legacy set: 20895133.",
            "Creating copy 3 of legacy set: 20895133.",
            "Creating copy 4 of legacy set: 20895133.",
            "Creating copy 5 of legacy set: 20895133.",
            "Creating copy 6 of legacy set: 20895133.",
            "Creating copy 7 of legacy set: 20895133.",
            "Creating copy 8 of legacy set: 20895133.",
            "Validating 8 copy/copies of set.",
        ]
