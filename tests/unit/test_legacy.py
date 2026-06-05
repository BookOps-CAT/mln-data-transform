import pytest

from mln_data_transform.legacy import (
    LegacyBibData,
    LegacyItemData,
    LegacyTeacherSet,
    LegacyTeacherSetBatch,
)


@pytest.fixture
def test_legacy_bib(test_bib_data) -> LegacyBibData:
    """Contains 7 item IDs, 1 ISBN, and notes there are 10 copies of the title."""
    return LegacyBibData(
        bib_id=test_bib_data["id"],
        set_title=test_bib_data["title"],
        fixed_fields=test_bib_data["fixedFields"],
        var_fields=test_bib_data["varFields"],
        language=test_bib_data["lang"]["code"],
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
        assert legacy_bib.copy_info == (10, 1)

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
            ("Five copies of two titles", (5, 2)),
            ("Three copies of ten titles", (3, 10)),
            ("Five copies of six titles", (5, 6)),
            ("Three copies of eight titles", (3, 8)),
            ("Four copies of four titles", (4, 4)),
            ("Five copies of four titles", (5, 4)),
            ("Five copies of two titles", (5, 2)),
            ("2 copies of 11 titles", (2, 11)),
            ("1 copy of 16 titles", (1, 16)),
            ("2 copies of 13 titles", (2, 13)),
            ("3 copies of 11 titles", (3, 11)),
            ("One copy of 35 titles", (1, 35)),
            ("Tabletop Game - ", (1, 1)),
            ("Game - ", (1, 1)),
            ("DVD - ", (1, 1)),
            ("Game (Board Game) - ", (1, 1)),
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
        assert legacy_bib.copy_info == output

    def test_legacy_bib_data_no_copy_info(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            fixed_fields={},
            var_fields={},
            language=test_bib_data["lang"],
        )
        with pytest.raises(ValueError) as exc:
            legacy_bib.copy_info
        assert (
            str(exc.value)
            == "500 and 520 fields do not match pattern. Cannot extract copy info: []"
        )

    def test_legacy_item_data(self, test_bib_data, test_item_data):
        legacy_item = LegacyItemData(
            legacy_item_count=len(test_bib_data["items"].split(",")),
            item_id=test_item_data["id"],
            call_number=test_item_data["callNumber"],
            barcode="33333123456789",
            shelf_number="1",
        )
        assert (
            legacy_item.call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1"
        )
        assert legacy_item.set_copy_number == 1
        assert legacy_item.grade_level == "A"
        assert legacy_item.set_type == "CLUB"
        assert legacy_item.shelf_number == "1"
        assert legacy_item.subject == "SOC"

    @pytest.mark.parametrize(
        "arg,subj,grade,enhanced,type,enum",
        [
            ("Math B Assorted 1-10", "MATH", "B", None, "TOPIC", 10),
            ("ELA D Genre - Horror 1-1", "ELA", "D", None, "TOPIC", 1),
            ("Language Arts ENG YA Book Club 185-5", "ELA", "E", None, "CLUB", 5),
            ("SPLA C Animals 1-1", "SPLA", "C", None, "TOPIC", 1),
            (
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1-1",
                "SOC",
                "C",
                "E",
                "CLUB",
                1,
            ),
            ("Arts A BIOG - Musicians (Jazz) 1-2", "ART", "A", None, "TOPIC", 2),
            ("Arts D BC Hamilton 1-3", "ART", "D", None, "CLUB", 3),
            ("Game B Mole 1-1", "GAME", "B", None, "GAME", 1),
            ("Games ENG MG 1-2", "GAME", "D", None, "GAME", 2),
            ("ELA D Storytelling 1-1", "ELA", "D", None, "STORY", 1),
            ("ELA D Audiobooks 1-1", "ELA", "D", None, "AUDIO", 1),
            ("ELA D Horror Large Print 1-1", "ELA", "D", None, "LPRINT", 1),
            ("Language Arts RUM J 105-2", "RULA", "C", None, "TOPIC", 2),
            (
                "Language Arts ENG MG Book Club Graphic Novel 29-1",
                "ELA",
                "D",
                None,
                "CLUB",
                1,
            ),
        ],
    )
    def test_legacy_item_data_call_number_patterns(
        self, arg, subj, grade, enhanced, type, enum
    ):
        legacy_item = LegacyItemData(
            legacy_item_count=2,
            item_id="i123456789",
            call_number=f"Teacher Set {arg}",
            barcode="33333123456789",
            shelf_number="1",
        )
        assert legacy_item.call_number == f"Teacher Set {arg}"
        assert legacy_item.call_number_components[0] == f"Teacher Set {arg}"
        assert legacy_item.subject == subj
        assert legacy_item.grade_level == grade
        assert legacy_item.enhanced == enhanced
        assert legacy_item.set_type == type
        assert legacy_item.shelf_number == "1"
        assert legacy_item.set_copy_number == enum

    def test_legacy_item_data_call_number_pattern_error(self):
        legacy_item = LegacyItemData(
            legacy_item_count=2,
            item_id="i123456789",
            call_number="call number",
            barcode="33333123456789",
            shelf_number="1",
        )
        with pytest.raises(ValueError) as exc:
            legacy_item.call_number_components
        assert (
            str(exc.value)
            == "Call number 'call number' does not match pattern. Cannot extract components."
        )


class TestLegacyTeacherSetBatch:
    def test_create_teacher_sets(self, mock_responses):
        batch = LegacyTeacherSetBatch(
            bib_id="12345", item_mapping={"33333402207449": "1"}
        )
        sets = batch.create_teacher_sets()
        assert isinstance(sets[0], LegacyTeacherSet)
        assert len(sets) == 1
