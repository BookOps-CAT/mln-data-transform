import pytest

from mln_data_transform.legacy_build import LegacyTeacherSetBuilder


class TestLegacyTeacherSetBuilder:
    BUILDER = LegacyTeacherSetBuilder(file="data/foo_bar.csv")

    def test_build_legacy_sets(self, mock_set):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
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
        valid_set_copies = self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
        )
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
        valid_set_copies = self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
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
        valid_set_copies = self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
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
        valid_set_copies = self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
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
            valid_set_copies = self.BUILDER.build_set_copies(
                legacy_set,
                control_number="nn-mlnyc-0000001",
                log_id=legacy_set["bib_id"],
            )
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

    def test_build_legacy_set_validation_error(self, mock_invalid_set, caplog):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        assert len(caplog.records) == 2
        assert (
            caplog.records[0].msg == "(12345678) Building teacher set from legacy data."
        )
        assert (
            caplog.records[1].msg.startswith(
                'Validation errors for set: [{"type":"get_attribute_error","loc":'
            )
            is True
        )
        assert legacy_set is None

    def test_build_set_copies_validation_error(self, mock_invalid_set_copies, caplog):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        valid_set_copies = self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
        )
        assert len(caplog.records) == 2
        assert (
            caplog.records[0].msg == "(12345678) Building teacher set from legacy data."
        )
        assert (
            caplog.records[1].msg.startswith(
                "Validation errors for set copies: [{'type': 'list_type'"
            )
            is True
        )
        assert valid_set_copies is None


class TestTeacherSetBuilderLogging:
    BUILDER = LegacyTeacherSetBuilder(file="data/foo_bar.csv")

    def test_build_legacy_sets(
        self, mock_session_managers, caplog, mock_location_mapping
    ):
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
        )
        assert len(caplog.records) == 2
        assert [i.msg for i in caplog.records] == [
            "(12345678) Building teacher set from legacy data.",
            "(12345678) Created 2 valid copy/copies of set.",
        ]

    def test_build_legacy_sets_debug(
        self, mock_session_managers, caplog, mock_location_mapping
    ):
        caplog.set_level("DEBUG")
        legacy_set = self.BUILDER.build_legacy_set(bib_id="12345678")
        self.BUILDER.build_set_copies(
            set_data=legacy_set,
            control_number="nn-mlnyc-0000001",
            log_id=legacy_set["bib_id"],
        )
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
            self.BUILDER.build_set_copies(
                set_data=legacy_set,
                control_number="nn-mlnyc-0000001",
                log_id=legacy_set["bib_id"],
            )
        assert str(exc.value) == "(12345678) Item status issue."
