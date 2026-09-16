from mln_data_transform.platform import PlatformManager


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
