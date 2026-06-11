import pytest

from mln_data_transform.legacy import (
    LegacyBibData,
    LegacyItemData,
    LegacyTeacherSet,
    LegacyTeacherSetBatch,
)


class TestLegacyData:
    def test_legacy_bib_data(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            fixed_fields=test_bib_data["fixedFields"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.isbns == ["9780789308849"]
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.physical_description == "10 v."
        assert legacy_bib.record_type == "a"
        assert legacy_bib.copy_count == 10

    def test_legacy_bib_data_missing_fields(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            fixed_fields={},
            var_fields={},
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == []
        assert legacy_bib.leader is None
        assert legacy_bib.physical_description is None
        assert legacy_bib.record_type == "a"

    @pytest.mark.parametrize(
        "arg,output",
        [
            ("Five copies of two titles", 5),
            ("Three copies of ten titles", 3),
            ("Five copies of six titles", 5),
            ("Three copies of eight titles", 3),
            ("Four copies of four titles", 4),
            ("Five copies of four titles", 5),
            ("Five copies of two titles", 5),
            ("2 copies of 11 titles", 2),
            ("1 copy of 16 titles", 1),
            ("2 copies of 13 titles", 2),
            ("3 copies of 11 titles", 3),
            ("One copy of 35 titles", 1),
            ("Tabletop Game - ", 1),
            ("Game - ", 1),
            ("DVD - ", 1),
            ("Game (Board Game) - ", 1),
        ],
    )
    def test_legacy_bib_data_pattern_matching(self, test_bib_data, arg, output):
        test_bib_data["varFields"] = [
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "500",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": "Teacher set"}],
            },
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "520",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": f"{arg} Baz - Qux. "}],
            },
        ]
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            fixed_fields=test_bib_data["fixedFields"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.copy_count == output

    def test_legacy_bib_data_call_number_pattern_error(self, test_bib_data):
        var_fields = [i for i in test_bib_data["varFields"] if i["marcTag"] != "091"]
        var_fields.append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "091",
                "fieldTag": "c",
                "subfields": [{"tag": "a", "content": "call number"}],
            }
        )
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            fixed_fields=test_bib_data["fixedFields"],
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        with pytest.raises(ValueError) as exc:
            legacy_bib.call_number_components
        assert (
            str(exc.value)
            == "Call number 'call number' does not match pattern. Cannot extract components."
        )

    def test_legacy_item_data(self, test_item_data):
        legacy_item = LegacyItemData(
            shelf_number="1",
            item_id=test_item_data["id"],
            call_number=test_item_data["callNumber"],
            barcode="33333123456789",
        )
        assert (
            legacy_item.call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1"
        )
        assert (
            legacy_item.bib_call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1"
        )

    @pytest.mark.parametrize(
        "arg,result",
        [
            ("Math B Assorted 1-10", "Math B Assorted 1"),
            ("ELA D Genre - Horror 1-1", "ELA D Genre - Horror 1"),
            (
                "Language Arts ENG YA Book Club 185-5",
                "Language Arts ENG YA Book Club 185",
            ),
            (
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1-1",
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1",
            ),
            ("Arts A BIOG - Musicians (Jazz) 1-2", "Arts A BIOG - Musicians (Jazz) 1"),
            ("ELA D Horror Large Print 1-1", "ELA D Horror Large Print 1"),
            (
                "Language Arts ENG MG Book Club Graphic Novel 29-1",
                "Language Arts ENG MG Book Club Graphic Novel 29",
            ),
        ],
    )
    def test_legacy_item_data_call_number_patterns(self, arg, result):
        legacy_item = LegacyItemData(
            item_id="i123456789",
            call_number=f"Teacher Set {arg}",
            barcode="33333123456789",
            shelf_number=1,
        )
        assert legacy_item.call_number == f"Teacher Set {arg}"
        assert legacy_item.bib_call_number == f"Teacher Set {result}"


class TestLegacyTeacherSetBatch:
    def test_create_teacher_sets(self, mock_responses):
        batch = LegacyTeacherSetBatch(
            bib_id="12345",
            item_mapping={"33333402207449": "1"},
            control_number="nn-mlnyc-0000001",
        )
        sets = batch.create_teacher_sets()
        assert isinstance(sets[0], LegacyTeacherSet)
        assert len(sets) == 1
        assert (
            sets[0].contents_note == 'Set consists of 10 copies of "This is New York".'
        )
        assert sets[0].pub_dates == ["2003"]
        assert len(sets[0].subjects) == 2

    def test_create_teacher_sets_missing_data(
        self, mock_worldcat_response_missing_data
    ):
        batch = LegacyTeacherSetBatch(
            bib_id="12345",
            item_mapping={"33333402207449": "1"},
            control_number="nn-mlnyc-0000001",
        )
        sets = batch.create_teacher_sets()
        assert sets[0].parts[0].author is None
        assert sets[0].parts[0].author_dates is None
        assert sets[0].parts[0].description == ""
        assert sets[0].parts[0].pub_date == "20uu"
        assert sets[0].parts[0].subjects == []
        assert sets[0].pub_dates == ["20uu"]
        assert sets[0].subjects == []

    def test_create_teacher_sets_no_pub_dates(
        self, mock_worldcat_response_no_pub_dates
    ):
        batch = LegacyTeacherSetBatch(
            bib_id="12345",
            item_mapping={"33333402207449": "1"},
            control_number="nn-mlnyc-0000001",
        )
        sets = batch.create_teacher_sets()
        assert sets[0].parts[0].pub_date is None
        assert sets[0].pub_dates == []
