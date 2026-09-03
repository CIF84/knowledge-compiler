"""Command-line interface for offline text-to-KnowledgeModel compilation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extractor import FixtureExtractor
from .models import ValidationError
from .pipeline import compile_knowledge_model


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="knowledge-compiler")
    subcommands = parser.add_subparsers(dest="command", required=True)
    translate = subcommands.add_parser("translate", help="compile a UTF-8 text file into KnowledgeModel JSON")
    translate.add_argument("source", type=Path)
    translate.add_argument("--output", "-o", required=True, type=Path)
    translate.add_argument("--extractor", choices=("fixture",), required=True)
    translate.add_argument("--fixture", type=Path, help="extraction JSON (defaults to the bundled golden fixture)")
    return parser


def _default_fixture() -> Path:
    return Path(__file__).parents[2] / "tests" / "fixtures" / "electromagnetism_extraction.json"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        text = args.source.read_text(encoding="utf-8")
        fixture = args.fixture or _default_fixture()
        model = compile_knowledge_model(
            text,
            FixtureExtractor(fixture),
            source_metadata={"filename": args.source.name},
        )
        args.output.write_text(
            json.dumps(model.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, UnicodeError, ValidationError, ValueError) as exc:
        print(f"knowledge-compiler: error: {exc}", file=sys.stderr)
        return 1
    print(
        f"Wrote {args.output} ({len(model.entities)} entities, "
        f"{len(model.relationships)} relationships, {len(model.claims)} claims)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
