"""Frozen executable identity for BASELINE-004."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .models import ValidationError


BASELINE004_RELATIVE_DIRECTORY = Path(
    "baselines/BASELINE-004-learner-navigation-workspace"
)
BASELINE004_EXECUTABLE_HASHES = {
    "index.html": "2023e876c965f723e796f135460798b1c7538d05b693b979db3128934ec210e6",
    "workspace.css": "53a6c5593da5c5da7935698d6c8682b4f1f542f6d082d96e77c634cb0432d211",
    "workspace.js": "d9eff687be246fc0ac42506b71d55944bb26a10046be4f8ca38270cd4ee94d33",
    "workspace-manifest.json": "e1ed270a97bf182120f3dd74fda76d2c961516f013b686c110f5fd7ebc976344",
    "workspace-fixture.json": "c214158c546fcbed1184b22ab6ac52371c49e7801b1ffb548ed453984fa1fb69",
    "projection.css": "ecf9e962889be2e5d2b096118cb9f10f4669fffd3ee6197575c0f20c7029597d",
    "projection-extension.js": "05ea171074c69f85c64a817ae75741fb6396be3ea2554322df5baa09fed9cc42",
    "projection.json": "8f1d3beb0e9954040f59862c904a6d9d17574f048bdfcb1cc9059d5df3761232",
    "grammar.css": "7158525143670c4dbfa6294eca9ffc8d55587af00a478744616d87e90050484e",
    "learner-grammar.js": "bab6defc170c4e00cfafda4e8afee4d66690d33e3447d38b608543c616f8793b",
}


def repository_root() -> Path:
    return Path(__file__).parents[2]


def baseline004_directory() -> Path:
    """Return the canonical directory future experiments must reuse."""
    return repository_root() / BASELINE004_RELATIVE_DIRECTORY


def verify_baseline004(
    directory: Path | None = None,
    expected: Mapping[str, str] = BASELINE004_EXECUTABLE_HASHES,
) -> dict[str, str]:
    """Fail closed unless every frozen executable asset is byte-identical."""
    root = directory or baseline004_directory()
    actual = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in expected
    }
    if actual != dict(expected):
        raise ValidationError("BASELINE-004 executable identity mismatch")
    return actual
