import pytest

from mln_data_transform.legacy import LegacyBibData, LegacyItemData


class TestLegacyData:
    def test_legacy_bib_data(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            item_ids=test_bib_data["items"],
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
        assert legacy_bib.copy_info == "Ten copies of one title"

    def test_legacy_bib_data_missing_fields(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            item_ids=test_bib_data["items"],
            set_title=test_bib_data["title"],
            fixed_fields={},
            var_fields={},
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == []
        assert legacy_bib.leader is None
        assert legacy_bib.physical_description is None
        assert legacy_bib.record_type == "a"

    def test_legacy_bib_data_secondary_match(self, test_bib_data):
        var_fields = [
            i for i in test_bib_data["varFields"] if i["marcTag"] not in ["500", "520"]
        ]
        var_fields.append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "500",
                "fieldTag": "n",
                "subfields": [
                    {"tag": "a", "content": "Duration of play: 45-60 minutes."}
                ],
            }
        )
        var_fields.append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "520",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": "Board Game - Foo bar baz."}],
            }
        )
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            item_ids=test_bib_data["items"],
            set_title=test_bib_data["title"],
            fixed_fields=test_bib_data["fixedFields"],
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.isbns == ["9780789308849"]
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.physical_description == "10 v."
        assert legacy_bib.record_type == "a"
        assert legacy_bib.copy_info == "Board Game - "

    def test_legacy_bib_data_no_copy_info(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            item_ids=test_bib_data["items"],
            set_title=test_bib_data["title"],
            fixed_fields={},
            var_fields={},
            language=test_bib_data["lang"],
        )
        with pytest.raises(ValueError) as exc:
            legacy_bib.copy_info
        assert (
            str(exc.value)
            == "500 and 520 fields do not match pattern. Cannot extract copy info. "
            "500 fields: []. 520 fields: []"
        )

    def test_legacy_item_data(self, test_bib_data, test_item_data):
        legacy_item = LegacyItemData(
            item_count=len(test_bib_data["items"].split(",")),
            item_id=test_item_data["id"],
            call_number=test_item_data["callNumber"],
        )
        assert (
            legacy_item.call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1"
        )
        assert (
            legacy_item.call_number_components[0]
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1"
        )
        assert legacy_item.enumeration == "1"
        assert legacy_item.grade_level == "A"
        assert (
            legacy_item.local_set_type == "Book Club Set NYC History - This Is New York"
        )
        assert legacy_item.shelf_number == "1"
        assert legacy_item.study_program_info == "SOC"

    @pytest.mark.parametrize(
        "arg,subj,grade,type,shelf,enum",
        [
            ("Math B Assorted 1-10", "Math", "B", "Assorted", "1", "10"),
            ("ELA D Genre - Horror 1-1", "ELA", "D", "Genre - Horror", "1", "1"),
            (
                "Language Arts ENG YA Book Club 185-5",
                "Language Arts ENG",
                "YA",
                "Book Club",
                "185",
                "5",
            ),
            ("SPLA C Animals 1-1", "SPLA", "C", "Animals", "1", "1"),
            (
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1-1",
                "SOC",
                "C",
                "Enhanced Book Club Set Narrative of the Life of Frederick Douglass",
                "1",
                "1",
            ),
            (
                "Arts A BIOG - Musicians (Jazz) 1-2",
                "Arts",
                "A",
                "BIOG - Musicians (Jazz)",
                "1",
                "2",
            ),
            ("Arts D BC Hamilton 1-3", "Arts", "D", "BC Hamilton", "1", "3"),
            ("Game B Mole 1-1", "Game", "B", "Mole", "1", "1"),
            ("Games ENG MG 1-2", "Games ENG", "MG", "", "1", "2"),
            ("Language Arts RUM J 105-2", "Language Arts RUM", "J", "", "105", "2"),
            (
                "Language Arts ENG MG Book Club Graphic Novel 29-1",
                "Language Arts ENG",
                "MG",
                "Book Club Graphic Novel",
                "29",
                "1",
            ),
        ],
    )
    def test_legacy_item_data_call_number_patterns(
        self, arg, subj, grade, type, shelf, enum
    ):
        legacy_item = LegacyItemData(
            item_count=2, item_id="i123456789", call_number=f"Teacher Set {arg}"
        )
        assert legacy_item.call_number == f"Teacher Set {arg}"
        assert legacy_item.call_number_components[0] == f"Teacher Set {arg}"
        assert legacy_item.study_program_info == subj
        assert legacy_item.grade_level == grade
        assert legacy_item.local_set_type == type
        assert legacy_item.shelf_number == shelf
        assert legacy_item.enumeration == enum

    def test_legacy_item_data_call_number_pattern_error(self):
        legacy_item = LegacyItemData(
            item_count=2, item_id="i123456789", call_number="call number"
        )
        with pytest.raises(ValueError) as exc:
            legacy_item.call_number_components
        assert (
            str(exc.value)
            == "Call number 'call number' does not match pattern. Cannot extract components."
        )
