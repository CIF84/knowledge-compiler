"""Minimal fail-closed validation for the repository work-packet pointer."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import ValidationError


CONTRACT_STATUSES = frozenset({
    "DRAFT",
    "APPROVED_FOR_IMPLEMENTATION",
    "IMPLEMENTED_AWAITING_REVIEW",
    "COMPLETED",
    "REJECTED",
})
EXECUTABLE_STATUSES = frozenset({"APPROVED_FOR_IMPLEMENTATION"})
AUTHORITIES = frozenset({"OFFLINE_ONLY", "LIVE_CALLS_EXPLICITLY_BOUNDED"})
HUMAN_GATES = frozenset({
    "NONE",
    "OWNER_REVIEW",
    "CHATGPT_REVIEW",
    "OWNER_AND_CHATGPT_REVIEW",
})
NO_ACTIVE_PACKET = "NONE"


@dataclass(frozen=True, slots=True)
class ContractControl:
    status: str
    authority: str
    human_gate: str
    promotion: str


@dataclass(frozen=True, slots=True)
class ControlPlaneState:
    packet: str | None
    control: ContractControl | None


def _field(text: str, name: str) -> str:
    match = re.search(
        rf"^{re.escape(name)}:\s*`?([^`\n]+?)`?\s*$", text, flags=re.MULTILINE
    )
    if not match:
        raise ValidationError(f"missing control-plane field: {name}")
    return match.group(1).strip()


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValidationError(f"missing STATUS.md section: {heading}")
    return match.group(1)


def parse_contract_control(text: str) -> ContractControl:
    control = ContractControl(
        status=_field(text, "Status"),
        authority=_field(text, "Authority"),
        human_gate=_field(text, "Human gate"),
        promotion=_field(text, "Promotion"),
    )
    return _validate_contract_control(control)


def _validate_contract_control(control: ContractControl) -> ContractControl:
    if control.status not in CONTRACT_STATUSES:
        raise ValidationError(f"unknown contract status: {control.status}")
    if control.authority not in AUTHORITIES and not re.fullmatch(
        r"BOUNDED_[A-Z0-9_]+", control.authority
    ):
        raise ValidationError(f"unknown or unbounded contract authority: {control.authority}")
    if control.human_gate not in HUMAN_GATES:
        raise ValidationError(f"unknown contract human gate: {control.human_gate}")
    if control.promotion != "NOT_AUTHORIZED" and not re.fullmatch(
        r"AUTHORIZED_IF_[A-Z0-9_]+", control.promotion
    ):
        raise ValidationError(f"unknown contract promotion boundary: {control.promotion}")
    return control


def validate_control_plane(repository: Path) -> ControlPlaneState:
    status_path = repository / "STATUS.md"
    if not status_path.is_file():
        raise ValidationError("root STATUS.md is missing")
    section = _section(status_path.read_text(encoding="utf-8"), "Current approved work packet")
    packet_match = re.search(r"```(?:text)?\s*\n([^\n]+)\n```", section)
    if not packet_match:
        raise ValidationError("STATUS.md current packet must be one explicit fenced value")
    packet = packet_match.group(1).strip()
    status_control = ContractControl(
        status=_field(section, "Status"),
        authority=_field(section, "Authority"),
        human_gate=_field(section, "Human gate"),
        promotion=_field(section, "Promotion"),
    )
    if packet == NO_ACTIVE_PACKET:
        if status_control != ContractControl(
            status=NO_ACTIVE_PACKET,
            authority=NO_ACTIVE_PACKET,
            human_gate=NO_ACTIVE_PACKET,
            promotion="NOT_AUTHORIZED",
        ):
            raise ValidationError("inactive STATUS.md pointer has active control metadata")
        return ControlPlaneState(packet=None, control=None)

    status_control = _validate_contract_control(status_control)

    relative = Path(packet)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.suffix != ".md"
        or relative.parts[0] not in {"specs", "ops"}
    ):
        raise ValidationError(f"invalid active work-packet path: {packet}")
    contract_path = repository / relative
    if not contract_path.is_file():
        raise ValidationError(f"active work packet does not exist: {packet}")
    contract_text = contract_path.read_text(encoding="utf-8")
    extended_fields = tuple(
        re.search(rf"^{re.escape(name)}:", contract_text, flags=re.MULTILINE)
        is not None
        for name in ("Authority", "Human gate", "Promotion")
    )
    if any(extended_fields):
        if not all(extended_fields):
            raise ValidationError("active contract has a partial control header")
        contract_control = parse_contract_control(contract_text)
        if status_control != contract_control:
            raise ValidationError("STATUS.md control metadata differs from active contract")
    if status_control.status not in EXECUTABLE_STATUSES:
        raise ValidationError(
            f"active work packet is not executable: {status_control.status}"
        )
    return ControlPlaneState(packet=packet, control=status_control)
