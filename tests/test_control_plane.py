from pathlib import Path

import pytest

from knowledge_compiler.control_plane import (
    ContractControl,
    parse_contract_control,
    validate_control_plane,
)
from knowledge_compiler.models import ValidationError


APPROVED_HEADER = """\
Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `CHATGPT_REVIEW`
Promotion: `NOT_AUTHORIZED`
"""


def _write_control_plane(root: Path, packet: str, metadata: str = APPROVED_HEADER) -> None:
    (root / "ops").mkdir()
    (root / "ops" / "OPS-999-test.md").write_text(
        f"# test packet\n\n{APPROVED_HEADER}", encoding="utf-8"
    )
    (root / "STATUS.md").write_text(
        "# status\n\n## Current approved work packet\n\n"
        f"```text\n{packet}\n```\n\n{metadata}\n",
        encoding="utf-8",
    )


def test_approved_active_pointer_resolves_with_matching_authority(tmp_path):
    _write_control_plane(tmp_path, "ops/OPS-999-test.md")
    state = validate_control_plane(tmp_path)
    assert state.packet == "ops/OPS-999-test.md"
    assert state.control == ContractControl(
        status="APPROVED_FOR_IMPLEMENTATION",
        authority="OFFLINE_ONLY",
        human_gate="CHATGPT_REVIEW",
        promotion="NOT_AUTHORIZED",
    )


def test_none_is_a_valid_explicit_inactive_pointer(tmp_path):
    _write_control_plane(
        tmp_path,
        "NONE",
        "Status: `NONE`\nAuthority: `NONE`\nHuman gate: `NONE`\n"
        "Promotion: `NOT_AUTHORIZED`",
    )
    assert validate_control_plane(tmp_path).packet is None


def test_stale_pointer_fails_visibly(tmp_path):
    _write_control_plane(tmp_path, "ops/OPS-998-missing.md")
    with pytest.raises(ValidationError, match="does not exist"):
        validate_control_plane(tmp_path)


def test_status_and_contract_control_mismatch_fails(tmp_path):
    _write_control_plane(
        tmp_path,
        "ops/OPS-999-test.md",
        APPROVED_HEADER.replace("OFFLINE_ONLY", "LIVE_CALLS_EXPLICITLY_BOUNDED"),
    )
    with pytest.raises(ValidationError, match="differs"):
        validate_control_plane(tmp_path)


def test_historical_contract_without_compact_header_remains_valid(tmp_path):
    _write_control_plane(tmp_path, "ops/OPS-999-test.md")
    (tmp_path / "ops" / "OPS-999-test.md").write_text(
        "# historical packet\n\n## Status\n\nReady for implementation.\n",
        encoding="utf-8",
    )
    assert validate_control_plane(tmp_path).packet == "ops/OPS-999-test.md"


def test_partial_new_control_header_fails_visibly(tmp_path):
    _write_control_plane(tmp_path, "ops/OPS-999-test.md")
    (tmp_path / "ops" / "OPS-999-test.md").write_text(
        "# malformed packet\n\nStatus: `APPROVED_FOR_IMPLEMENTATION`\n"
        "Authority: `OFFLINE_ONLY`\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="partial control header"):
        validate_control_plane(tmp_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("Status", "READY_MAYBE", "unknown contract status"),
        ("Authority", "DO_WHATEVER", "unknown or unbounded contract authority"),
        ("Human gate", "SOMEONE", "unknown contract human gate"),
        ("Promotion", "MAYBE", "unknown contract promotion boundary"),
    ],
)
def test_malformed_control_headers_fail_visibly(field, value, message):
    text = APPROVED_HEADER.replace(f"{field}: `" + {
        "Status": "APPROVED_FOR_IMPLEMENTATION",
        "Authority": "OFFLINE_ONLY",
        "Human gate": "CHATGPT_REVIEW",
        "Promotion": "NOT_AUTHORIZED",
    }[field] + "`", f"{field}: `{value}`")
    with pytest.raises(ValidationError, match=message):
        parse_contract_control(text)


def test_nonapproved_packet_cannot_be_active(tmp_path):
    _write_control_plane(tmp_path, "ops/OPS-999-test.md")
    packet = tmp_path / "ops" / "OPS-999-test.md"
    packet.write_text(
        packet.read_text(encoding="utf-8").replace(
            "APPROVED_FOR_IMPLEMENTATION", "IMPLEMENTED_AWAITING_REVIEW"
        ),
        encoding="utf-8",
    )
    (tmp_path / "STATUS.md").write_text(
        (tmp_path / "STATUS.md").read_text(encoding="utf-8").replace(
            "APPROVED_FOR_IMPLEMENTATION", "IMPLEMENTED_AWAITING_REVIEW"
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="not executable"):
        validate_control_plane(tmp_path)


def test_repository_status_has_an_explicit_valid_pointer_state():
    repository = Path(__file__).parents[1]
    assert validate_control_plane(repository).packet is None


def test_ops003_records_a_well_formed_awaiting_review_control_header():
    repository = Path(__file__).parents[1]
    control = parse_contract_control(
        (repository / "ops/OPS-003-repository-control-plane-and-low-attention-handoff.md")
        .read_text(encoding="utf-8")
    )
    assert control == ContractControl(
        status="IMPLEMENTED_AWAITING_REVIEW",
        authority="OFFLINE_ONLY",
        human_gate="CHATGPT_REVIEW",
        promotion="NOT_AUTHORIZED",
    )
