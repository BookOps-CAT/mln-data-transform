from mln_data_transform.legacy import LegacyBibData, LegacyItemData


class TestLegacyData:
    def test_legacy_bib_data_from_json(self, platform_test_data):
        legacy_bib = LegacyBibData(
            bib_id=platform_test_data["id"],
            item_ids=platform_test_data["items"],
            set_title=platform_test_data["title"],
            fixed_fields=platform_test_data["fixedFields"],
            var_fields=platform_test_data["varFields"],
            language=platform_test_data["lang"],
        )
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.isbns == ["9780789308849"]
        assert legacy_bib.leader == "00000nam  2200000 a 4500"
        assert legacy_bib.physical_description == "10 v."

    def test_legacy_bib_data_from_json_None(self, platform_test_data):
        legacy_bib = LegacyBibData(
            bib_id=platform_test_data["id"],
            item_ids=platform_test_data["items"],
            set_title=platform_test_data["title"],
            fixed_fields={},
            var_fields={},
            language=platform_test_data["lang"],
        )
        assert legacy_bib.isbns == []
        assert legacy_bib.leader is None
        assert legacy_bib.physical_description is None

    def test_legacy_item_data_from_json(self, platform_test_data, platform_test_item):
        legacy_item = LegacyItemData(
            item_count=len(platform_test_data["items"].split(",")),
            item_id=platform_test_item["id"],
            call_number=platform_test_item["callNumber"],
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

    def test_legacy_item_data_from_json_None(self, platform_test_data):
        legacy_bib = LegacyItemData(
            item_count=len(platform_test_data["items"].split(",")),
            item_id=platform_test_data["items"].split(",")[0],
            call_number="call number",
        )
        assert legacy_bib.call_number_components is None
        assert legacy_bib.enumeration is None
        assert legacy_bib.grade_level is None
        assert legacy_bib.local_set_type is None
        assert legacy_bib.shelf_number is None
        assert legacy_bib.study_program_info is None
