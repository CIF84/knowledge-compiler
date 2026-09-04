"""Command-line interface for offline text-to-KnowledgeModel compilation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .evaluation import default_domains_directory, run_live_evaluation
from .assertion_evaluation import (
    finalize_assertion_first_evaluation,
    run_assertion_first_evaluation,
)
from .extractor import FixtureExtractor
from .layout_evaluation import default_spec005_representations_directory, prepare_layout_evaluation
from .models import KnowledgeModel, ValidationError
from .openai_extractor import DEFAULT_MODEL, ExtractionError, OpenAILLMExtractor
from .pipeline import compile_knowledge_model
from .proposition_evaluation import run_proposition_evaluation
from .quantum_learning_evaluation import run_quantum_learning_evaluation
from .representation_builder import RepresentationBuilder
from .representation_evaluation import (
    default_presentation_metadata_path,
    default_spec004_structures_directory,
    prepare_representation_evaluation,
)
from .resolution_evaluation import (
    default_parent_models_directory,
    default_parent_representations_directory,
    default_reference_directory,
    run_resolution_evaluation,
)
from .resolution_strategy_evaluation import run_resolution_strategy_evaluation
from .semantic_navigation import (
    default_spec006_representations_directory,
    prepare_semantic_navigation_evaluation,
)
from .staged_semantic_evaluation import (
    finalize_staged_semantic_evaluation,
    run_staged_semantic_evaluation,
)
from .structures import DetectedStructureSet
from .structure_detection import StructureDetector
from .structure_evaluation import (
    default_spec003_models_directory,
    default_structure_expectations_path,
    evaluate_structure_models,
)


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
    detect = subcommands.add_parser("detect-structures", help="detect structures in KnowledgeModel JSON")
    detect.add_argument("model", type=Path)
    detect.add_argument("--output", "-o", required=True, type=Path)
    structure_evaluation = subcommands.add_parser(
        "evaluate-structures", help="evaluate structure detection from the five SPEC-003 models"
    )
    structure_evaluation.add_argument("--models-dir", type=Path, default=default_spec003_models_directory())
    structure_evaluation.add_argument(
        "--expectations", type=Path, default=default_structure_expectations_path()
    )
    structure_evaluation.add_argument("--output-dir", required=True, type=Path)
    represent = subcommands.add_parser(
        "represent", help="build presentation JSON from a KnowledgeModel and detected structures"
    )
    represent.add_argument("model", type=Path)
    represent.add_argument("structures", type=Path)
    represent.add_argument("--metadata", type=Path)
    represent.add_argument("--output", "-o", required=True, type=Path)
    prepare = subcommands.add_parser(
        "prepare-representations", help="build the offline five-domain representation review"
    )
    prepare.add_argument("--models-dir", type=Path, default=default_spec003_models_directory())
    prepare.add_argument("--structures-dir", type=Path, default=default_spec004_structures_directory())
    prepare.add_argument("--metadata", type=Path, default=default_presentation_metadata_path())
    prepare.add_argument("--output-dir", required=True, type=Path)
    layout = subcommands.add_parser(
        "prepare-layout-interaction",
        help="build the offline SPEC-006 structure-aware viewer from fixed SPEC-005 artifacts",
    )
    layout.add_argument("--input-dir", type=Path, default=default_spec005_representations_directory())
    layout.add_argument("--models-dir", type=Path, default=default_spec003_models_directory())
    layout.add_argument("--structures-dir", type=Path, default=default_spec004_structures_directory())
    layout.add_argument("--output-dir", required=True, type=Path)
    navigation = subcommands.add_parser(
        "prepare-semantic-navigation",
        help="build the offline SPEC-007 progressive-disclosure comparison",
    )
    navigation.add_argument(
        "--input-dir", type=Path, default=default_spec006_representations_directory()
    )
    navigation.add_argument("--output-dir", required=True, type=Path)
    resolution = subcommands.add_parser(
        "evaluate-multi-resolution",
        help="run the live SPEC-008 child-resolution compilation spike",
    )
    resolution.add_argument("--models-dir", type=Path, default=default_parent_models_directory())
    resolution.add_argument(
        "--representations-dir", type=Path, default=default_parent_representations_directory()
    )
    resolution.add_argument("--reference-dir", type=Path, default=default_reference_directory())
    resolution.add_argument("--model", default=DEFAULT_MODEL)
    resolution.add_argument("--output-dir", required=True, type=Path)
    strategy_evaluation = subcommands.add_parser(
        "evaluate-resolution-strategies",
        help="run the live SPEC-009 Generic versus type-aware resolution matrix",
    )
    strategy_evaluation.add_argument("--model", default=DEFAULT_MODEL)
    strategy_evaluation.add_argument("--output-dir", required=True, type=Path)
    proposition_evaluation = subcommands.add_parser(
        "evaluate-propositions",
        help="build the deterministic SPEC-010 proposition regression review",
    )
    proposition_evaluation.add_argument("--output-dir", required=True, type=Path)
    quantum_evaluation = subcommands.add_parser(
        "evaluate-quantum-learning-slice",
        help="run the live SPEC-011 real-source quantum learning slice",
    )
    quantum_evaluation.add_argument("source", type=Path)
    quantum_evaluation.add_argument("--source-metadata", required=True, type=Path)
    quantum_evaluation.add_argument("--model", default=DEFAULT_MODEL)
    quantum_evaluation.add_argument("--output-dir", required=True, type=Path)
    quantum_evaluation.add_argument(
        "--prior-run-history", action="append", default=[], type=Path,
        help="preserve earlier failed attempts in the aggregate run history",
    )
    staged_evaluation = subcommands.add_parser(
        "evaluate-staged-semantic-compilation",
        help="run the live SPEC-012 symbol-discovery and semantic-linking benchmark",
    )
    staged_evaluation.add_argument("source", type=Path)
    staged_evaluation.add_argument("--source-metadata", required=True, type=Path)
    staged_evaluation.add_argument("--control-proposal", required=True, type=Path)
    staged_evaluation.add_argument("--model", default=DEFAULT_MODEL)
    staged_evaluation.add_argument("--output-dir", required=True, type=Path)
    staged_finalize = subcommands.add_parser(
        "finalize-staged-semantic-compilation",
        help="validate independent semantic review and finalize SPEC-012 comparison",
    )
    staged_finalize.add_argument("output_dir", type=Path)
    assertion_evaluation = subcommands.add_parser(
        "evaluate-assertion-first-compilation",
        help="run the live SPEC-013 assertion extraction and canonicalization benchmark",
    )
    assertion_evaluation.add_argument("source", type=Path)
    assertion_evaluation.add_argument("--source-metadata", required=True, type=Path)
    assertion_evaluation.add_argument("--symbol-table", required=True, type=Path)
    assertion_evaluation.add_argument("--model", default=DEFAULT_MODEL)
    assertion_evaluation.add_argument("--output-dir", required=True, type=Path)
    assertion_finalize = subcommands.add_parser(
        "finalize-assertion-first-compilation",
        help="validate independent reviews and finalize the SPEC-013 comparison",
    )
    assertion_finalize.add_argument("output_dir", type=Path)
    view = subcommands.add_parser("view-representations", help="serve a prepared representation review locally")
    view.add_argument("directory", type=Path)
    view.add_argument("--host", default="127.0.0.1")
    view.add_argument("--port", type=int, default=8000)
    view.add_argument("--open-browser", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "finalize-assertion-first-compilation":
            report = finalize_assertion_first_evaluation(args.output_dir)
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"(verdict {report['verdict']})"
            )
            return 0

        if args.command == "evaluate-assertion-first-compilation":
            if not os.environ.get("OPENAI_API_KEY"):
                raise ExtractionError("OPENAI_API_KEY is required for the live SPEC-013 evaluation")
            report = run_assertion_first_evaluation(
                source_path=args.source,
                source_metadata_path=args.source_metadata,
                symbol_table_path=args.symbol_table,
                output_dir=args.output_dir,
                model=args.model,
            )
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"({report['assertion_grounding']['assertion_count']} grounded assertions; "
                "semantic review pending)"
            )
            return 0

        if args.command == "finalize-staged-semantic-compilation":
            report = finalize_staged_semantic_evaluation(args.output_dir)
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"(verdict {report['verdict']})"
            )
            return 0

        if args.command == "evaluate-staged-semantic-compilation":
            if not os.environ.get("OPENAI_API_KEY"):
                raise ExtractionError("OPENAI_API_KEY is required for the live SPEC-012 evaluation")
            report = run_staged_semantic_evaluation(
                source_path=args.source,
                source_metadata_path=args.source_metadata,
                control_proposal_path=args.control_proposal,
                output_dir=args.output_dir,
                model=args.model,
            )
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"({report['counts']['entities']} frozen symbols; semantic review pending)"
            )
            return 0

        if args.command == "evaluate-quantum-learning-slice":
            if not os.environ.get("OPENAI_API_KEY"):
                raise ExtractionError("OPENAI_API_KEY is required for the live SPEC-011 evaluation")
            report = run_quantum_learning_evaluation(
                source_path=args.source,
                source_metadata_path=args.source_metadata,
                output_dir=args.output_dir,
                model=args.model,
                prior_run_histories=tuple(args.prior_run_history),
            )
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"(parent {report['parent']['counts']['entities']} entities, "
                f"child outcome {report['semantic_zoom']['outcome']})"
            )
            return 0

        if args.command == "evaluate-propositions":
            report = run_proposition_evaluation(output_dir=args.output_dir)
            status = "semantic invariants pass" if report["all_machine_invariants_pass"] else "integrity failure"
            print(f"Wrote {args.output_dir / 'report.json'} (2/2 regressions, {status})")
            return 0 if report["all_machine_invariants_pass"] else 1

        if args.command == "evaluate-resolution-strategies":
            report = run_resolution_strategy_evaluation(
                output_dir=args.output_dir,
                model=args.model,
            )
            attempts = report["generation_attempt_count"]
            provider_failures = report["outcome_counts"]["PROVIDER_FAILURE"]
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"({attempts}/6 paired generation attempts preserved, "
                f"{provider_failures} provider failures)"
            )
            return 0 if attempts == 6 and provider_failures == 0 else 1

        if args.command == "evaluate-multi-resolution":
            report = run_resolution_evaluation(
                models_dir=args.models_dir,
                representations_dir=args.representations_dir,
                reference_dir=args.reference_dir,
                output_dir=args.output_dir,
                model=args.model,
            )
            successful = report["successful_child_count"]
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"({successful}/2 original-source child resolutions succeeded)"
            )
            return 0 if successful == 2 else 1

        if args.command == "prepare-semantic-navigation":
            report = prepare_semantic_navigation_evaluation(
                input_dir=args.input_dir,
                output_dir=args.output_dir,
            )
            complete = all((
                report["all_modes_available"],
                report["all_return_targets_valid"],
                report["all_parent_selections_restorable"],
                report["all_child_selection_identities_complete"],
                report["all_canonical_directions_preserved"],
                report["all_provenance_truthful"],
                report["all_layouts_deterministic"],
                report["all_contextual_identities_present"],
                report["baseline_artifacts_byte_preserved"],
            ))
            status = "semantic-navigation integrity complete" if complete else "integrity failure"
            print(f"Wrote {args.output_dir / 'report.json'} (2/2 fixtures, {status})")
            return 0 if complete else 1

        if args.command == "prepare-layout-interaction":
            report = prepare_layout_evaluation(
                input_dir=args.input_dir,
                models_dir=args.models_dir,
                structures_dir=args.structures_dir,
                output_dir=args.output_dir,
            )
            complete = all((
                report["all_semantic_content_unchanged"],
                report["all_selection_identity_complete"],
                report["all_canonical_directions_preserved"],
                report["all_provenance_preserved"],
                report["all_layouts_have_no_node_overlap"],
            ))
            status = "layout and interaction integrity complete" if complete else "integrity failure"
            print(f"Wrote {args.output_dir / 'report.json'} (5/5 domains, {status})")
            return 0 if complete else 1

        if args.command == "represent":
            model = KnowledgeModel.from_dict(json.loads(args.model.read_text(encoding="utf-8")))
            structures = DetectedStructureSet.from_dict(
                json.loads(args.structures.read_text(encoding="utf-8"))
            )
            metadata = json.loads(args.metadata.read_text(encoding="utf-8")) if args.metadata else None
            representation = RepresentationBuilder().build(
                model, structures, presentation_metadata=metadata
            )
            args.output.write_text(
                json.dumps(representation.to_dict(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"Wrote {args.output} ({len(representation.representations)} representations)")
            return 0

        if args.command == "prepare-representations":
            report = prepare_representation_evaluation(
                models_dir=args.models_dir,
                structures_dir=args.structures_dir,
                output_dir=args.output_dir,
                metadata_path=args.metadata,
            )
            complete = report["all_references_valid"] and report["all_provenance_complete"]
            status = "provenance complete" if complete else "integrity failure"
            print(
                f"Wrote {args.output_dir / 'report.json'} "
                f"({len(report['results'])}/5 domains, {status})"
            )
            return 0 if complete else 1

        if args.command == "view-representations":
            from .viewer import serve_viewer
            serve_viewer(args.directory, args.host, args.port, open_browser=args.open_browser)
            return 0

        if args.command == "detect-structures":
            model = KnowledgeModel.from_dict(json.loads(args.model.read_text(encoding="utf-8")))
            structures = StructureDetector().detect(model)
            args.output.write_text(
                json.dumps(structures.to_dict(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"Wrote {args.output} ({len(structures.structures)} structures)")
            return 0

        if args.command == "evaluate-structures":
            report = evaluate_structure_models(
                models_dir=args.models_dir,
                output_dir=args.output_dir,
                expectations_path=args.expectations,
            )
            met = sum(item["all_golden_expectations_met"] for item in report["results"])
            print(f"Wrote {args.output_dir / 'report.json'} ({met}/{len(report['results'])} domains met expectations)")
            return 0 if met == len(report["results"]) else 1

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
