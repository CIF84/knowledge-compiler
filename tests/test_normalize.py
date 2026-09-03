from knowledge_compiler.normalize import normalize_document, normalize_text


def test_normalize_line_endings_and_outer_whitespace() -> None:
    assert normalize_text(" \r\nFirst\r\n\r\nSecond\r ") == "First\n\nSecond"


def test_document_id_is_content_stable() -> None:
    assert normalize_document("x\r\n").id == normalize_document(" x\n").id
