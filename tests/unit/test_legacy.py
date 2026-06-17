import pytest

from mln_data_transform.legacy import (
    LegacyBibData,
    LegacyItemData,
    LegacyTeacherSet,
    LegacyTeacherSetData,
)
from mln_data_transform.transform import PlatformManager


class TestLegacyBibData:
    def test_legacy_bib_data(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == ["9781234567897", "9780987654328"]
        assert legacy_bib.physical_description == "10 item(s)"
        assert legacy_bib.record_type == "a"
        assert legacy_bib.copy_count == 10

    def test_legacy_bib_data_missing_fields(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields={},
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == []
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
            ("Foo, Bar", None),
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
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.copy_count == output

    @pytest.mark.parametrize(
        "arg,enhanced,grade,set_type,subject",
        [
            ("Math B Assorted 1", None, "B", "TOPIC", "MAT"),
            ("FRLA D Genre - Horror 1", None, "D", "TOPIC", "FRLA"),
            ("Language Arts CHI YA Book Club 185", None, "E", "CLUB", "CHLA"),
            (
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1",
                "E",
                "C",
                "CLUB",
                "SOC",
            ),
            ("Arts A BIOG - Musicians (Jazz) 1", None, "A", "TOPIC", "ART"),
            ("ELA D Horror Large Print 1", None, "D", "LPRINT", "ELA"),
            (
                "Language Arts ENG MG Book Club Graphic Novel 29",
                None,
                "D",
                "CLUB",
                "ELA",
            ),
            ("Language Arts ENG YA Audiobook 194", None, "E", "AUDIO", "ELA"),
            ("Game C Catan 1", None, "C", "GAME", "GAME"),
            ("ELA D Storytelling 1", None, "D", "STORY", "ELA"),
            ("Language Arts SPA J 135", None, "C", "TOPIC", "SPLA"),
            ("Language Arts POL J 99", None, "C", "TOPIC", "WorldLang"),
        ],
    )
    def test_legacy_bib_data_call_number_patterns(
        self, test_bib_data, arg, enhanced, grade, set_type, subject
    ):
        var_fields = [i for i in test_bib_data["varFields"] if i["marcTag"] != "091"]
        var_fields.append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "091",
                "fieldTag": "c",
                "subfields": [{"tag": "a", "content": f"Teacher Set {arg}"}],
            }
        )
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        assert legacy_bib.enhanced == enhanced
        assert legacy_bib.grade_level == grade
        assert legacy_bib.set_type == set_type
        assert legacy_bib.subject == subject

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
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        with pytest.raises(ValueError) as exc:
            legacy_bib.call_number_components
        assert (
            str(exc.value)
            == "Call number 'call number' does not match pattern. Cannot extract components."
        )

    @pytest.mark.parametrize(
        "arg,output",
        [
            ("9780789308849 ", ["9780789308849"]),
            ("978-0-78-930884-9 ", ["9780789308849"]),
            ("9780789308849 9781234567890", ["9780789308849"]),
            ("978-0-78-930884-9 asdfgh", ["9780789308849"]),
            ("978-0-78-930884-X 068816241X", ["068816241X"]),
            (" 0789308843", ["0789308843"]),
            ("0-7893-0884-3", ["0789308843"]),
            (" 068816241X ", ["068816241X"]),
            ("0-7893-0884-3 97897897X9", ["0789308843"]),
            ("068816241X  0-7893-0884-Z ", ["068816241X"]),
        ],
    )
    def test_legacy_bib_data_validate_isbns(self, test_bib_data, arg, output):
        test_bib_data["varFields"] = [
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "944",
                "fieldTag": "y",
                "subfields": [{"tag": "a", "content": arg}],
            }
        ]
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == output


class TestLegacyItemData:
    def test_legacy_item_data(self):
        legacy_item = LegacyItemData(
            item_id="i123456789",
            call_number="Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1",
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
        )
        assert legacy_item.call_number == f"Teacher Set {arg}"
        assert legacy_item.bib_call_number == f"Teacher Set {result}"


class TestLegacyTeacherSetData:
    def test_legacy_set_data(
        self, stub_metadata_session, stub_platform_session, caplog
    ):
        platform_manager = PlatformManager()
        legacy_set_data = LegacyTeacherSetData(
            bib_id="12345", platform_manager=platform_manager
        )
        assert (
            legacy_set_data.bib_data.call_number
            == "Teacher Set SOC A Foo Bar Book Club 1"
        )
        assert len(legacy_set_data.item_data) == 2

    def test_legacy_set_data_get_parts(
        self, stub_metadata_session, stub_platform_session, caplog
    ):
        platform_manager = PlatformManager()
        legacy_set_data = LegacyTeacherSetData(
            bib_id="12345", platform_manager=platform_manager
        )
        worldcat_parts = legacy_set_data.get_worldcat_data_for_parts()
        assert len(worldcat_parts) == 2
        assert worldcat_parts[0]["author_name"] == "Bar, Foo"
        assert worldcat_parts[0]["author_dates"] == "1980-"
        assert worldcat_parts[0]["description"] == "Fake description of book."
        assert worldcat_parts[0]["isbn"] == "9781234567897"
        assert worldcat_parts[0]["pub_date"] == "2000"
        assert worldcat_parts[0]["subjects"] == [
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
                "subfields": [("a", "Comics (Graphic works)."), ("2", "lcgft")],
            },
        ]
        assert worldcat_parts[0]["title"] == "Fake book 1"


class TestLegacyTeacherSet:
    def test_legacy_set(self, stub_platform_session, caplog, mock_worldcat_response):
        platform_manager = PlatformManager()
        legacy_set_data = LegacyTeacherSetData(
            bib_id="12345", platform_manager=platform_manager
        )
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert legacy_set.parts[0].author == "Bar, Foo"
        assert legacy_set.parts[0].author_dates == "1980-"
        assert legacy_set.parts[0].description == "Fake description of book."
        assert legacy_set.parts[0].pub_date == "2000"
        assert len(legacy_set.parts[0].subjects) == 2
        assert (
            legacy_set.contents_note
            == 'Set consists of 10 copies of "Fake book 1", 10 copies of "Fake book 2".'
        )
        assert len(legacy_set.var_field_data) == 16
        assert legacy_set.legacy_barcodes == {
            "33333987654321": "Teacher Set SOC A Foo Bar Book Club 1-1",
            "33333123456789": "Teacher Set SOC A Foo Bar Book Club 1-2",
        }
        assert legacy_set.local_genre_term == []
        assert legacy_set.local_topic_term == []

    def test_legacy_set_single_copy(
        self, stub_platform_session_single_copy, caplog, mock_worldcat_response
    ):
        platform_manager = PlatformManager()
        legacy_set_data = LegacyTeacherSetData(
            bib_id="12345", platform_manager=platform_manager
        )
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert (
            legacy_set.contents_note
            == 'Set consists of 1 copy of "Fake book 1", 1 copy of "Fake book 2".'
        )
        assert legacy_set.legacy_barcodes == {
            "33333987654321": "Teacher Set SOC A Foo Bar Book Club 1-1",
            "33333123456789": "Teacher Set SOC A Foo Bar Book Club 1-2",
        }
