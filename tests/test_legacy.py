from mln_data_transform.legacy import LegacyTeacherSetData


class TestTeacherSetBib:
    def test_teacher_set_from_json(self, platform_test_data):
        legacy_bib = LegacyTeacherSetData(
            bib_id=platform_test_data["id"],
            item_ids=platform_test_data["items"],
            set_title=platform_test_data["title"],
            fixed_fields=platform_test_data["fixedFields"],
            var_fields=platform_test_data["varFields"],
            language=platform_test_data["lang"],
        )
        assert legacy_bib.isbns == ["9780789308849"]
        assert legacy_bib.physical_description == "10 v."
        assert (
            legacy_bib.legacy_call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1"
        )
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.subjects[0] == {
            "ind1": " ",
            "ind2": "0",
            "marcTag": "651",
            "subfields": [
                {"tag": "a", "content": "New York (N.Y.)"},
                {"tag": "x", "content": "Description and travel."},
            ],
        }

    def test_teacher_set_from_json_None(self, platform_test_data):
        legacy_bib = LegacyTeacherSetData(
            bib_id=platform_test_data["id"],
            item_ids=platform_test_data["items"],
            set_title=platform_test_data["title"],
            fixed_fields={},
            var_fields={},
            language=platform_test_data["lang"],
        )
        assert legacy_bib.isbns is None
        assert legacy_bib.physical_description is None
        assert legacy_bib.legacy_call_number is None
        assert legacy_bib.leader is None
