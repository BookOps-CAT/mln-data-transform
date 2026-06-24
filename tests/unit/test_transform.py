import pytest

from mln_data_transform.transform import (
    BriefBibResponse,
    FullWorldCatResponse,
    PlatformManager,
    WorldcatManager,
)


class TestWorldcatResponses:
    @pytest.mark.parametrize(
        "level, sort_key",
        [
            ({"levelOfCataloging": "M"}, (1, 9)),
            ({"levelOfCataloging": " "}, (0, 0)),
            ({"levelOfCataloging": "7"}, (1, 7)),
            ({"levelOfCataloging": "3"}, (1, 3)),
        ],
    )
    def test_brief_bib_response(self, level, sort_key):
        record = {"oclcNumber": "ocn123456789", "catalogingInfo": level}
        brief_bib_response = BriefBibResponse(record)
        assert brief_bib_response.sort_key() == sort_key
        assert brief_bib_response.cat_level == level["levelOfCataloging"]
        assert brief_bib_response.oclc_number == "ocn123456789"

    def test_brief_bib_response_sorted(self):
        records = [
            {
                "oclcNumber": "ocn111111111",
                "catalogingInfo": {"levelOfCataloging": "M"},
            },
            {
                "oclcNumber": "ocn222222222",
                "catalogingInfo": {"levelOfCataloging": "5"},
            },
            {
                "oclcNumber": "ocn333333333",
                "catalogingInfo": {"levelOfCataloging": "7"},
            },
            {
                "oclcNumber": "ocn444444444",
                "catalogingInfo": {"levelOfCataloging": "I"},
            },
            {
                "oclcNumber": "ocn555555555",
                "catalogingInfo": {"levelOfCataloging": " "},
            },
            {
                "oclcNumber": "ocn666666666",
                "catalogingInfo": {"levelOfCataloging": "3"},
            },
            {"oclcNumber": "ocn777777777"},
        ]
        brief_bib_responses = [BriefBibResponse(i) for i in records]
        sorted_responses = sorted(brief_bib_responses, key=BriefBibResponse.sort_key)
        assert [i.oclc_number for i in sorted_responses] == [
            "ocn444444444",
            "ocn555555555",
            "ocn666666666",
            "ocn222222222",
            "ocn333333333",
            "ocn111111111",
            "ocn777777777",
        ]


class TestFullWorldCatResponse:
    def test_full_bib_response(self, stub_bib):
        full_bib_response = FullWorldCatResponse(
            isbn="9781234567897", wc_response=stub_bib
        )
        assert full_bib_response.author_data.format_field() == "Bar, Foo 1980-"
        assert full_bib_response.author_name == "Bar, Foo"
        assert full_bib_response.author_dates == "1980-"
        assert full_bib_response.description == "Fake description of book."
        assert full_bib_response.pub_date == "2000"
        assert len(full_bib_response.subjects) == 2
        assert full_bib_response.title == "Fake book 1"
        assert list(full_bib_response.to_dict().keys()) == [
            "author_name",
            "author_dates",
            "description",
            "isbn",
            "pub_date",
            "subjects",
            "title",
        ]

    def test_full_bib_response_missing_data(self, stub_bib):
        stub_bib.remove_fields("100", "264", "520", "651", "655")
        full_bib_response = FullWorldCatResponse(
            isbn="9781234567897", wc_response=stub_bib
        )
        assert full_bib_response.author_data is None
        assert full_bib_response.author_name is None
        assert full_bib_response.author_dates is None
        assert full_bib_response.description == ""
        assert full_bib_response.pub_date is None
        assert len(full_bib_response.subjects) == 0
        assert full_bib_response.title == "Fake book 1"
        assert list(full_bib_response.to_dict().keys()) == [
            "author_name",
            "author_dates",
            "description",
            "isbn",
            "pub_date",
            "subjects",
            "title",
        ]


class TestPlatformManager:
    def test_get_platform_bib(self, mock_session_managers, caplog):
        caplog.set_level("DEBUG")
        platform_manager = PlatformManager()
        bib_data = platform_manager.get_platform_bib("12345")
        assert "id" in bib_data
        assert "lang" in bib_data
        assert "title" in bib_data
        assert "varFields" in bib_data
        assert "code" in bib_data["lang"]
        assert len(caplog.records) == 1
        assert caplog.records[0].msg == "(12345) Getting bib record from platform."

    def test_get_platform_bib_items(self, mock_session_managers, caplog):
        caplog.set_level("DEBUG")
        platform_manager = PlatformManager()
        bib_items_data = platform_manager.get_platform_bib_items("12345")
        assert len(bib_items_data) == 2
        assert "id" in bib_items_data[0]
        assert "callNumber" in bib_items_data[0]
        assert "barcode" in bib_items_data[0]
        assert len(caplog.records) == 1
        assert caplog.records[0].msg == "(12345) Getting item records from platform."


class TestWorldcatManager:
    def test_get_worldcat_data_for_part(self, mock_session_managers, caplog):
        caplog.set_level("DEBUG")
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                "9781234567897"
            )
        assert worldcat_response.author_data.format_field() == "Bar, Foo 1980-"
        assert worldcat_response.author_name == "Bar, Foo"
        assert worldcat_response.author_dates == "1980-"
        assert worldcat_response.description == "Fake description of book."
        assert worldcat_response.pub_date == "2000"
        assert len(worldcat_response.subjects) == 2
        assert worldcat_response.title == "Fake book 1"
        assert list(worldcat_response.to_dict().keys()) == [
            "author_name",
            "author_dates",
            "description",
            "isbn",
            "pub_date",
            "subjects",
            "title",
        ]
        assert [i.msg for i in caplog.records] == [
            "ISBN 9781234567897: retrieving brief bib record.",
            "ISBN 9781234567897: retrieving full bib record (OCLC number: ocn123456789).",
        ]
