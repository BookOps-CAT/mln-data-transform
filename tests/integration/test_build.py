import copy
import os
from typing import Generator

import pytest
from dotenv import load_dotenv

from mln_data_transform.build import TeacherSetBuilder


class TestTeacherSetBuilder:
    BUILDER = TeacherSetBuilder(file="data/foo_bar.csv")

    def test_build_teacher_sets(self, set_test_data, mock_set):
        teacher_set = self.BUILDER.build_teacher_set(**set_test_data)
        valid_set_copies = self.BUILDER.build_set_copies(teacher_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert teacher_set["parts"][0]["subjects"] == [
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
                "subfields": [("a", "Historical fiction."), ("2", "lcgft")],
            },
        ]
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert teacher_set["local_genre_term"] == ["Fiction"]
        assert teacher_set["local_topic_term"] == ["New York City"]
        assert len(bibs) == 2
        assert len(field_strings) == 24
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20002000xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo,$d1980-$tFake book 1.$f2000.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_teacher_sets_enhanced(self, set_test_data, mock_set):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        teacher_set = self.BUILDER.build_teacher_set(**set_test_data)
        valid_set_copies = self.BUILDER.build_set_copies(teacher_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 3
        assert teacher_set["parts"][0]["subjects"] == [
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
                "subfields": [("a", "Historical fiction."), ("2", "lcgft")],
            },
        ]
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 26
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20002000xxu\\\\\\\\\\\\\\\\\\\\\\\\\\|\\||eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB E$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a5 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2", 1 Cat puppet(s).',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=520  \\\\$3Cat puppet$aA puppet.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo,$d1980-$tFake book 1.$f2000.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Cat puppet$nCat puppet$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_teacher_sets_missing_info(
        self, set_test_data, mock_set_missing_info
    ):
        teacher_set = self.BUILDER.build_teacher_set(**set_test_data)
        valid_set_copies = self.BUILDER.build_set_copies(set_data=teacher_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 24
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20uu20uuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_teacher_sets_no_dates(self, set_test_data, mock_set_no_dates):
        teacher_set = self.BUILDER.build_teacher_set(**set_test_data)
        valid_set_copies = self.BUILDER.build_set_copies(set_data=teacher_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 24
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo.$tFake book 1.$x9781234567897",
            "=730  02$aFake book 2.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    @pytest.mark.parametrize(
        "title,field_245",
        [
            ("A Title", "2$aA Title."),
            ("L'Title", "2$aL'Title."),
            ("An Alternative Title", "3$aAn Alternative Title."),
            ("El Title", "3$aEl Title."),
            ("La Title", "3$aLa Title."),
            ("Le Title", "3$aLe Title."),
            ("The Titles", "4$aThe Titles."),
            ("Las Titles", "4$aLas Titles."),
            ("Los Titles", "4$aLos Titles."),
            ("Les Titles", "4$aLes Titles."),
            ("Title!", "0$aTitle!"),
            ("Title?", "0$aTitle?"),
        ],
    )
    def test_build_teacher_sets_title_variants(
        self, set_test_data, mock_set, title, field_245
    ):
        set_data = copy.deepcopy(set_test_data)
        set_data["set_title"] = title
        teacher_set = self.BUILDER.build_teacher_set(**set_data)
        valid_set_copies = self.BUILDER.build_set_copies(teacher_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20002000xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            f"=245  0{field_245}$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo,$d1980-$tFake book 1.$f2000.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets(self, mock_set):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert legacy_set["local_genre_term"] == ["Fiction"]
        assert legacy_set["local_topic_term"] == ["New York City"]
        assert len(bibs) == 2
        assert len(field_strings) == 25
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20002000xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c1",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo,$d1980-$tFake book 1.$f2000.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar Book Club 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets_enhanced(self, mock_set_enhanced):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 3
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert legacy_set["local_genre_term"] == ["Fiction"]
        assert legacy_set["local_topic_term"] == ["New York City"]
        assert len(bibs) == 2
        assert len(field_strings) == 28
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20002000xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ELA$fCLUB$pD$c1",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s) + 1 DVD",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2", 1 copy of "Fake DVD [DVD]".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=520  \\\\$3Fake DVD$aA fake description of a DVD.",
            "=521  2\\$a6-8",
            "=526  8\\$aLanguage Arts",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo,$d1980-$tFake book 1.$f2000.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=730  02$aFake DVD.$f20uu.$x9789876543217",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar Book Club 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake DVD [DVD]$nFake DVD [DVD]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets_enhanced_missing_identifier(
        self, mock_set_enhanced_missing_identifier
    ):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 27
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20uu20uuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ELA$fCLUB$pD$c1",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s) + 4 Playaways",
            '=500  \\\\$aSet consists of 4 copies of "Fake book 1", 4 copies of "Playaway (missing identifier) [Playaway audiobook]".',
            "=520  \\\\$3Fake book 1$aA fake description of a book.",
            "=520  \\\\$3Playaway (missing identifier) [Playaway audiobook].",
            "=521  2\\$a6-8",
            "=526  8\\$aLanguage Arts",
            "=690  \\7$aBook Club.$2bookops",
            "=730  02$aFake book 1.$f20uu.$x9780987654328",
            "=730  02$aPlayaway (missing identifier)$xNone",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar Book Club 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Playaway (missing identifier) [Playaway audiobook]$nPlayaway (missing identifier) [Playaway audiobook]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Playaway (missing identifier) [Playaway audiobook]$nPlayaway (missing identifier) [Playaway audiobook]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Playaway (missing identifier) [Playaway audiobook]$nPlayaway (missing identifier) [Playaway audiobook]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Playaway (missing identifier) [Playaway audiobook]$nPlayaway (missing identifier) [Playaway audiobook]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets_missing_info(self, mock_set_missing_info):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 23
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20uu20uuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c1",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar Book Club 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets_no_dates(self, mock_set_no_dates):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 23
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c1",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=700  12$aBar, Foo.$tFake book 1.$x9781234567897",
            "=730  02$aFake book 2.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar Book Club 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets_multiple(self, mock_set, tmp_path):
        fake_file = tmp_path / "legacy_sets.mrc"
        for bib_id in self.BUILDER.all_bib_ids[:2]:
            legacy_set = self.BUILDER.build_legacy_set(bib_id=bib_id)
            valid_set_copies = self.BUILDER.build_set_copies(legacy_set)
            self.BUILDER.write_marc_to_file(
                set_bibs=valid_set_copies, out_file=fake_file
            )
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            ["Foo Bar Teacher Set. Copy 1 of 2", "Foo Bar Teacher Set. Copy 2 of 2"]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            ["nn-mlnyc-0000001", "nn-mlnyc-0000001"]
        )
        assert len(bibs) == 2
        assert len(field_strings) == 25
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i20002000xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c1",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a4 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".',
            "=520  \\\\$3Fake book 1$aFake description of book.",
            "=520  \\\\$3Fake book 2$aAnother fake description of a book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aNew York City.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aBar, Foo,$d1980-$tFake book 1.$f2000.$x9781234567897",
            "=730  02$aFake book 2.$f20uu.$x9780987654328",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333987654321$oTeacher Set SOC A Foo Bar Book Club 1-1",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 2$nFake book 2$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]


class TestTeacherSetBuilderLogging:
    BUILDER = TeacherSetBuilder(file="data/foo_bar.csv")

    def test_build_teacher_sets(
        self, set_test_data, mock_session_managers, caplog, mock_location_mapping
    ):
        teacher_set = self.BUILDER.build_teacher_set(**set_test_data)
        self.BUILDER.build_set_copies(teacher_set)
        assert len(caplog.records) == 2
        assert [i.msg for i in caplog.records] == [
            "Building teacher set from new data: 'Foo Bar Teacher Set'.",
            "(nn-mlnyc-0000001) Created 2 valid copy/copies of set.",
        ]

    def test_build_legacy_sets(
        self, mock_session_managers, caplog, mock_location_mapping
    ):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        self.BUILDER.build_set_copies(set_data=legacy_set)
        assert len(caplog.records) == 2
        assert [i.msg for i in caplog.records] == [
            "(12345678) Building teacher set from legacy data.",
            "(12345678) Created 2 valid copy/copies of set.",
        ]

    def test_build_teacher_sets_debug(
        self, set_test_data, mock_session_managers, caplog, mock_location_mapping
    ):
        caplog.set_level("DEBUG")
        teacher_set = self.BUILDER.build_teacher_set(**set_test_data)
        self.BUILDER.build_set_copies(teacher_set)
        assert len(caplog.records) == 7
        assert [i.msg for i in caplog.records] == [
            "Building teacher set from new data: 'Foo Bar Teacher Set'.",
            "ISBN/UPC 9781234567897: retrieving brief bib record.",
            "ISBN/UPC 9781234567897: retrieving full bib record (OCLC number: ocn123456789).",
            "ISBN/UPC 9780987654328: retrieving brief bib record.",
            "ISBN/UPC 9780987654328: retrieving full bib record (OCLC number: ocn123456789).",
            "(nn-mlnyc-0000001) Creating 2 copy/copies of set.",
            "(nn-mlnyc-0000001) Created 2 valid copy/copies of set.",
        ]

    def test_build_legacy_sets_debug(
        self, mock_session_managers, caplog, mock_location_mapping
    ):
        caplog.set_level("DEBUG")
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        self.BUILDER.build_set_copies(set_data=legacy_set)
        assert len(caplog.records) == 11
        assert [i.msg for i in caplog.records] == [
            "(12345678) Building teacher set from legacy data.",
            "(12345678) Getting bib record from platform.",
            "(12345678) Bib record retrieved from platform.",
            "(12345678) Getting item records from platform.",
            "(12345678) Retrieved bib and 2 item record(s) from platform.",
            "ISBN/UPC 9781234567897: retrieving brief bib record.",
            "ISBN/UPC 9781234567897: retrieving full bib record (OCLC number: ocn123456789).",
            "ISBN/UPC 9780987654328: retrieving brief bib record.",
            "ISBN/UPC 9780987654328: retrieving full bib record (OCLC number: ocn123456789).",
            "(12345678) Creating 2 copy/copies of set.",
            "(12345678) Created 2 valid copy/copies of set.",
        ]

    def test_build_legacy_sets_invalid_status(
        self, mock_session_managers_item_missing, mock_location_mapping, caplog
    ):
        with pytest.raises(ValueError) as exc:
            legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
            self.BUILDER.build_set_copies(set_data=legacy_set)
        assert str(exc.value) == "(12345678) Item status issue."


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
    BUILDER = TeacherSetBuilder(file="tests/data/all_legacy_sets.txt")

    def test_build_legacy_sets_large_print(
        self, live_creds, mock_control_number_file, caplog
    ):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="19810559")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            [
                "Roll of thunder, hear my cry by Mildred D. Taylor. Copy 1 of 6",
                "Roll of thunder, hear my cry by Mildred D. Taylor. Copy 2 of 6",
                "Roll of thunder, hear my cry by Mildred D. Taylor. Copy 3 of 6",
                "Roll of thunder, hear my cry by Mildred D. Taylor. Copy 4 of 6",
                "Roll of thunder, hear my cry by Mildred D. Taylor. Copy 5 of 6",
                "Roll of thunder, hear my cry by Mildred D. Taylor. Copy 6 of 6",
            ]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            [
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
            ]
        )
        assert legacy_set["local_genre_term"] == ["Fiction"]
        assert legacy_set["local_topic_term"] == ["African Americans"]
        assert len(bibs) == 6
        assert len(field_strings) == 32
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101i19762018xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ELA$fCLUB$pD$c4907",
            "=245  00$aRoll of thunder, hear my cry by Mildred D. Taylor.$pCopy 1 of 6",
            "=300  \\\\$a11 item(s)",
            '=500  \\\\$aSet consists of 10 copies of "Roll of thunder, hear my cry", 1 copy of "Roll of thunder, hear my cry [Large print]".',
            "=520  \\\\$3Roll of thunder, hear my cry$a\"This is an extraordinarily moving novel -- one you will not easily forget. Set in Mississippi at the height of the Depression, it is the story of one family's struggle to maintain their integrity, pride, and independence. It is a story of physical survival, but more important, it is a story of the survival of the human spirit. And, too, it is Cassie's story -- Cassie Logan, an independent girl raised by a family for whom independence is primary, a family determined not to relinquish their humanity simply because they are Black. Cassie has grown up protected, grown up strong, and so far grown up unaware that any white person could force her to be untrue to herself, could consider her inferior and treat her accordingly. It took the events of one turbulent year -- the year of the night riders and the burnings, the year a white girl humiliated Cassie in public simply because she was Black -- to show Cassie why the land meant so much, why having a place of their own where they answered to no one permitted the Logans the luxuries of pride and courage their sharecropper neighbors couldn't afford and their white neighbors couldn't allow. Richly characterized, powerfully told, Mildred Taylor's novel is unforgettable. The Logans' story is at times warm and humorous, at times terrifying. It is a story of courage and love and pride, the story of one family's passionate determination not to be beaten down\" --Front jacket flap.",
            "=520  \\\\$3Roll of thunder, hear my cry [Large print]$aA black family living in Mississippi during the Depression of the 1930s is faced with prejudice and discrimination which its children do not understand.",
            "=521  2\\$a6-8",
            "=526  8\\$aLanguage Arts",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aAfrican Americans.$2bookops",
            "=695  \\7$aFiction.$2bookops",
            "=700  12$aTaylor, Mildred D.$tRoll of thunder, hear my cry.$f1976.$x9780803726475",
            "=700  12$aTaylor, Mildred D.$tRoll of thunder, hear my cry.$f2018.$sLarge print edition.$x9781432849252",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=901  \\\\$n33333400062432$oTeacher Set ELA B Book Club Set Roll of Thunder, Hear My Cry 1-3",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry$nRoll of thunder, hear my cry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Roll of thunder, hear my cry [Large print]$nRoll of thunder, hear my cry [Large print]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_build_legacy_sets_dvd(self, live_creds, mock_control_number_file, caplog):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="18892614")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bibs = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bibs[0].fields]
        assert len(valid_set_copies[0].components) == 2
        assert sorted([i.field_245.format_field() for i in valid_set_copies]) == sorted(
            [
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 1 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 2 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 3 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 4 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 5 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 6 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 7 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 8 of 9",
                "Charlie and the Chocolate Factory by Roald Dahl with DVD. Copy 9 of 9",
            ]
        )
        assert sorted([i.field_001.format_field() for i in valid_set_copies]) == sorted(
            [
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
                "nn-mlnyc-0000001",
            ]
        )
        assert sorted(legacy_set["local_genre_term"]) == sorted(["Fiction", "Fantasy"])
        assert sorted(legacy_set["local_topic_term"]) == sorted(["Behavior", "Music"])
        assert len(bibs) == 9
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i19642011xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fCLUB$pC$cINC-1138",
                "=245  00$aCharlie and the Chocolate Factory by Roald Dahl with DVD.$pCopy 1 of 9",
                "=300  \\\\$a10 item(s) + 1 DVD.",
                '=500  \\\\$aSet consists of 10 copies of "Charlie and the chocolate factory", 1 copy of "Willy Wonka & the chocolate factory [DVD]".',
                "=520  \\\\$3Charlie and the chocolate factory$aEach of five children lucky enough to discover an entry ticket into Mr. Willy Wonka's mysterious chocolate factory takes advantage of the situation in his own way.",
                "=520  \\\\$3Willy Wonka & the chocolate factory$aCandy manufacturer Willy Wonka has a contest and hides five golden tickets in five of his scrumptious candy bars. All five ticket winners get a free tour of the mysterious Wonka factory, as well as a lifetime supply of Wonka candy. Four of the children are nasty brats who are punished by Willie Wonka with various diabolical, but funny, methods. Only Charlie, a likeable child, wins the heart of the manufacturer.",
                "=521  2\\$a3-5",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aBook Club.$2bookops",
                "=691  \\7$aBehavior.$2bookops",
                "=691  \\7$aMusic.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aFantasy.$2bookops",
                "=700  12$aDahl, Roald.$tCharlie and the chocolate factory.$f1964.$x9780142410318",
                "=730  02$aWilly Wonka & the chocolate factory.$f2011.$x0780671236",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333400075343$oTeacher Set ELA B Book Club Set Charlie and the Chocolate Factory 1-11",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Charlie and the chocolate factory$nCharlie and the chocolate factory$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Willy Wonka & the chocolate factory [DVD]$nWilly Wonka & the chocolate factory [DVD]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_adventure(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="20830666")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            ["Fiction", "Adventure", "Fantasy"]
        )
        assert sorted(legacy_set["local_topic_term"]) == sorted(["New York City"])
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20122014xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fTOPIC$pC$c2080",
                "=245  00$aMagic Tree House with Companion Books by Mary Pope Osbourne.$pCopy 1 of 7",
                "=300  \\\\$a14 item(s)",
                '=500  \\\\$aSet consists of 2 copies of "Hurry up, Houdini!", 2 copies of "Magic tricks from the tree house", 2 copies of "A perfect time for pandas", 2 copies of "Pandas and other endangered species", 2 copies of "High time for heroes", 2 copies of "Soccer on Sunday", 2 copies of "Soccer".',
                '=520  \\\\$3Hurry up, Houdini!$a"Join Jack and Annie as they as they meet one of the world\'s most famous illusionists - Harry Houdini!"-- Provided by publisher.',
                "=520  \\\\$3Magic tricks from the tree house$aA chapter-book companion to the fiftieth Magic Tree House adventure outlines how to perform basic magic tricks and is complemented by facts about famous historical magicians.",
                "=520  \\\\$3A perfect time for pandas$aThe magic tree house whisks Jack and Annie off to a village in the mountains of southeast China, near a worldfamous panda reserve. They need to find a special food to save Merlin's penguin, Penny. Then a historic earthquake strikes! How will Jack and Annie survive?.",
                "=520  \\\\$3Pandas and other endangered species$aA nonfiction companion to A Perfect Time for Pandas answers Jack and Annie's various questions about endangered species, from what pandas eat and where they live to why leatherback sea turtles are scarce. Includes information on doing research and museums & zoos.",
                '=520  \\\\$3High time for heroes$a"Jack and Annie are magically transported to mid-1800\'s Thebes where they are saved from a dangerous accident by Florence Nightingale!"-- Provided by publisher.',
                "=520  \\\\$3Soccer on Sunday$aJack and Annie are taking the magic tree house to the 1970 World Cup in Mexico City! They are sure the famous soccer player Pelé will tell them a secret of greatness. The game is nonstop action, and the stands are packed. But how will they find Pelé in a crowd of 100,000 soccer fans? Will the answer come when they least expect it?.",
                '=520  \\\\$3Soccer$a"A nonfiction companion to Magic Tree House #52: Soccer on Sunday"-- Provided by publisher.',
                "=521  2\\$a3-5",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aNew York City.$2bookops",
                "=695  \\7$aFantasy.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aAdventure.$2bookops",
                "=700  12$aOsborne, Mary Pope.$tHurry up, Houdini!$f2013.$x9780307980458",
                "=700  12$aOsborne, Mary Pope.$tMagic tricks from the tree house.$f2013.$x9780449817902",
                "=700  12$aOsborne, Mary Pope.$tA perfect time for pandas.$f2012.$x9780375868269",
                "=700  12$aOsborne, Mary Pope.$tPandas and other endangered species.$f©2012.$x9780375870255",
                "=700  12$aOsborne, Mary Pope.$tHigh time for heroes.$f2014.$x9780307980496",
                "=700  12$aOsborne, Mary Pope.$tSoccer on Sunday.$f2014.$x9780307980540",
                "=700  12$aOsborne, Mary Pope.$tSoccer.$f2014.$x9780385386302",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333408135537$oTeacher Set ELA B Magic Tree House 1-4",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Hurry up, Houdini!$nHurry up, Houdini!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hurry up, Houdini!$nHurry up, Houdini!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Magic tricks from the tree house$nMagic tricks from the tree house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Magic tricks from the tree house$nMagic tricks from the tree house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A perfect time for pandas$nA perfect time for pandas$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A perfect time for pandas$nA perfect time for pandas$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Pandas and other endangered species$nPandas and other endangered species$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Pandas and other endangered species$nPandas and other endangered species$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-High time for heroes$nHigh time for heroes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-High time for heroes$nHigh time for heroes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Soccer on Sunday$nSoccer on Sunday$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Soccer on Sunday$nSoccer on Sunday$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Soccer$nSoccer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Soccer$nSoccer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_uniform_title(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="21184946")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            ["Fiction", "Biography"]
        )
        assert sorted(legacy_set["local_topic_term"]) == sorted(
            ["Astronomy", "African Americans"]
        )
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20162017xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC SOC$fCLUB$pE$c1500",
                "=245  00$aHidden Figures: The American Dream and the Untold Story of the Black Women Mathematicians Who Helped Win the Space Race by Margot Lee Shetterly with DVD.$pCopy 1 of 3",
                "=300  \\\\$a10 item(s) + 1 DVD.",
                '=500  \\\\$aSet consists of 10 copies of "Hidden figures", 1 copy of "Hidden figures (Motion picture) [DVD]".',
                "=520  \\\\$3Hidden figures$a\"Before John Glenn orbited the earth or Neil Armstrong walked on the moon, a group of dedicated female mathematicians known as 'human computers' used pencils, slide rules and adding machines to calculate the numbers that would launch rockets, and astronauts, into space. Among these problem-solvers were a group of exceptionally talented African American women, some of the brightest minds of their generation. Originally relegated to teaching math in the South's segregated public schools, they were called into service during the labor shortages of World War II, when America's aeronautics industry was in dire need of anyone who had the right stuff. Suddenly, these overlooked math whizzes had a shot at jobs worthy of their skills, and they answered Uncle Sam's call, moving to Hampton, Virginia, and the fascinating, high-energy world of the Langley Memorial Aeronautical Laboratory. Even as Virginia's Jim Crow laws required them to be segregated from their white counterparts, the women of Langley's all-black 'West Computing' group helped America achieve one of the things it desired most: a decisive victory over the Soviet Union in the Cold War, and complete domination of the heavens\"--Publisher's description.",
                "=520  \\\\$3Hidden figures (Motion picture)$aAs the United States raced against Russia to put a man in space, NASA found untapped talent in a group of African-American female mathematicians that served as the brains behind one of the greatest operations in U.S. history. Dorothy Vaughan, Mary Jackson, and Katherine Johnson crossed all gender, race, and professional lines while their brilliance and desire to dream big - beyond anything ever accomplished before by the human race - firmly cemented them in U.S. history as true American heroes.",
                "=521  2\\$a9-12",
                "=526  8\\$aSocial Studies",
                "=690  \\7$aBook Club.$2bookops",
                "=691  \\7$aAstronomy.$2bookops",
                "=691  \\7$aAfrican Americans.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aBiography.$2bookops",
                "=700  12$aShetterly, Margot Lee.$tHidden figures.$f2016.$x9780062363596",
                "=730  02$aHidden figures (Motion picture)$f2017.$x9786316777201",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333400078552$oTeacher Set SOC D BC Shetterly 1-2",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures$nHidden figures$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hidden figures (Motion picture) [DVD]$nHidden figures (Motion picture) [DVD]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_award_winners(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="20798098")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            ["Fiction", "Award Winners", "Biography"]
        )
        assert sorted(legacy_set["local_topic_term"]) == sorted(
            ["Dance", "Animals", "African Americans", "Family", "Music"]
        )
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20132014xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fTOPIC$pB$c5936",
                "=245  00$aAward Winners - Ezra Jack Keats Award.$pCopy 1 of 13",
                "=300  \\\\$a10 item(s)",
                '=500  \\\\$aSet consists of 1 copy of "Edda", 1 copy of "Firebird", 1 copy of "Grandfather Gandhi", 1 copy of "Hana Hashimoto, sixth violin", 1 copy of "Little Elliot, big city", 1 copy of "Rain!", 1 copy of "Shh! We have a plan", 1 copy of "Sophie\'s squash", 1 copy of "Take me out to the Yakyu", 1 copy of "Tea party rules".',
                "=520  \\\\$3Edda$aEdda is a Valkyrie (an ancient Norse goddess who guides and protects heroes). She lives in a magical land called Asgard where she has everything she wants. Well ... almost everything. Edda wants to find a friend her own age. Edda's wise papa knows of a place where she can make friends: a place on Earth called \"school.\" School is very different from Asgard. Edda's not sure if she likes it at first. But then she remembers that Valkyries are very brave. Even little Valkyries. Edda learns that being different is what makes her special and she begins to make new friends.",
                "=520  \\\\$3Firebird$aWith spare, poignant text, American Ballet Theatre soloist Misty Copeland writes of a young dancer whose confidence is fragile. Through hard work and dedication, Misty shows her how she can reach the same heights as Misty, even becoming the Firebird, Misty Copeland's signature role. An affecting story echoing Misty Copeland's own remarkable and meteoric rise in ballet, paired with vibrant, memorable art with plenty of style and flair--some of Caldecott Honoree Christopher Myers's best work. A must-have for any lover of ballet--From dust jacket.",
                '=520  \\\\$3Grandfather Gandhi$a"Mahatma Gandhi\'s grandson tells the story of how his grandfather taught him to turn darkness into light in this uniquely personal and vibrantly illustrated tale that carries a message of peace."--Amazon.com.',
                "=520  \\\\$3Hana Hashimoto, sixth violin$a\"In this beautifully written picture book, Hana Hashimoto has signed up to play her violin at her school's talent show. The trouble is, she's only a beginner, and she's had only three lessons. her brothers insist she isn't good enough. 'It's a talent show, Hana,' they tell her. 'You'll be a disaster!' Hana remembers how wonderfully her talented grandfather, or Ojiichan, played his violin when she was visiting him in Japan. So, just like Ojiichan, Hana practices every day. She is determined to play her best. When Hana's confidence wavers on the night of the show, however, she begins to wonder if her brothers were right. But then Hana surprises everyone once it's her turn to perform--even herself! The Asian American female protagonist in this story offers a unique perspective, and bestselling author Chieri Uegaki has woven in lyrical scenes from Japan that add depth and resonance. The details in the artwork by Qin Leng connect the two places and contain a feeling of melody throughout. In the classroom, this book could serve as a celebration of music and performing arts, multicultural studies or the importance of intergenerational relationships. It is also a fabulous character education tie-in for discussing courage and perseverance. This terrifically inspiring book offers hope and confidence to all children who are yearning to master something difficult. Perhaps even more important, it allows children to see that there is more than one way to be successful at a task.\" -- From publisher.",
                "=520  \\\\$3Little Elliot, big city$aElliot the little elephant has a hard time with a lot of things in the city he loves until he meets Mouse, who is even smaller--and hungrier.",
                "=520  \\\\$3Rain!$aAs an old man grumbles his way through a rainy morning, spreading gloom, his neighbor, a young child, spreads cheer while hopping through puddles in frog-themed rainwear.",
                "=520  \\\\$3Shh! We have a plan$a\"Four friends creep through the woods, and what do they spot? An exquisite bird high in a tree! 'Hello birdie, ' waves one. 'Shh! We have a plan, ' hush the others. They stealthily make their advance, nets in the air. Ready one, ready two, ready three, and go! But as one comically foiled plan follows another, it soon becomes clear that their quiet, observant companion, hand outstretched, has a far better idea. Award-winning author-illustrator Chris Haughton is back with another simple, satisfying story whose visual humor plays out in boldly graphic, vibrantly colorful illustrations.\"-- Provided by publisher.",
                "=520  \\\\$3Sophie's squash$aA young girl befriends a squash.",
                "=520  \\\\$3Take me out to the Yakyu$aA little boy's grandfathers, one in America and one in Japan, teach him about baseball and its rich, varying cultural traditions.",
                '=520  \\\\$3Tea party rules$a"A bossy little girl makes a bear cub follow all the rules at her tea party before he is allowed to eat any of the cookies"-- Provided by publisher.',
                "=521  2\\$aK-2",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aFamily.$2bookops",
                "=691  \\7$aAfrican Americans.$2bookops",
                "=691  \\7$aAnimals.$2bookops",
                "=691  \\7$aDance.$2bookops",
                "=691  \\7$aMusic.$2bookops",
                "=695  \\7$aAward Winners.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aBiography.$2bookops",
                "=700  12$aAuerbach, Adam.$tEdda.$f2014.$x9780805097030",
                "=700  12$aCopeland, Misty.$tFirebird.$f2014.$x9780399166150",
                "=700  12$aGandhi, Arun.$tGrandfather Gandhi.$f©2012.$x9781442423657",
                "=700  12$aUegaki, Chieri.$tHana Hashimoto, sixth violin.$f2014.$x9781894786331",
                "=700  12$aCurato, Mike.$tLittle Elliot, big city.$f2014.$x9780805098259",
                "=700  12$aAshman, Linda.$tRain!$f2013.$x9780547733951",
                "=700  12$aHaughton, Chris.$tShh! We have a plan.$f2014.$x9780763672935",
                "=700  12$aMiller, Pat Zietlow.$tSophie's squash.$f©2013.$x9780307978967",
                "=700  12$aMeshon, Aaron.$tTake me out to the Yakyu.$f2013.$x9781442441774",
                "=700  12$aDyckman, Ame.$tTea party rules.$f2013.$x9780670785018",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333402219972$oTeacher Set ELA A Award Keats 1-1",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Edda$nEdda$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Firebird$nFirebird$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Grandfather Gandhi$nGrandfather Gandhi$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Hana Hashimoto, sixth violin$nHana Hashimoto, sixth violin$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Little Elliot, big city$nLittle Elliot, big city$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Rain!$nRain!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Shh! We have a plan$nShh! We have a plan$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Sophie's squash$nSophie's squash$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Take me out to the Yakyu$nTake me out to the Yakyu$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Tea party rules$nTea party rules$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_manga(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="21294725")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            [
                "Manga",
                "Fantasy",
                "Romance",
                "Fiction",
                "Adventure",
                "Comics & Graphic Novels",
                "Folklore",
            ]
        )
        assert legacy_set["local_topic_term"] == ["Sports"]
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20162016xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fTOPIC$pE$cINC 1178",
                "=245  00$aManga Assorted Titles (Set II).$pCopy 1 of 7",
                "=300  \\\\$a30 item(s)",
                '=500  \\\\$aSet consists of 3 copies of "Behind the scenes!!", 3 copies of "Shigeru Mizuki\'s Kitaro", 3 copies of "Bleach", 3 copies of "Devil\'s line", 3 copies of "Haikyu!!", 3 copies of "Horimiya", 3 copies of "Monthly girls\' Nozaki-kun", 3 copies of "Naruto", 3 copies of "One piece", 3 copies of "Yona of the dawn".',
                "=520  \\\\$3Behind the scenes!!$a\"Ranmaru Kurisu comes from a family of hardy, rough-and-tumble fisherfolk and he sticks out at home like a delicate, artistic sore thumb. It's given him a raging inferiority complex and a permanently pessimistic outlook. Now that he's in college, he's hoping to find a sense of belonging. But after a whole life of being left out, does he even know how to fit in?! It's two months into Ranmaru's college career, and if he's learned one thing, it's that he's really uncomfortable around other people. But when he stumbles into a zombie mob attack, he's forced out of his comfort zone in the most dramatic way possible! Of course it's just a movie shoot, but when he wakes up from his ignoble faint, he's been whisked away behind the scenes with the Art Squad! Could this group of weirdos be what Ranmaru's been looking for all his life?!\"--Back cover.",
                "=520  \\\\$3Bleach$aIchigo Kurosaki has martial arts skills and the ability to see ghosts, and his life is about to change when he meets Rukia Kuchiki, a soul reaper and protector of innocents.",
                '=520  \\\\$3Devil\'s line$a"Tsukasa, a college student, is rescued from an attack by a devil, one of many vampires that can blend in among the human population. Anzai, her savior, is a half-devil who exploits his supernatural gifts as a member of a shadowy police task force that specializes in devil-related crime in Tokyo."--Page 4 of cover.',
                "=520  \\\\$3Haikyu!!$a\"Ever since he saw the legendary player known as 'the Little Giant' compete at the national volleyball finals, Shoyo Hinata has been aiming to be the best volleyball player ever! Who says you need to be tall to play volleyball when you can jump higher than anyone else? After losing his first and last volleyball match against Tobio Kageyama, 'the King of the Court, ' Shoyo Hinata swears to become his rival after graduating middle school. But what happens when the guy he wants to defeat ends up being his teammate?!, \"--Page 4 of cover.",
                "=520  \\\\$3Horimiya$aDespite their veneers as a frivolous high school girl and a gloomy high school fanboy, Hori and Miyamura are actually quite similar, and a relationship begins when they accidentally run into each other outside of class.",
                "=520  \\\\$3Monthly girls' Nozaki-kun$a\"To the eyes of classmate Chiyo Sakura, high school student Umetarou Nozaki--brawny of build and brusque of tongue--is a dreamboat! When Chiyo finally works up the courage to tell Nozaki how she feels about him, she knows rejection is on the table ... but getting recruited as a mangaka's assistant?! Never in a million years! As Chiyo quickly discovers, Nozaki-kun, the boy of Chiyo's dreams, is a manga artist ... a hugely popular shoujo manga artist, that is! But for someone who makes a living drawing sweet girly romances, Nozaki-kun is a little slow on the uptake when it comes to matters of the heart in reality. And so Chiyo's daily life of manga making and heartache begins!\"--Page 4 of cover.",
                "=520  \\\\$3Naruto$aIn the village of Konohagakure, school is literally a battlefield where classmates are ninjas in training competing to become the greatest ninja in the land.",
                '=520  \\\\$3One piece$a"Join Monkey D. Luffy and his swashbuckling crew in their search for the ultimate treasure, the One Piece. As a child, Monkey D. Luffy dreamed of becoming King of the Pirates. But his life changed when he accidentally gained the power to stretch like rubber--at the cost of never being able to swim again! Years later, Luffy sets off in search of the One Piece, said to be the greatest treasure in the world..." -- From publisher\'s website. https://www.viz.com/one-piece.',
                "=520  \\\\$3Shigeru Mizuki's Kitaro$aThe Birth of Kitaro collects seven of Shigeru Mizuki's early, and beloved, Kitaro stories, making them available for the first time in English, in an all-new, kid-friendly format. These stories are from the golden era of the late 1960s, when Gegege no Kitaro truly hit its stride as an all-ages supernatural series. Mizuki's Kitaro stories are both timelessly relevant and undeniably influential, inspiring a decades-long boom in stories about yokai, Japanese ghosts, and monsters. \"Kitaro's Birthday\" reveals the origin story of the half-yokai boy Kitaro and his tiny eyeball father, Medama Oyaji. \"Neko Musume versus Nezumi Otoko\" is the first of Mizuki's stories to feature the popular recurring character Neko Musume, a little girl who transforms into a cat when she gets angry or hungry. Other stories in The Birth of Kitaro draw heavily from Japanese folklore, with Kitaro taking on legendary Japanese yokai like the Nopperabo and Makura Gaeshi, and fighting the monstrous recurring villain Gyuki.",
                "=520  \\\\$3Yona of the dawn$a\"Princess Yona lives an ideal life as the only princess of her kingdom. Doted on by her father, the king, and protected by her faithful guard Hak, she cherishes the time spent with the man she loves, Soo-won. But everything changes on her 16th birthday when she witnesses her father's murder! Yona reels from the shock of witnessing a loved one's murder and having to fight for her life. With Hak's help, she flees the palace and struggles to survive while evading her enemy's forces. But where will this displaced princess go when all the paths before her are uncertain?\"-- Page [4] of cover.",
                "=521  2\\$a9-12",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aSports.$2bookops",
                "=695  \\7$aAdventure.$2bookops",
                "=695  \\7$aFantasy.$2bookops",
                "=695  \\7$aComics & Graphic Novels.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aFolklore.$2bookops",
                "=695  \\7$aManga.$2bookops",
                "=695  \\7$aRomance.$2bookops",
                "=700  12$aFurudate, Haruichi,$d1983-$tHaikyu!!$f[2016]-[2021]$x9781421587660",
                "=700  12$aHanada, Ryo,$d1987-$tDevil's line.$f2016-$x9781942993377",
                "=700  12$aHatori, Bisco.$tBehind the scenes!!$f2016.$x9781421585246",
                "=700  12$aHero.$tHorimiya.$f[2015-2021]$x9780316342032",
                "=700  12$aKishimoto, Masashi,$d1974-$tNaruto.$f2003-$x9781569319000",
                "=700  12$aKubo, Tite.$tBleach.$f2004-$x9781591164418",
                "=700  12$aKusanagi, Mizuho,$d1979-$tYona of the dawn.$f[2016]-$x9781421587813",
                "=700  12$aMizuki, Shigeru,$d1922-2015$tShigeru Mizuki's Kitaro.$f2016.$x9781770462281",
                "=700  12$aOda, Eiichirō,$d1975-$tOne piece.$f[2003-]$x9781569319017",
                "=700  12$aTsubaki, Izumi.$tMonthly girls' Nozaki-kun.$f2015-$x9780316309479",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333400081697$oTeacher Set ELA D Manga 2-3",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Behind the scenes!!$nBehind the scenes!!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Behind the scenes!!$nBehind the scenes!!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Behind the scenes!!$nBehind the scenes!!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Bleach$nBleach$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Bleach$nBleach$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Bleach$nBleach$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Devil's line$nDevil's line$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Devil's line$nDevil's line$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Devil's line$nDevil's line$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Haikyu!!$nHaikyu!!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Haikyu!!$nHaikyu!!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Haikyu!!$nHaikyu!!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Horimiya$nHorimiya$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Horimiya$nHorimiya$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Horimiya$nHorimiya$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Monthly girls' Nozaki-kun$nMonthly girls' Nozaki-kun$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Monthly girls' Nozaki-kun$nMonthly girls' Nozaki-kun$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Monthly girls' Nozaki-kun$nMonthly girls' Nozaki-kun$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Naruto$nNaruto$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Naruto$nNaruto$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Naruto$nNaruto$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-One piece$nOne piece$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-One piece$nOne piece$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-One piece$nOne piece$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Shigeru Mizuki's Kitaro$nShigeru Mizuki's Kitaro$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Shigeru Mizuki's Kitaro$nShigeru Mizuki's Kitaro$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Shigeru Mizuki's Kitaro$nShigeru Mizuki's Kitaro$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Yona of the dawn$nYona of the dawn$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Yona of the dawn$nYona of the dawn$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Yona of the dawn$nYona of the dawn$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_mystery(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="20039849")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(["Fiction", "Mystery"])
        assert legacy_set["local_topic_term"] == []
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20112011xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fCLUB$pE$c5882",
                "=245  00$aSpy in the House by Y. S. Lee.$pCopy 1 of 4",
                "=300  \\\\$a10 item(s)",
                '=500  \\\\$aSet consists of 10 copies of "A spy in the house".',
                "=520  \\\\$3A spy in the house$aRescued from the gallows in 1850s London, young orphan and thief Mary Quinn is offered a place at Miss Scrimshaw's Academy for Girls where she is trained to be part of an all-female investigative unit called The Agency and, at age seventeen, she infiltrates a rich merchant's home in hopes of tracing his missing cargo ships.",
                "=521  2\\$a9-12",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aBook Club.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aMystery.$2bookops",
                "=700  12$aLee, Y. S,$d1974-$tA spy in the house.$f2011.$x9780763652890",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333402191049$oTeacher Set ELA D Book Club Set A Spy in the House 1-1",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-A spy in the house$nA spy in the house$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_poetry(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="20748659")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(["Memoir", "Poetry"])
        assert sorted(legacy_set["local_topic_term"]) == sorted(
            ["African Americans", "Civil Rights"]
        )
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20122014xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fTOPIC$pD$c",
                "=245  00$aCivil Rights Poetry.$pCopy 1 of 11",
                "=300  \\\\$a15 item(s)",
                '=500  \\\\$aSet consists of 5 copies of "I, too, am America", 5 copies of "When thunder comes", 5 copies of "How I discovered poetry".',
                '=520  \\\\$3How I discovered poetry$aThe author reflects on her childhood in the 1950s and her development as an artist and young woman through fifty poems that consider such influences as the Civil Rights Movement, the "Red Scare" era, and the feminist movement.',
                "=520  \\\\$3I, too, am America$aPresents the popular poem by one of the central figures in the Harlem Renaissance, highlighting the courage and dignity of the African American Pullman porters in the early twentieth century.",
                "=520  \\\\$3When thunder comes$aA collection of poetry inspired by various leaders of civil rights. Featuring Coretta Scott King, Harvey Milk, Mohandas Gandhi, Nelson Mandela, Sylvia Mendez, Aung San Suu Kyi, Mamie Carthan Till, Helen Zia, Josh Gibson, Dennis James Banks, Mitsuye Endo, Ellison Onizuka, Jackie Robinson, Muhammad Yunus, James Chaney, Andrew Goodman, and Michael Schwerner. Includes brief descriptions of each leader at the end of the book.",
                "=521  2\\$a6-8",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aAfrican Americans.$2bookops",
                "=691  \\7$aCivil Rights.$2bookops",
                "=695  \\7$aPoetry.$2bookops",
                "=695  \\7$aMemoir.$2bookops",
                "=700  12$aHughes, Langston,$d1902-1967$tI, too, am America.$f2012.$x9781442420083",
                "=700  12$aLewis, J. Patrick.$tWhen thunder comes.$f2013.$x9781452101194",
                "=700  12$aNelson, Marilyn,$d1946-$tHow I discovered poetry.$f2014.$x9780803733046",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333400069890$oTeacher Set ELA C Poetry - Civil Rights 1-4",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-How I discovered poetry$nHow I discovered poetry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-How I discovered poetry$nHow I discovered poetry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-How I discovered poetry$nHow I discovered poetry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-How I discovered poetry$nHow I discovered poetry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-How I discovered poetry$nHow I discovered poetry$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-I, too, am America$nI, too, am America$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-I, too, am America$nI, too, am America$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-I, too, am America$nI, too, am America$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-I, too, am America$nI, too, am America$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-I, too, am America$nI, too, am America$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-When thunder comes$nWhen thunder comes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-When thunder comes$nWhen thunder comes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-When thunder comes$nWhen thunder comes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-When thunder comes$nWhen thunder comes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-When thunder comes$nWhen thunder comes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_genre_coming_of_age(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="20760653")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            ["Coming of Age", "Comics & Graphic Novels", "Fiction"]
        )
        assert legacy_set["local_topic_term"] == []
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20142014xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fCLUB$pE$c1632",
                "=245  00$aThis One Summer by Mariko Tamaki.$pCopy 1 of 5",
                "=300  \\\\$a10 item(s)",
                '=500  \\\\$aSet consists of 10 copies of "This one summer".',
                "=520  \\\\$3This one summer$a\"Every summer, Rose goes with her mom and dad to a lake house in Awago Beach. It's their getaway, their refuge. Rosie's friend Windy is always there, too, like the little sister she never had. But this summer is different. Rose's mom and dad won't stop fighting, and when Rose and Windy seek a distraction from the drama, they find themselves with a whole new set of problems. One of the local teens - just a couple of years older than Rose and Windy - is caught up in something bad ... Something life threatening. It's a summer of secrets, and sorrow, and growing up, and it's a good thing Rose and Windy have each other. This One Summer is a tremendously exciting new teen graphic novel from two creators with true literary clout. Cousins Mariko and Jillian Tamaki, the team behind Skim, have collaborated on this gorgeous, heartbreaking, and ultimately hopeful story about a girl on the cusp of childhood - a story of renewal and revelation.\"--Publisher's web site.",
                "=521  2\\$a9-12",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aBook Club.$2bookops",
                "=695  \\7$aComics & Graphic Novels.$2bookops",
                "=695  \\7$aComing of Age.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=700  12$aTamaki, Mariko.$tThis one summer.$f2014.$x9781626720947",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333402207688$oTeacher Set ELA D Book Club Set This One Summer (GN) 1-1",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This one summer$nThis one summer$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_topic_ancient_civ(self, caplog, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="20895133")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert legacy_set["local_genre_term"] == []
        assert legacy_set["local_topic_term"] == ["Ancient Civilization"]
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
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20152015xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC SOC$fTOPIC$pE$c1072",
                "=245  00$aAncient Civilizations.$pCopy 1 of 8",
                "=300  \\\\$a8 item(s)",
                '=500  \\\\$aSet consists of 1 copy of "Ancient Rome", 1 copy of "Ancient Mesopotamia", 1 copy of "Ancient Maya", 1 copy of "Ancient India", 1 copy of "Ancient Greece", 1 copy of "Ancient Egypt", 1 copy of "Ancient China", 1 copy of "Ancient Aztecs".',
                "=520  \\\\$3Ancient Rome$a\"In Ancient Rome, readers discover the history and impressive accomplishments of the ancient Romans, including their military power and feats of engineering. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
                "=520  \\\\$3Ancient Mesopotamia$a\"In Ancient Mesopotamia, readers discover the history and impressive accomplishments of the ancient Mesopotamians, including their extraordinary cultural achievements and technological wonders. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
                "=520  \\\\$3Ancient Maya$a\"In Ancient Maya, readers discover the history and impressive accomplishments of the Maya people, including their advanced mathematics and massive stone cities. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
                "=520  \\\\$3Ancient India$a\"In Ancient India, readers discover the history and impressive accomplishments of the people of ancient India, including their enduring religions and rich literary traditions. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
                "=520  \\\\$3Ancient Greece$aReaders will discover the history and accomplishments of the people of ancient Greece, including their cultural achievements and feats of construction.",
                "=520  \\\\$3Ancient Egypt$a\"In Ancient Egypt, readers discover the history and impressive accomplishments of the people of ancient Egypt, including their extraordinary cultural achievements and feats of construction. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
                "=520  \\\\$3Ancient China$a\"In Ancient China, readers discover the history and impressive accomplishments of the people of ancient China, including their technological wonders and feats of construction. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
                "=520  \\\\$3Ancient Aztecs$a\"In Ancient Aztecs, readers discover the history and impressive accomplishments of the Aztec civilization, including their military power and feats of engineering. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
                "=521  2\\$a9-12",
                "=526  8\\$aSocial Studies",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aAncient Civilization.$2bookops",
                "=700  12$aHamen, Susan E.$tAncient Rome.$f2015.$x9781624035425",
                "=700  12$aHead, Tom.$tAncient Mesopotamia.$f2015.$x9781624035418",
                "=700  12$aEdwards, Sue Bradford.$tAncient Maya.$f2015.$x9781624035401",
                "=700  12$aRowell, Rebecca.$tAncient India.$f2015.$x9781624035395",
                "=700  12$aBailey, Diane,$d1966-$tAncient Greece.$f2015.$x9781624035388",
                "=700  12$aAmstutz, Lisa J.$tAncient Egypt.$f2015.$x9781624035371",
                "=700  12$aAtkins, Marcie Flinchum.$tAncient China.$f2015.$x9781624035364",
                "=700  12$aKenney, Karen Latchana.$tAncient Aztecs.$f2015.$x9781624035357",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333408154165$oTeacher Set SOC C Ancient Civilizations 2-1",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Ancient Rome$nAncient Rome$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient Mesopotamia$nAncient Mesopotamia$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient Maya$nAncient Maya$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient India$nAncient India$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient Greece$nAncient Greece$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient Egypt$nAncient Egypt$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient China$nAncient China$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Ancient Aztecs$nAncient Aztecs$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )
        assert len(caplog.records) == 2
        assert [i.msg for i in caplog.records] == [
            "(20895133) Building teacher set from legacy data.",
            "(20895133) Created 8 valid copy/copies of set.",
        ]

    def test_topic_astronomy(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="19544031")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert legacy_set["local_genre_term"] == []
        assert legacy_set["local_topic_term"] == ["Astronomy"]
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20092009xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC SCI$fCLUB$pB$c297",
                "=245  00$aGalaxies, Galaxies! by Gail Gibbons.$pCopy 1 of 9",
                "=300  \\\\$a10 item(s)",
                '=500  \\\\$aSet consists of 10 copies of "Galaxies, Galaxies!".',
                "=520  \\\\$3Galaxies, Galaxies!$aGibbons's view of our solar system may no longer be valid, but she's really focusing her attention so far beyond local space that the damage is minor. Between an opening description of the Milky Way and a closing claim that galaxy formation is still going on, the author depicts ancient astronomers at work, describes several kinds of telescopes, and profiles five distinctive galactic forms, from irregular to lenticular. Pairing brief, matter-of-fact generalizations leavened with digestible doses of specific information to painted scenes that link diverse groups of human observers to galaxies seen in blobby, broadly brushed portraits, this introduction to some of the universes largest structures will put stars in the eyes of the most Earthbound young readers.",
                "=521  2\\$aK-2",
                "=526  8\\$aScience",
                "=690  \\7$aBook Club.$2bookops",
                "=691  \\7$aAstronomy.$2bookops",
                "=700  12$aGibbons, Gail.$tGalaxies, Galaxies!$f2009.$x9780823421923",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333402202721$oTeacher Set SCI A Book Club Set Astronomy - Galaxies, Galaxies 1-1",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Galaxies, Galaxies!$nGalaxies, Galaxies!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_topic_behavior(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="21164120")
        assert legacy_set["bib_id"] == "21164120"
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            ["Fiction", "Biography"]
        )
        assert sorted(legacy_set["local_topic_term"]) == sorted(
            [
                "Behavior",
                "Bullying",
                "Family",
                "Immigration",
                "African Americans",
                "Animals",
                "Autism",
                "Community",
            ]
        )
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20002022xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC SOC$fTOPIC$pB$c431",
                "=245  00$aEmpathy, Activism, and Understanding with DVD.$pCopy 1 of 8",
                "=300  \\\\$a29 item(s) + 1 DVD.",
                '=500  \\\\$aSet consists of 1 copy of "Adrift at sea", 1 copy of "Be the change in your community", 1 copy of "The black book of colors", 1 copy of "Can I play, too?", 1 copy of "Can we help?", 1 copy of "Each kindness", 1 copy of "Emmanuel\'s dream", 1 copy of "Empathy", 1 copy of "Families, families, families!", 1 copy of "I am Jazz", 1 copy of "If you plant a seed", 1 copy of "It\'s okay to be different", 1 copy of "Let\'s talk about race", 1 copy of "My brother Charlie", 1 copy of "Red", 1 copy of "Their great gift", 1 copy of "Those shoes", 1 copy of "Two white rabbits", 1 copy of "We came to America", 1 copy of "We march", 1 copy of "Whose hands are these?", 1 copy of "Wings", 1 copy of "The great big green book", 1 copy of "The soda bottle school", 1 copy of "Families", 1 copy of "My family, your family", 1 copy of "Families around the world", 1 copy of "Look where we live!", 1 copy of "Feminist Baby", 1 copy of "DVD (missing identifier) [DVD]".',
                '=520  \\\\$3Adrift at sea$a"Tuan and his family survive bullets, a broken motor, and a leaking boat in the long days they spend at sea after fleeing Vietnam. A true story as told to the author by Tuan Ho. Includes family photographs and a historical note about the Vietnamese refugee crisis."-- Provided by publisher.',
                "=520  \\\\$3Be the change in your community$aThis empowering title will help readers discover that they have the ability to create positive changes in their communities. Inviting text and relatable examples prompt children to learn what it means to be a citizen of a community and find meaningful ways to act for the common good. Ideas include creating artwork to brighten up a local retirement facility and donating old books to a library or reading program. (Publisher).",
                '=520  \\\\$3Can I play, too?$a"Gerald is careful. Piggie is not. Piggie cannot help smiling. Gerald can. Gerald worries so that Piggie does not have to. Gerald and Piggie are best friends. In Can I Play Too? Gerald and Piggie meet a new snake friend who wants to join in a game of catch. But how can a snake play catch?" --Back cover.',
                "=520  \\\\$3Can we help?$aDescribes how children can help their communities in different ways, from tending a community garden and training service dogs to volunteering to help people with disabilities and mentoring younger students.",
                "=520  \\\\$3Each kindness$aWhen Ms. Albert teaches a lesson on kindness, Chloe realizes that she and her friends have been wrong in making fun of new student Maya's shabby clothes and refusing to play with her.",
                "=520  \\\\$3Emmanuel's dream$a\"Emmanuel Ofosu Yeboah's inspiring true story--which was turned into a film, Emmanuel's Gift, narrated by Oprah Winfrey--is nothing short of remarkable. Born in Ghana, West Africa, with one deformed leg, he was dismissed by most people--but not by his mother, who taught him to reach for his dreams. As a boy, Emmanuel hopped to school more than two miles each way, learned to play soccer, left home at age thirteen to provide for his family, and, eventually, became a cyclist. He rode an astonishing four hundred miles across Ghana in 2001, spreading his powerful message: disability is not inability. Today, Emmanuel continues to work on behalf of the disabled. Thompson's lyrical prose and Qualls's bold collage illustrations offer a powerful celebration of triumphing over adversity.\" Publisher description.",
                "=520  \\\\$3Empathy$aThe ability to really understand and care about the feelings of another is a difficult attribute to develop. Contains examples and hints to help give readers the tools they need to develop empathy.",
                "=520  \\\\$3Families around the world$aAllows young readers to visit with fourteen children, each from a different country, to learn about their families. Includes suggested activities.",
                '=520  \\\\$3Families$a"Big or small, similar or different-looking, there are all kinds of families. Some have one parent, some have two, and many include extended family. This inclusive look at many varieties of families will help young readers see beyond their own immediate experiences"--Amazon.com.',
                '=520  \\\\$3Families, families, families!$a"A host of animals portrays all kinds of non-traditional families"-- Provided by publisher.',
                "=520  \\\\$3Feminist Baby$aFeminist Baby likes pink and blue, playing with cars and dolls, and the choice to become whatever she dreams.",
                "=520  \\\\$3I am Jazz$aFrom the time she was two years old, Jazz knew that she had a girl's brain in a boy's body. She loved pink and dressing up as a mermaid and didn't feel like herself in boys' clothing. This confused her family, until they took her to a doctor who said that Jazz was transgender and that she was born that way.",
                "=520  \\\\$3If you plant a seed$aWhile planting seeds in their garden, two animals learn the value of kindness.",
                '=520  \\\\$3It\'s okay to be different$aIllustrations and brief text describe all kinds of differences that are "okay," such as "It\'s Okay to be a different color," "It\'s Okay to need some help," "It\'s Okay to be adopted," and "It\'s Okay to have a Different nose.".',
                "=520  \\\\$3Let's talk about race$aThe author introduces the concept of race as only one component in an individual's or nation's \"story.\".",
                "=520  \\\\$3Look where we live!$aIn this book, five young friends -- Nick, Yulee, Pedro, Sally and Martin -- spend the day traveling around their neighborhood and participating in activities designed to raise money for their local library. Along the way, they learn about the people and places that make up their community and what it means to be a part of one.",
                "=520  \\\\$3My brother Charlie$aCallie is very proud of her brother Charlie. He's good at so many things -- swimming, playing the piano, running fast. And Charlie has a special way with animals, especially their dog, Harriet. But sometimes Charlie gets very quiet. His words get locked inside him, and he seems far away. Then, when Callie and Charlie start to play, Charlie is back to laughing, holding hands, having fun. Charlie is like any other boy -- and he has autism.",
                "=520  \\\\$3My family, your family$aExamines the ways in which families can differ, such as differing numbers of parents and children in individual homes.",
                "=520  \\\\$3Red$aRed's factory-applied label clearly says that he is red, but despite the best efforts of his teacher, fellow crayons and art supplies, and family members, he cannot seem to do anything right until a new friend offers a fresh perspective.",
                "=520  \\\\$3The black book of colors$aThis title invites readers to imagine living without sight through remarkable illustrations done with raised lines and descriptions of colors based on imagery. Braille letters accompany the illustrations and a full Braille alphabet offers sighted readers help reading along with their fingers.",
                '=520  \\\\$3The great big green book$a"Think of the future. Can you imagine our planet as beautiful as it used to be? You could be the one to help make it beautiful again, with the things you do and the ideas you have. Your planet needs YOU!" From a simple introduction to our home in Space, the authors explain what we need for life on Earth, and show the importance of the rainforests and the oceans; they stress the need to look after our planet and show how some of the things we take for granted are running out, and how we have polluted so much of our planet. The action plans include saving water, saving energy, recycling, repairing, growing seasonal food, cooking fresh food, saving on packing, asking questions ... and thinking of new inventions and big ideas.',
                "=520  \\\\$3The soda bottle school$aIn a Guatemalan village, students squished into their tiny schoolhouse, two grades to a classroom. The villagers had tried expanding the school, but the money ran out before the project was finished. No money meant no wall materials, and that meant no more room for the students. Until one boy got a wonderful, crazy idea: Why not use soda bottles, which were scattered all around, to form the cores of the walls?.",
                "=520  \\\\$3Their great gift$aExplores the experience of immigrants who came to America in the twenty-first century, celebrating the diversity of the country and hope for the future.",
                "=520  \\\\$3Those shoes$aJeremy, who longs to have the black high tops that everyone at school seems to have but his grandmother cannot afford, is excited when he sees them for sale in a thrift shop and decides to buy them even though they are the wrong size.",
                "=520  \\\\$3Two white rabbits$aIn this moving and timely story, a young child describes what it is like to be a migrant as she and her father travel north toward the U.S. border. They travel mostly on the roof of a train known as The Beast, but the little girl doesn't know where they are going. She counts the animals by the road, the clouds in the sky, the stars. Sometimes she sees soldiers. She sleeps, dreaming that she is always on the move, although sometimes they are forced to stop and her father has to earn more money before they can continue their journey. As many thousands of people, especially children, in Mexico and Central America continue to make the arduous journey to the U.S. border in search of a better life, this is an important book that shows a young migrant's perspective. -- From amazon.com.",
                "=520  \\\\$3We came to America$aA timely and beautiful look at America's rich history of immigration and diversity, from acclaimed artist Faith Ringgold, the Coretta Scott King and Caldecot Honor winning creator of Tar Beach. Vividly expressed in Faith Ringgold's sumptuous colors and patterns, We Came to America is an ode to every Amerian who came before us, and a tribute to each child who will carry its proud message of diversity into our nation's future. America is a country rich in diversity -- From the Native Americans who first called this land their home, to the millions of people who have flocked to its shores ever since. Some of our ancestors were driven by dreams and hope. others came in chains, or were escaping poverty or persecution. No matter what brought them here, each person embodied a unique gift - their art and music, their determination and grit, their stories and their culture. And together they forever shaped the country we all call home. -- From amazon.com.",
                "=520  \\\\$3We march$aIllustrations and brief text portray the events of the 1963 march in Washington, D.C., where the Reverend Martin Luther King Jr. delivered a historic speech.",
                "=520  \\\\$3Whose hands are these?$aAsks young readers to identify the occupation of each community helper from the type of tasks they perform and explains how these helpers work together to keep communities clean and safe and people healthy.",
                "=520  \\\\$3Wings$aIkarus Jackson, the new boy in school, is outcast because he has wings, but his resilient spirit inspires one girl to speak up for him.",
                "=520  \\\\$3DVD (missing identifier).",
                "=521  2\\$aK-2",
                "=526  8\\$aSocial Studies",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aAfrican Americans.$2bookops",
                "=691  \\7$aAnimals.$2bookops",
                "=691  \\7$aAutism.$2bookops",
                "=691  \\7$aBehavior.$2bookops",
                "=691  \\7$aBullying.$2bookops",
                "=691  \\7$aCommunity.$2bookops",
                "=691  \\7$aFamily.$2bookops",
                "=691  \\7$aImmigration.$2bookops",
                "=695  \\7$aBiography.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=700  12$aAncona, George.$tCan we help?$f2015.$x9780763673673",
                "=700  12$aBoelts, Maribeth,$d1964-$tThose shoes.$f2007.$x9780763642846",
                "=700  12$aBrantz, Loryn.$tFeminist Baby.$f2017.$x9781484778586",
                "=700  12$aBuitrago, Jairo.$tTwo white rabbits.$f2015.$x9781554987412",
                "=700  12$aBullard, Lisa.$tMy family, your family.$f2015.$x9781467749015",
                "=700  12$aCottin, Menena.$tThe black book of colors.$f©2008.$x9780888998736",
                "=700  12$aCoy, John$d1958-$tTheir great gift.$f2016.$x9781467780544",
                "=700  12$aEvans, Shane.$tWe march.$f2012.$x9781250073259",
                "=700  12$aGeorge, Liz.$tEmpathy.$f2016.$x9780531213803",
                "=700  12$aHall, Michael,$d1954-$tRed$f2015.$x9780062252074",
                "=700  12$aHerthel, Jessica.$tI am Jazz.$f2014.$x9780803741072",
                "=700  12$aHoffman, Mary,$d1945-$tThe great big green book.$f201.$x9781847804457",
                "=700  12$aKopp, Megan.$tBe the change in your community.$f2015.$x9780778706366",
                "=700  12$aLang, Suzanne.$tFamilies, families, families!$f2015.$x9780553499384",
                "=700  12$aLester, Julius,$d1939-2018.$tLet's talk about race.$f2005.$x9780064462266",
                "=700  12$aMyers, Christopher.$tWings.$f2000.$x9780590033770",
                "=700  12$aNelson, Kadir.$tIf you plant a seed.$f2015.$x9780062298898",
                "=700  12$aParr, Todd.$tIt's okay to be different.$f2001.$x9780316666039",
                "=700  12$aPaul, Miranda.$tWhose hands are these?$f2016.$x9781467752145",
                "=700  12$aPeete, Holly Robinson$d1964-$tMy brother Charlie$f2010$x9780545094665",
                "=700  12$aRinggold, Faith$tWe came to America$f2016.$x9780517709474",
                "=700  12$aRitchie, Scot$tLook where we live!$f2015$x9781771381024",
                "=700  12$aRotner, Shelley$tFamilies$f2015$x9780823430536",
                "=700  12$aRuurs, Margriet$tFamilies around the world$f2014$x9781894786577",
                "=700  12$aSkrypuch, Marsha Forchuk$tAdrift at sea$f2016.$x9781772780055",
                "=700  12$aSlade, Suzanne.$tThe soda bottle school$f2014$x9780884483717",
                "=700  12$aThompson, Laurie Ann$tEmmanuel's dream$f2022$x9780449817445",
                "=700  12$aWillems, Mo$tCan I play, too?$f2010$x9781423119913",
                "=700  12$aWoodson, Jacqueline$tEach kindness$f©2012$x9780399246524",
                "=730  02$aDVD (missing identifier)$xNone",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333400077950$oTeacher Set SOC A Empathy 1-10",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-Adrift at sea$nAdrift at sea$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Be the change in your community$nBe the change in your community$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Can I play, too?$nCan I play, too?$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Can we help?$nCan we help?$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Each kindness$nEach kindness$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Emmanuel's dream$nEmmanuel's dream$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Empathy$nEmpathy$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Families around the world$nFamilies around the world$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Families$nFamilies$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Families, families, families!$nFamilies, families, families!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Feminist Baby$nFeminist Baby$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-I am Jazz$nI am Jazz$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-If you plant a seed$nIf you plant a seed$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-It's okay to be different$nIt's okay to be different$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Let's talk about race$nLet's talk about race$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Look where we live!$nLook where we live!$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-My brother Charlie$nMy brother Charlie$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-My family, your family$nMy family, your family$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Red$nRed$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The black book of colors$nThe black book of colors$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The great big green book$nThe great big green book$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The soda bottle school$nThe soda bottle school$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Their great gift$nTheir great gift$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Those shoes$nThose shoes$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Two white rabbits$nTwo white rabbits$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-We came to America$nWe came to America$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-We march$nWe march$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Whose hands are these?$nWhose hands are these?$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Wings$nWings$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-DVD (missing identifier) [DVD]$nDVD (missing identifier) [DVD]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_topic_chinese_americans(self, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="21613075")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert sorted(legacy_set["local_genre_term"]) == sorted(
            [
                "Adventure",
                "Biography",
                "Comics & Graphic Novels",
                "Coming of Age",
                "Fantasy",
                "Fiction",
                "Romance",
            ]
        )
        assert sorted(legacy_set["local_topic_term"]) == sorted(
            [
                "Animals",
                "Asian Americans",
                "Chinese Americans",
                "Family",
                "Immigration",
                "New York City",
            ]
        )
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20172018xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC ELA$fTOPIC$pE$c3153",
                "=245  00$aAsian Pacific American Heritage Month Young Adult Collection.$pCopy 1 of 10",
                "=300  \\\\$a19 item(s)",
                '=500  \\\\$aSet consists of 1 copy of "Down and across", 1 copy of "Love, hate & other filters", 1 copy of "Saints and misfits", 1 copy of "Starfish", 1 copy of "All that I can fix", 1 copy of "The speaker", 1 copy of "Emergency contact", 1 copy of "Picture us in the light", 1 copy of "A line in the dark", 1 copy of "Warcross", 1 copy of "From Twinkle, with love", 1 copy of "Rebel Seoul", 1 copy of "The astonishing color of after", 1 copy of "You bring the distant near", 1 copy of "Noteworthy", 1 copy of "The epic crush of Genie Lo", 1 copy of "Cool Tokyo guide", 1 copy of "The best we could do", 1 copy of "Girl code".',
                "=520  \\\\$3A line in the dark$a\"When Chinese American teenager Jess Wong's best friend Angie falls in love with a girl from the nearby boarding school, Jess expects heartbreak. But when everybody's secrets start to be revealed, the stakes quickly elevate from love or loneliness to life or death\"-- Provided by publisher.",
                '=520  \\\\$3All that I can fix$a"In Makersville, Indiana, people know all about fifteen-year-old Ronney--he\'s from that mixed-race family with the dad who tried to kill himself, the pill-popping mom, and the genius kid sister. Can Ronney figure out a way to hold it together as all his worlds fall apart?"-- Provided by publisher.',
                "=520  \\\\$3Cool Tokyo guide$aTokyo is an astonishing world unto itself--a city for lovers of Japanese culture, fashion and great food that mixes the best of old and new. In Cool Tokyo Guide, Abby Denson, author of the popular Cool Japan Guide, turns her focus to Tokyo's exciting streets and a little bit beyond. Abby, her husband Matt, friend Yuuko and sidekick Kitty Sweet Tooth will introduce you to: A restaurant where clowns drive robots and mermaids ride on sharks; fantastic shops for lovers of everything from vintage manga to dollar-store treasures; great places to take kids--or be a kid, of any age--like the Ghibli Museum and Palette Town; famous sites both old and new, from Sensoji Temple to Tokyo Tower; major comic conventions in the anime, cosplay and manga capital of the world; must-visit spots like Ueno Park and even a few spots outside the city. This practical and fun comic book guide also helps you navigate everyday Tokyo life such as train etiquette, trash disposal, tricky toilets, department store fitting rooms, and the surgical mask phenomenon. There is also information on ways to prepare ahead of time to make the most of your stay in Tokyo. So whether you're planning a trip or taking an armchair sojourn, take this book with you and get ready for the best time ever!.",
                '=520  \\\\$3Down and across$aHis friends know what they want to do with the rest of their lives, but Scott Ferdowsi can hardly commit to a breakfast cereal, let alone a passion. With his parents pushing him to settle on a "practical" career, Scott sneaks off to Washington, DC, seeking guidance from a famous psychologist who claims to know the secret to success. He meets Fiora Buchanan, a ballsy college student whose life ambition is to write crossword puzzles. Now Scott is sneaking into bars, attempting to pick up girls at the National Zoo, and even giving the crossword thing a try. Will he be able to find out who he is-- and who he wants to be?-- Adapted from dust jacket.',
                '=520  \\\\$3Emergency contact$a"After a chance encounter, Penny and Sam become each other\'s emergency contacts and find themselves falling in love digitally, without the humiliating weirdness of having to see each other"-- Provided by publisher.',
                "=520  \\\\$3From Twinkle, with love$aCharming romantic comedy about an aspiring teen filmmaker who finds her voice and falls in love-- told through leters-- from the New York Times bestselling author of When Dimple Met Rishi.",
                "=520  \\\\$3Girl code$aThe teenage phenoms behind the viral video game Tampon Run share the story of their experience at Girls Who Code and their rise to fame, plus a look at starts-ups, women in tech, and the power of coding. This book includes bonus content to help you get started coding.",
                "=520  \\\\$3Love, hate & other filters$aMaya Aziz, seventeen, is caught between her India-born parents' world of college and marrying a suitable Muslim boy and her dream world of film school and dating her classmate, Phil, when a terrorist attack changes her life forever.",
                "=520  \\\\$3Noteworthy$aAfter learning that her deep voice is keeping her from being cast in plays at her exclusive performing arts school, Jordan Sun, junior, auditions for an all-male octet hoping for a chance to perform internationally.",
                "=520  \\\\$3Picture us in the light$aDanny Cheng has always known his parents have secrets. But when he discovers a taped-up box in his father's closet filled with old letters and a file on a powerful Bay Area family, he realizes there's much more to his family's past than he ever imagined. Danny has been an artist for as long as he can remember, and it seems his future is set, with a scholarship to RISD and his family's blessing to pursue the career he's always dreamed of. Still, contemplating a future without his best friend, Harry Wong, by his side makes Danny feel a panic he can barely put into words. Harry's and Danny's lives are deeply intertwined, and as they approach the one-year anniversary of a tragedy that shook their friend group to its core, Danny can't stop asking himself if Harry is truly in love with his girlfriend, Regina Chan. When Danny digs deeper into his parents' past, he uncovers a secret that disturbs the foundations of his family history, and the carefully constructed façade his parents have maintained begins to crumble. With everything Danny cares about in danger of being stripped away, he must face the ghosts of the past in order to build a future that belongs to him. -- From dust jacket.",
                "=520  \\\\$3Rebel Seoul$aIn 2199 in the Neo State of Korea, eighteen-year-old Jaewon is partnered with supersoldier Tera, but their evolving love is threatened when Jaewon must choose among conflicting loyalties--to the totalitarian government that promises to end all war, the nationalist rebels his father followed, or the crime syndicate staging a coup.",
                "=520  \\\\$3Saints and misfits$aThere are three kinds of people in my life: 1. Saints, those special people moving the world forward. Sometimes you gaze right through them. Or, at least, I do. They're in your face so much, you can't see them, like how you can't see your nose. 2. Misfits, people who don't belong. Like me--the way I don't fit into Dad's brand-new family or in the leftover one composed of Mom and my older brother, Mama's -Boy Muhammad. Also, there's Jeremy and me. Misfits. Because although, alliteratively speaking, Janna and Jeremy sound good together, we don't go together. Same planet, different worlds. But sometimes worlds collide and beautiful things happen, right? 3. Monsters. Well, monsters wearing saint masks, like in Flannery O'Connor's stories. Like the monster at my mosque. People think he's holy, untouchable, but nobody has seen under the mask. Except me. -- From dust jacket.",
                "=520  \\\\$3Starfish$aKiko Himura yearns to escape the toxic relationship with her mother by getting into her dream art school, but when things do not work out as she hoped Kiko jumps at the opportunity to tour art schools with her childhood friend, learning life-changing truths about herself and her past along the way.",
                "=520  \\\\$3The astonishing color of after$aAfter her mother's suicide, grief-stricken Leigh Sanders travels to Taiwan to stay with grandparents she never met, determined to find her mother who she believes turned into a bird.",
                '=520  \\\\$3The best we could do$a"Exploring the anguish of immigration and the lasting effects that displacement has on a child and her family, Bui documents the story of her family\'s daring escape after the fall of South Vietnam in the 1970s, and the difficulties they faced building new lives for themselves"--Publisher description.',
                "=520  \\\\$3The epic crush of Genie Lo$aGenie Lo is one among droves of Ivy-hopeful overachievers in her sleepy Bay Area suburb. You know, the type who wins. When she's not crushing it at volleyball or hitting the books, Genie is typically working on how to crack the elusive Harvard entry code. But when her hometown comes under siege from hellspawn straight out of Chinese folklore, her priorities are dramatically rearranged. Enter Quentin Sun, a mysterious new kid in class who becomes Genie's self-appointed guide to battling demons. While Genie knows Quentin only as an attractive transfer student with an oddly formal command of the English language, in another reality he is Sun Wukong, the mythological Monkey King incarnate -- right down to the furry tail and penchant for peaches. Suddenly, acing the SATs is the least of Genie's worries. The fates of her friends, family, and the entire Bay Area all depend on her summoning an inner power that Quentin assures her is strong enough to level the very gates of Heaven. But every second Genie spends tapping into the secret of her true nature is a second in which the lives of her loved ones hang in the balance.",
                '=520  \\\\$3The speaker$a"Sefia and Archer\'s adventure continues as Archer searches for a way to combat his nightmares of his time with the impressors and Sefia becomes more and more consumed by her study of the Book"-- Provided by publisher.',
                '=520  \\\\$3Warcross$a"When teenage coder Emika Chen hacks her way into the opening tournament of the Warcross Championships, she glitches herself into the game as well as a sinister plot with major consequences for the entire Warcross empire"-- Provided by publisher.',
                "=520  \\\\$3You bring the distant near$aFrom 1965 through the present, an Indian American family adjusts to life in New York City, alternately fending off and welcoming challenges to their own traditions.",
                "=521  2\\$a9-12",
                "=526  8\\$aLanguage Arts",
                "=690  \\7$aTopic.$2bookops",
                "=691  \\7$aAnimals.$2bookops",
                "=691  \\7$aChinese Americans.$2bookops",
                "=691  \\7$aFamily.$2bookops",
                "=691  \\7$aAsian Americans.$2bookops",
                "=691  \\7$aImmigration.$2bookops",
                "=691  \\7$aNew York City.$2bookops",
                "=695  \\7$aAdventure.$2bookops",
                "=695  \\7$aBiography.$2bookops",
                "=695  \\7$aComics & Graphic Novels.$2bookops",
                "=695  \\7$aFantasy.$2bookops",
                "=695  \\7$aComing of Age.$2bookops",
                "=695  \\7$aFiction.$2bookops",
                "=695  \\7$aRomance.$2bookops",
                "=700  12$aAhmadi, Arvin.$tDown and across.$f2018.$x9780425289877",
                "=700  12$aAhmed, Samira.$tLove, hate & other filters.$f2018.$x9781616958473",
                "=700  12$aAli, S. K.$tSaints and misfits.$f2017.$x9781481499248",
                "=700  12$aBowman, Akemi Dawn.$tStarfish.$f2017.$x9781481487726",
                "=700  12$aBui, Thi.$tThe best we could do.$f2017.$x9781419718779",
                "=700  12$aChan, Crystal.$tAll that I can fix.$fJune 2018.$x9781534408883",
                "=700  12$aChee, Traci.$tThe speaker.$f2017.$x9780399176784",
                "=700  12$aChoi, Mary H. K.$tEmergency contact.$f2018.$x9781534408968",
                "=700  12$aDenson, Abby.$tCool Tokyo guide.$f2018.$x9784805314418",
                "=700  12$aGilbert, Kelly Loy.$tPicture us in the light.$f2018.$x9781484726020",
                "=700  12$aGonzales, Andrea.$tGirl code.$f2017.$x9780062472502",
                "=700  12$aLo, Malinda.$tA line in the dark.$f2017.$x9780735227422",
                "=700  12$aLu, Marie,$d1984-$tWarcross.$f2017.$x9780399547966",
                "=700  12$aMenon, Sandhya.$tFrom Twinkle, with love.$f2018.$x9781481495400",
                "=700  12$aOh, Axie.$tRebel Seoul.$f2017.$x9781620142998",
                "=700  12$aPan, Emily X. R.$tThe astonishing color of after.$f2018.$x9780316463997",
                "=700  12$aPerkins, Mitali.$tYou bring the distant near.$f2017.$x9780374304904",
                "=700  12$aRedgate, Riley.$tNoteworthy.$f2017.$x9781419723735",
                "=700  12$aYee, F. C.$tThe epic crush of Genie Lo.$f2017.$x9781419725487",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333400088494$oTeacher Set ELA D Asian American 1-2",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-A line in the dark$nA line in the dark$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-All that I can fix$nAll that I can fix$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Cool Tokyo guide$nCool Tokyo guide$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Down and across$nDown and across$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Emergency contact$nEmergency contact$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-From Twinkle, with love$nFrom Twinkle, with love$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Girl code$nGirl code$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Love, hate & other filters$nLove, hate & other filters$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Noteworthy$nNoteworthy$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Picture us in the light$nPicture us in the light$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Rebel Seoul$nRebel Seoul$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Saints and misfits$nSaints and misfits$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Starfish$nStarfish$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The astonishing color of after$nThe astonishing color of after$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The best we could do$nThe best we could do$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The epic crush of Genie Lo$nThe epic crush of Genie Lo$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-The speaker$nThe speaker$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-Warcross$nWarcross$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-You bring the distant near$nYou bring the distant near$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )

    def test_topic_new_york_city(self, caplog, live_creds, mock_control_number_file):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="19538471")
        valid_set_copies = self.BUILDER.build_set_copies(set_data=legacy_set)
        bib_records = [i.to_bib() for i in valid_set_copies]
        field_strings = [str(i) for i in bib_records[0].fields]
        assert legacy_set["local_genre_term"] == []
        assert legacy_set["local_topic_term"] == ["New York City"]
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
        assert sorted(field_strings) == sorted(
            [
                "=001  nn-mlnyc-0000001",
                "=003  BookOps",
                "=008  000101i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
                "=091  \\\\$aMLNYC SOC$fCLUB$pB$c358",
                "=245  00$aThis is New York by M. Sasek.$pCopy 1 of 7",
                "=300  \\\\$a10 item(s)",
                '=500  \\\\$aSet consists of 10 copies of "This is New York".',
                "=520  \\\\$3This is New York$aA pictorial tour of Manhattan Island presenting drawings of its neighborhoods, transportation and traffic, buildings, and the city's activities, from the local shoeshine stall to Wall Street.",
                "=521  2\\$aK-2",
                "=526  8\\$aSocial Studies",
                "=690  \\7$aBook Club.$2bookops",
                "=691  \\7$aNew York City.$2bookops",
                "=700  12$aSasek, M,$d1916-1980$tThis is New York.$f2003.$x9780789308849",
                "=901  \\\\$amlnyc-bot$bCATBL",
                "=901  \\\\$n33333402207449$oTeacher Set SOC A Book Club Set NYC History - This Is New York 1-1",
                "=909  \\\\$aOCLC Holdings Exclusion",
                "=910  \\\\$aBL",
                "=949  \\\\$a*b2=8;b3=e;bn=ed;",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
                "=949  \\\\$h10$i[BARCODE]-This is New York$nThis is New York$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            ]
        )
        assert len(caplog.records) == 2
        assert [i.msg for i in caplog.records] == [
            "(19538471) Building teacher set from legacy data.",
            "(19538471) Created 7 valid copy/copies of set.",
        ]
