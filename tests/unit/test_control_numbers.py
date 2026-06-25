from pathlib import Path

import pytest

from mln_data_transform.control_numbers import ControlNumberGenerator


@pytest.fixture
def mock_control_number_file(monkeypatch):
    def fake_read_text(*args, **kwargs) -> str:
        return '{"used_numbers": [1]}'

    def fake_write_text(*args, **kwargs) -> str:
        pass

    def fake_path_exists(*args, **kwargs) -> str:
        return True

    monkeypatch.setattr(Path, "exists", fake_path_exists)
    monkeypatch.setattr(Path, "read_text", fake_read_text)
    monkeypatch.setattr(Path, "write_text", fake_write_text)


class TestControlNumberGenerator:
    def test_control_number_generator(self, caplog, mock_control_number_file):
        generator = ControlNumberGenerator("foo.json")
        assert (
            caplog.records[0].msg
            == "Loading current control number data: {'used_numbers': [1]}"
        )
        assert caplog.records[1].msg == "Next control number is 2"
        assert list(generator.used_numbers) == [1]
        assert generator.next_number == 2

    def test_next_control_number(self, mock_control_number_file):
        generator = ControlNumberGenerator("foo.json")
        assert generator.next_number == 2
        assert list(generator.used_numbers) == [1]
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000002"
        assert list(generator.used_numbers) == [1, 2]
        assert generator.next_number == 3

    def test_next_control_number_no_file(self, caplog):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000001"
        assert caplog.records == []

    def test_save_state_write_to_file(self, caplog, mock_control_number_file):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000002"
        generator.save_state()
        assert list(generator.used_numbers) == [1, 2]
        assert generator.next_number == 3
