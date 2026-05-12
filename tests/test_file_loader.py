from codeguardian.tools.file_loader import read_optional_text_file, read_text_file


def test_read_text_file_reads_utf8_text(tmp_path):
    sample = tmp_path / "assignment.txt"
    sample.write_text("实现 sumEven", encoding="utf-8")

    assert read_text_file(sample) == "实现 sumEven"


def test_read_optional_text_file_returns_empty_for_none():
    assert read_optional_text_file(None) == ""
