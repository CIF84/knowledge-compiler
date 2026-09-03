"""Command-line interface for offline text-to-KnowledgeModel compilation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .evaluation import default_domains_directory, run_live_evaluation
from .extractor import FixtureExtractor
from .models import ValidationError
from .openai_extractor import DEFAULT_MODEL, ExtractionError, OpenAILLMExtractor
from .pipeline import compile_knowledge_model


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="knowledge-compiler")
    subcommands = parser.add_subparsers(dest="command", required=True)
    translate = subcommands.add_parser("translate", help="compile a UTF-8 text file into KnowledgeModel JSON")
    translate.add_argument("source", type=Path)
    translate.add_argument("--output", "-o", required=True, type=Path)
    translate.add_argument("--extractor", choices=("fixture", "llm"), required=True)
    translate.add_argument("--fixture", type=Path, help="extraction JSON (required for fixture extraction)")
    translate.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model for LLM extraction")
    evaluate = subcommands.add_parser("evaluate", help="run the five-domain live LLM evaluation")
    evaluate.add_argument("--extractor", choices=("llm",), default="llm")
    evaluate.add_argument("--model", default=DEFAULT_MODEL)
    evaluate.add_argument("--fixtures-dir", type=Path, default=default_domains_directory())
    evaluate.add_argument("--output-dir", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "evaluate":
            if not os.environ.get("OPENAI_API_KEY"):
                raise ExtractionError("OPENAI_API_KEY is required for --extractor llm")
            report = run_live_evaluation(
                extractor_factory=lambda: OpenAILLMExtractor(model=args.model),
                fixtures_dir=args.fixtures_dir,
                output_dir=args.output_dir,
                provider="openai",
                model=args.model,
            )
            succeeded = sum(item["validation_success"] for item in report["results"])
            print(f"Wrote {args.output_dir / 'report.json'} ({succeeded}/{len(report['results'])} domains succeeded)")
            return 0 if succeeded == len(report["results"]) else 1

        text = args.source.read_text(encoding="utf-8")
        if args.extractor == "fixture":
            if args.fixture is None:
                raise ValidationError("--fixture is required for --extractor fixture")
            extractor = FixtureExtractor(args.fixture)
        else:
            extractor = OpenAILLMExtractor(model=args.model)
        model = compile_knowledge_model(
            text,
            extractor,
            source_metadata={"filename": args.source.name},
        )
        args.output.write_text(
            json.dumps(model.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, UnicodeError, ValidationError, ExtractionError, ValueError) as exc:
        print(f"knowledge-compiler: error: {exc}", file=sys.stderr)
        return 1
    print(
        f"Wrote {args.output} ({len(model.entities)} entities, "
        f"{len(model.relationships)} relationships, {len(model.claims)} claims)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
