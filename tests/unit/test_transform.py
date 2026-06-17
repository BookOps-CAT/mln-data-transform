from mln_data_transform.transform import PlatformManager, WorldcatManager


class TestPlatformManager:
    def test_get_platform_bib(self, mock_platform_session, caplog):
        platform_manager = PlatformManager()
        bib_data = platform_manager.get_platform_bib("12345")
        assert "id" in bib_data
        assert "lang" in bib_data
        assert "title" in bib_data
        assert "varFields" in bib_data
        assert "code" in bib_data["lang"]
        assert len(caplog.records) == 1
        assert caplog.records[0].msg == "Getting bib record from platform for 12345."

    def test_get_platform_bib_items(self, mock_platform_session, caplog):
        platform_manager = PlatformManager()
        bib_items_data = platform_manager.get_platform_bib_items("12345")
        assert len(bib_items_data) == 2
        assert "id" in bib_items_data[0]
        assert "callNumber" in bib_items_data[0]
        assert "barcode" in bib_items_data[0]
        assert len(caplog.records) == 2
        assert caplog.records[0].msg == "Getting items from platform for 12345."
        assert caplog.records[1].msg == "2 item record(s) found for bib 12345."


class TestWorldcatManager:
    def test_get_worldcat_data_for_part(self, mock_metadata_session, caplog):
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                "978123456897"
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

    def test_teacher_set_missing_data(self, mock_metadata_session_missing_data):
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                "978123456897"
            )
        assert worldcat_response.author_data is None
        assert worldcat_response.author_name is None
        assert worldcat_response.author_dates is None
        assert worldcat_response.description == ""
        assert worldcat_response.pub_date is None
        assert len(worldcat_response.subjects) == 0
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
