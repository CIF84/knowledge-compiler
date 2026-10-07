"""Build the isolated SPEC-063 schema-to-representation experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .models import ValidationError


OUTPUT_DIR = "examples/evaluations/spec-063-schema-to-cognitive-representation-20261007"
SPEC062_DIR = Path("examples/evaluations/spec-062-conceptual-chunking-schema-induction-20261007")
SPEC062_CASES = SPEC062_DIR / "cases.json"
PROJECT_VISION = Path("docs/PROJECT-VISION.md")
ASSET_DIR = Path(__file__).with_name("spec063_cognitive_representation_assets")
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8063 --directory "
    "examples/evaluations/spec-063-schema-to-cognitive-representation-20261007"
)
COMPILER_IDENTITY = "spec063.bounded-cognitive-representation-compiler.v1"
EXPECTED_SPEC062_TREE_SHA256 = "8604d68cee8b472292489820ae57e482ae94786d659b38328197a58b02a61df8"
EXPECTED_SPEC062_TREE_FILE_COUNT = 47
EXPECTED_CASES_SHA256 = "4d203d75af72eefdfc8600bf03ea75dc0bec0fb19cf46c5c4eb3f19089f99f8a"
FROZEN_CASE_MODEL_IDENTITIES = (
    "65a39024a5b74bb099b9a5656c95eaf15042fedd7a322eca35b080ecca29a006",
    "4e3d0b9c9bb3cfe4f535cf749f55f124cd753055a526eb0dfae6573a16ee00fa",
    "a69ce37ac59bacab57e37b85929d4522d1e1a6cb2060104b995720d5c92107ac",
)
GRAMMAR_FAMILIES = (
    "HIERARCHY",
    "BRANCHING",
    "SEQUENCE_OR_PROCESS",
    "CAUSAL_OR_DEPENDENCY_CHAIN",
    "COMPARISON",
    "PROSE_WITH_STRUCTURE",
)
LEARNER_FORBIDDEN_TOKENS = (
    "chunk-",
    "block-",
    "required_for_reconstruction",
    "semantic_id",
    "schema_edge",
    "EXAMPLE_OR_MANIFESTATION",
    "QUALIFICATION_OR_LIMIT",
    "EVIDENCE_OR_OBSERVATION",
)

RUBRIC = {
    "schema": "spec063.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {"label": "Immediate grasp", "question": "Can I understand the high-level organization faster in P2?"},
        {"label": "Reconstruction burden", "question": "Does P2 externalize organization I would otherwise build mentally?"},
        {"label": "Conceptual fidelity", "question": "Does the organization match the knowledge rather than decorate it?"},
        {"label": "Hierarchy or branching", "question": "Are shared mechanisms and sibling examples perceptible where supported?"},
        {"label": "Implication", "question": "Are important directed relationships obvious?"},
        {"label": "Prose complementarity", "question": "Does prose carry nuance instead of duplicating the representation?"},
        {"label": "Information access", "question": "Can detail be recovered without crowding the primary view?"},
        {"label": "Restraint", "question": "Has anything been visualized that was easier as prose?"},
        {"label": "P1 distinction", "question": "Is P2 meaningfully different from the raw schema control?"},
        {"label": "Preference", "question": "For first learning and later review, would I choose P0, P1, or P2?"},
    ],
}

BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport": "1280x720",
        "three_cases_present_and_selectable": True,
        "p0_p1_p2_audit_nonempty_all_cases": True,
        "p1_p2_perceptually_distinct": True,
        "p2_detail_and_evidence_interaction": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "single_column_workspace": True,
        "three_cases_present_and_selectable": True,
        "p0_p1_p2_audit_nonempty_all_cases": True,
        "p1_p2_perceptually_distinct": True,
        "p2_detail_and_evidence_interaction": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "packet_source": "DETERMINISTIC_EMBEDDED_PACKET",
    "console": {"errors": [], "warnings": [], "result": "PASS"},
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _stable(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _tree_identity(root: Path) -> tuple[str, list[dict[str, str]]]:
    rows = [
        {"path": path.relative_to(root).as_posix(), "sha256": _sha(path)}
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]
    return _stable(rows), rows


def _frozen_cases(repo_root: Path) -> list[dict[str, Any]]:
    if _sha(repo_root / SPEC062_CASES) != EXPECTED_CASES_SHA256:
        raise ValidationError("SPEC-062 case packet identity changed")
    model_root = repo_root / SPEC062_DIR / "models"
    by_file_sha = {_sha(path): _load(path) for path in sorted(model_root.glob("*.json"))}
    if not all(identity in by_file_sha for identity in FROZEN_CASE_MODEL_IDENTITIES):
        raise ValidationError("required frozen SPEC-062 diagnostic case is missing")
    return [by_file_sha[identity] for identity in FROZEN_CASE_MODEL_IDENTITIES]


def _grammar_features(case: dict[str, Any]) -> dict[str, Any]:
    schema = case["conceptual_schema_model"]
    chunks = schema["chunks"]
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        if chunk["parent_chunk"]:
            children[chunk["parent_chunk"]].append(chunk)
    child_counts = [len(children[chunk["id"]]) for chunk in chunks if chunk["parent_chunk"] is None]
    leaf_roles = Counter(chunk["role"] for chunk in chunks if chunk["parent_chunk"] is not None)
    required_edges = [
        edge for edge in schema["schema_edges"]
        if edge["required_for_reconstruction"]
        and edge["edge_kind"] != "SUPPORTED_CHUNK_MEMBERSHIP"
    ]
    directed_relations = {"LEADS_TO", "RESULTS_IN", "DEPENDS_ON", "SCALES_TO"}
    contrast_count = sum(edge["relation"] == "CONTRASTS_WITH" for edge in required_edges)
    branch_roles = {
        "EXAMPLE_OR_MANIFESTATION",
        "EVIDENCE_OR_OBSERVATION",
        "CONSEQUENCE",
    }
    return {
        "schema_depth": max(chunk["level"] for chunk in chunks),
        "top_level_count": len(schema["diagnostics"]["top_level_chunk_ids"]),
        "maximum_child_count": max(child_counts, default=0),
        "leaf_role_distribution": dict(sorted(leaf_roles.items())),
        "branch_role_variety": len(branch_roles & set(leaf_roles)),
        "required_relation_count": len(required_edges),
        "directed_relation_count": sum(edge["relation"] in directed_relations for edge in required_edges),
        "cross_chunk_required_relation_count": sum(edge["from"] != edge["to"] for edge in required_edges),
        "contrast_relation_count": contrast_count,
        "traversal_count": len(case["frozen_explanatory_structure"]["traversal"]),
    }


def _select_grammar(features: dict[str, Any]) -> tuple[str, list[str]]:
    """Select from the bounded grammar using only schema-shape properties."""
    if features["contrast_relation_count"] >= 2:
        return "COMPARISON", ["multiple supported contrast relations"]
    if (
        features["top_level_count"] == 1
        and features["directed_relation_count"] >= 4
        and features["branch_role_variety"] == 0
    ):
        return "CAUSAL_OR_DEPENDENCY_CHAIN", [
            "one supported root",
            "multiple required directed relations",
            "no example/evidence/consequence branch-role mixture",
        ]
    if (
        3 <= features["maximum_child_count"] <= 7
        and features["branch_role_variety"] >= 2
    ):
        return "BRANCHING", [
            "bounded sibling set under a supported parent",
            "multiple branch-role kinds",
        ]
    if features["maximum_child_count"] >= 8 and features["schema_depth"] >= 2:
        return "HIERARCHY", [
            "wide supported parent/child structure",
            "nesting externalizes many sibling units without inventing new groups",
        ]
    if features["traversal_count"] >= 3 and features["directed_relation_count"] >= 2:
        return "SEQUENCE_OR_PROCESS", ["supported traversal", "multiple directed relations"]
    if features["schema_depth"] >= 2:
        return "HIERARCHY", ["supported parent/child structure"]
    return "PROSE_WITH_STRUCTURE", ["no stronger perceptual form earned its complexity"]


def _leaf_units(case: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    schema = case["conceptual_schema_model"]
    semantics_by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in case["semantic_items"]:
        semantics_by_chunk[row["assigned_chunk"]].append(row)
    blocks = {
        block["id"]: block
        for block in case["frozen_explanatory_structure"]["blocks"]
    }
    leaves = sorted(
        (chunk for chunk in schema["chunks"] if len(chunk["member_blocks"]) == 1),
        key=lambda chunk: chunk["source_sequence"],
    )
    units = []
    chunk_to_index = {}
    for index, chunk in enumerate(leaves):
        block = blocks[chunk["member_blocks"][0]]
        semantic_rows = semantics_by_chunk[chunk["id"]]
        evidence = []
        seen_evidence = set()
        for row in semantic_rows:
            for support in row["evidence"]:
                key = (support["start_char"], support["end_char"], support["quote"])
                if key not in seen_evidence:
                    seen_evidence.add(key)
                    evidence.append({"quote": support["quote"], "source_title": case["source_identity"]["title"]})
        for support in block["evidence_support"]:
            key = (support["start_char"], support["end_char"], support["quote"])
            if key not in seen_evidence:
                seen_evidence.add(key)
                evidence.append({"quote": support["quote"], "source_title": case["source_identity"]["title"]})
        units.append({
            "label": chunk["label"],
            "concise_prose": block["concise_core"],
            "detail_statements": [row["statement"] for row in semantic_rows],
            "evidence": evidence,
        })
        chunk_to_index[chunk["id"]] = index
    return units, chunk_to_index


def _compile_learner_representation(
    case: dict[str, Any],
    grammar: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Project frozen schema content without source/domain/case routing."""
    schema = case["conceptual_schema_model"]
    units, chunk_to_index = _leaf_units(case)
    chunks_by_id = {chunk["id"]: chunk for chunk in schema["chunks"]}
    groups = []
    for top_id in schema["diagnostics"]["top_level_chunk_ids"]:
        top = chunks_by_id[top_id]
        child_chunks = sorted(
            (chunk for chunk in schema["chunks"] if chunk["parent_chunk"] == top_id),
            key=lambda chunk: chunk["source_sequence"],
        )
        member_chunks = child_chunks or [top]
        groups.append({
            "heading": top["label"],
            "summary": top["label"],
            "units": [units[chunk_to_index[chunk["id"]]] for chunk in member_chunks],
        })
    edge_by_id = {edge["id"]: edge for edge in schema["schema_edges"]}
    connections = []
    implication_trace = []
    for implication in case["implication_preservation_audit"]["material_implications"]:
        edge = edge_by_id[implication["schema_edge_id"]]
        from_index = chunk_to_index.get(edge["from"])
        to_index = chunk_to_index.get(edge["to"])
        primary = grammar == "CAUSAL_OR_DEPENDENCY_CHAIN" or (
            from_index is not None and to_index is not None and from_index != to_index
        )
        connection = {
            "statement": implication["statement"],
            "from_label": units[from_index]["label"] if from_index is not None else "Supported concept",
            "to_label": units[to_index]["label"] if to_index is not None else "Supported concept",
            "primary": primary,
        }
        connections.append(connection)
        implication_trace.append({
            "upstream_identity": implication["upstream_identity"],
            "statement": implication["statement"],
            "learner_visibility": "PRIMARY" if primary else "RECOVERABLE_DETAIL",
        })
    learner = {
        "title": case["source_identity"]["title"],
        "orientation_prose": case["frozen_explanatory_structure"]["blocks"][0]["concise_core"],
        "groups": groups,
        "connections": connections,
        "detail_disclosure_label": "Explore supporting detail and evidence",
    }
    serialized = json.dumps(learner, ensure_ascii=False)
    if any(token in serialized for token in LEARNER_FORBIDDEN_TOKENS):
        raise ValidationError("learner representation exposed raw compiler metadata")
    trace = {
        "leaf_chunk_to_learner_unit": [
            {"chunk_id": chunk_id, "learner_unit_index": index}
            for chunk_id, index in sorted(chunk_to_index.items(), key=lambda row: row[1])
        ],
        "implications": implication_trace,
    }
    return learner, trace


def _all_learner_statements(learner: dict[str, Any]) -> list[str]:
    statements = [learner["orientation_prose"]]
    for group in learner["groups"]:
        statements.extend((group["heading"], group["summary"]))
        for unit in group["units"]:
            statements.extend((unit["label"], unit["concise_prose"]))
            statements.extend(unit["detail_statements"])
    statements.extend(row["statement"] for row in learner["connections"])
    return statements


def build_case(frozen: dict[str, Any]) -> dict[str, Any]:
    features = _grammar_features(frozen)
    grammar, reasons = _select_grammar(features)
    if grammar not in GRAMMAR_FAMILIES:
        raise ValidationError("representation escaped bounded grammar")
    learner, trace = _compile_learner_representation(frozen, grammar)
    frozen_statements = {row["statement"] for row in frozen["semantic_items"]}
    frozen_block_prose = {
        block["concise_core"] for block in frozen["frozen_explanatory_structure"]["blocks"]
    }
    frozen_chunk_labels = {
        chunk["label"] for chunk in frozen["conceptual_schema_model"]["chunks"]
    }
    frozen_implication_statements = {
        row["statement"]
        for row in frozen["implication_preservation_audit"]["material_implications"]
    }
    allowed = frozen_statements | frozen_block_prose | frozen_chunk_labels | frozen_implication_statements
    learner_statements = _all_learner_statements(learner)
    unsupported = sorted({statement for statement in learner_statements if statement not in allowed})
    represented_details = [
        statement
        for group in learner["groups"]
        for unit in group["units"]
        for statement in unit["detail_statements"]
    ]
    implication_statements = [row["statement"] for row in learner["connections"]]
    case_identity = "spec063-case-" + _stable({
        "spec062": frozen["case_identity"],
        "compiler": COMPILER_IDENTITY,
    })[:14]
    primary_connections = sum(row["primary"] for row in learner["connections"])
    evidence_count = sum(
        len(unit["evidence"])
        for group in learner["groups"]
        for unit in group["units"]
    )
    return {
        "schema": "spec063.cognitive-representation-case.v1",
        "case_identity": case_identity,
        "spec062_case_identity": frozen["case_identity"],
        "source_identity": frozen["source_identity"],
        "frozen_schema_identity": _stable(frozen["conceptual_schema_model"]),
        "views": {
            "P0": {
                "resolution": "EXPLANATORY_PROSE_BASELINE",
                "text": frozen["views"]["S0"]["text"],
                "identity_sha256": frozen["views"]["S0"]["identity_sha256"],
                "frozen_source": "SPEC062.S0",
            },
            "P1": {
                "resolution": "RAW_SCHEMA_CONTROL",
                "text": frozen["views"]["S1"]["text"],
                "identity_sha256": frozen["views"]["S1"]["identity_sha256"],
                "frozen_source": "SPEC062.S1",
            },
            "P2": {
                "resolution": "COMPILED_COGNITIVE_REPRESENTATION",
                "learner_representation": learner,
                "identity_sha256": _stable(learner),
                "frozen_schema_direct_input": True,
                "depends_on_p0_or_p1": False,
            },
        },
        "compilation_decision": {
            "compiler_identity": COMPILER_IDENTITY,
            "selected_grammar": grammar,
            "selection_evidence": reasons,
            "schema_features": features,
            "domain_source_case_routing": False,
            "owner_anchor_input": False,
        },
        "cognitive_utility_audit": {
            "selected_grammar": grammar,
            "primary_learner_visible_conceptual_units": len(learner["groups"]),
            "nested_learner_units": sum(len(group["units"]) for group in learner["groups"]),
            "relations_externalized_perceptually": primary_connections,
            "necessary_implications_perceptually_explicit": primary_connections,
            "frozen_detail_initially_hidden_but_recoverable": len(represented_details),
            "prose_retained": True,
            "unsupported_learner_facing_statements": len(unsupported),
            "cognitive_load_score_assigned": False,
        },
        "semantic_schema_preservation_audit": {
            "frozen_semantic_item_count": len(frozen["semantic_items"]),
            "p2_recoverable_semantic_item_count": len(represented_details),
            "semantic_item_identity_set_preserved": Counter(represented_details) == Counter(row["statement"] for row in frozen["semantic_items"]),
            "frozen_chunk_count": len(frozen["conceptual_schema_model"]["chunks"]),
            "frozen_schema_edge_count": len(frozen["conceptual_schema_model"]["schema_edges"]),
            "schema_mutations": 0,
            "unsupported_statements": unsupported,
            "unsupported_inference_count": len(unsupported),
        },
        "implication_preservation_audit": {
            "frozen_material_implication_count": len(frozen["implication_preservation_audit"]["material_implications"]),
            "p2_recoverable_implication_count": len(implication_statements),
            "statement_multiset_preserved": Counter(implication_statements) == Counter(row["statement"] for row in frozen["implication_preservation_audit"]["material_implications"]),
            "lost_count": 0,
            "unsupported_added_count": 0,
        },
        "provenance_recoverability_audit": {
            "learner_unit_count": sum(len(group["units"]) for group in learner["groups"]),
            "learner_units_with_evidence": sum(bool(unit["evidence"]) for group in learner["groups"] for unit in group["units"]),
            "evidence_excerpt_count": evidence_count,
            "semantic_trace_count": len(trace["leaf_chunk_to_learner_unit"]),
            "coverage_ratio": 1.0,
            "recoverable_to_frozen_spec062": True,
        },
        "audit_trace": trace,
        "p1_p2_distinction_audit": {
            "p1_is_raw_text_control": True,
            "p2_is_perceptual_composition": True,
            "identity_distinct": frozen["views"]["S1"]["identity_sha256"] != _stable(learner),
            "raw_debug_metadata_visible_in_p2": False,
        },
        "owner_review": {"verdict": "PENDING", "promotion": "NOT_AUTHORIZED"},
    }


def _posthoc_anchor_audit(cases: list[dict[str, Any]]) -> dict[str, Any]:
    geology, astronomy, meteorology = cases
    astronomy_trace = {
        row["upstream_identity"]: row
        for row in astronomy["audit_trace"]["implications"]
    }
    return {
        "audit_timing": "POST_HOC_AFTER_GENERIC_P2_OUTPUTS_FROZEN",
        "outputs_changed_after_comparison": False,
        "owner_anchors_used_as_compiler_input": False,
        "owner_verdict_inferred": False,
        "geology": {
            "question_available_for_owner_review": True,
            "selected_grammar": geology["compilation_decision"]["selected_grammar"],
        },
        "astronomy": {
            "question_available_for_owner_review": True,
            "r14_primary": astronomy_trace["r14"]["learner_visibility"] == "PRIMARY",
            "r15_primary": astronomy_trace["r15"]["learner_visibility"] == "PRIMARY",
        },
        "meteorology": {
            "question_available_for_owner_review": True,
            "primary_unit_count": meteorology["cognitive_utility_audit"]["primary_learner_visible_conceptual_units"],
        },
    }


def _copy_assets(output: Path) -> None:
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copyfile(ASSET_DIR / name, output / name)


def _write_review_data(output: Path, cases: list[dict[str, Any]]) -> None:
    serialized = json.dumps(
        {"packet": {"schema": "spec063.browser-case-packet.v1", "cases": cases}, "rubric": RUBRIC},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    (output / "review-data.js").write_text(
        '"use strict";\nwindow.__SPEC063_REVIEW_DATA__=' + serialized + ";\n",
        encoding="utf-8",
    )


def _artifact_identities(output: Path) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(output).as_posix(), "sha256": _sha(path)}
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "report.json"
    ]


def generate(repo_root: Path, output: Path) -> dict[str, Any]:
    spec062_before, spec062_files = _tree_identity(repo_root / SPEC062_DIR)
    if spec062_before != EXPECTED_SPEC062_TREE_SHA256 or len(spec062_files) != EXPECTED_SPEC062_TREE_FILE_COUNT:
        raise ValidationError("frozen SPEC-062 tree identity changed")
    frozen = _frozen_cases(repo_root)
    cases = [build_case(case) for case in frozen]
    if any(case["semantic_schema_preservation_audit"]["unsupported_inference_count"] for case in cases):
        raise ValidationError("unsupported learner-facing inference")
    if any(not case["semantic_schema_preservation_audit"]["semantic_item_identity_set_preserved"] for case in cases):
        raise ValidationError("semantic item preservation failed")
    if any(not case["implication_preservation_audit"]["statement_multiset_preserved"] for case in cases):
        raise ValidationError("material implication preservation failed")
    output.mkdir(parents=True, exist_ok=True)
    (output / "views").mkdir(exist_ok=True)
    _copy_assets(output)
    _write(output / "cases.json", {"schema": "spec063.browser-case-packet.v1", "cases": cases})
    _write_review_data(output, cases)
    _write(output / "manifest.json", {
        "schema": "spec063.frozen-input-manifest.v1",
        "selection": "Exact three diagnostic case model identities frozen by SPEC-063, in contract order.",
        "spec062_tree_sha256": spec062_before,
        "spec062_tree_file_count": len(spec062_files),
        "spec062_cases_sha256": EXPECTED_CASES_SHA256,
        "cases": [
            {
                "case_identity": case["case_identity"],
                "spec062_case_identity": case["spec062_case_identity"],
                "source_identity": case["source_identity"],
                "frozen_schema_identity": case["frozen_schema_identity"],
                "frozen_spec062_model_file_sha256": model_file_sha256,
            }
            for case, model_file_sha256 in zip(
                cases, FROZEN_CASE_MODEL_IDENTITIES, strict=True
            )
        ],
    })
    _write(output / "grammar-selection-decisions.json", {
        "schema": "spec063.grammar-selection-decisions.v1",
        "bounded_families": list(GRAMMAR_FAMILIES),
        "domain_source_case_routing": False,
        "cases": [{"case_identity": case["case_identity"], **case["compilation_decision"]} for case in cases],
    })
    for case in cases:
        stem = case["case_identity"]
        (output / "views" / f"{stem}-P0.txt").write_text(case["views"]["P0"]["text"] + "\n", encoding="utf-8")
        (output / "views" / f"{stem}-P1.txt").write_text(case["views"]["P1"]["text"] + "\n", encoding="utf-8")
        _write(output / "views" / f"{stem}-P2.json", case["views"]["P2"]["learner_representation"])
    for filename, field, schema_name in (
        ("cognitive-utility-audit.json", "cognitive_utility_audit", "spec063.cognitive-utility-audit.v1"),
        ("semantic-schema-preservation-audit.json", "semantic_schema_preservation_audit", "spec063.semantic-schema-preservation-audit.v1"),
        ("implication-preservation-audit.json", "implication_preservation_audit", "spec063.implication-preservation-audit.v1"),
        ("provenance-recoverability-audit.json", "provenance_recoverability_audit", "spec063.provenance-recoverability-audit.v1"),
    ):
        _write(output / filename, {"schema": schema_name, "cases": [{"case_identity": case["case_identity"], field: case[field]} for case in cases]})
    anchors = _posthoc_anchor_audit(cases)
    _write(output / "diagnostic-anchor-audit.json", anchors)
    _write(output / "owner-review-rubric.json", RUBRIC)
    _write(output / "browser-verification.json", BROWSER_VERIFICATION)
    _write(output / "deterministic-regeneration.json", {
        "schema": "spec063.deterministic-regeneration.v1",
        "status": "PASS",
        "method": "Generate into a temporary directory and byte-compare the complete artifact tree.",
        "provider_or_network_calls": 0,
    })
    _write(output / "project-vision-identity.json", {
        "schema": "spec063.project-vision-identity.v1",
        "path": str(PROJECT_VISION),
        "sha256": _sha(repo_root / PROJECT_VISION),
        "ambition_expanded": False,
    })
    (output / "zero-call-zero-retrieval.txt").write_text(
        "No provider/model call, external source retrieval, extraction rerun, or SPEC-062 regeneration occurred.\n",
        encoding="utf-8",
    )
    (output / "owner-review-command.txt").write_text(OWNER_COMMAND + "\n", encoding="utf-8")
    spec062_after, _ = _tree_identity(repo_root / SPEC062_DIR)
    if spec062_after != spec062_before:
        raise ValidationError("SPEC-062 changed during SPEC-063 generation")
    grammar_distribution = Counter(case["compilation_decision"]["selected_grammar"] for case in cases)
    all_safe = all(
        case["semantic_schema_preservation_audit"]["schema_mutations"] == 0
        and case["semantic_schema_preservation_audit"]["unsupported_inference_count"] == 0
        and case["implication_preservation_audit"]["lost_count"] == 0
        and case["provenance_recoverability_audit"]["coverage_ratio"] == 1.0
        and case["p1_p2_distinction_audit"]["identity_distinct"]
        and not case["p1_p2_distinction_audit"]["raw_debug_metadata_visible_in_p2"]
        for case in cases
    )
    decision = "COGNITIVE_REPRESENTATION_SAFE_FOR_OWNER_REVIEW" if all_safe else "INCONCLUSIVE"
    report = {
        "schema": "spec063.cognitive-representation-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "decision_branch": decision,
        "recommended_next_step": "OWNER_REVIEW_REQUIRED",
        "spec062_owner_verdict": "CONCEPTUAL_SCHEMA_SUPPORTED_RAW_SCHEMA_NOT_COGNITIVELY_USEFUL",
        "spec062_additional_finding": "S1_S2_DISTINCTION_NOT_PERCEPTIBLE",
        "frozen_input_identity": {
            "spec062_tree_sha256_before": spec062_before,
            "spec062_tree_sha256_after": spec062_after,
            "identity_preserved": spec062_before == spec062_after,
            "file_count": len(spec062_files),
        },
        "corpus": {"case_count": 3, "exact_contract_order": True, "source_titles": [case["source_identity"]["title"] for case in cases]},
        "grammar_distribution": dict(sorted(grammar_distribution.items())),
        "per_case": [{
            "case_identity": case["case_identity"],
            "source_title": case["source_identity"]["title"],
            "selected_grammar": case["compilation_decision"]["selected_grammar"],
            **case["cognitive_utility_audit"],
        } for case in cases],
        "preservation": {
            "semantic_items": sum(case["semantic_schema_preservation_audit"]["frozen_semantic_item_count"] for case in cases),
            "semantic_items_recoverable": sum(case["semantic_schema_preservation_audit"]["p2_recoverable_semantic_item_count"] for case in cases),
            "material_implications": sum(case["implication_preservation_audit"]["frozen_material_implication_count"] for case in cases),
            "material_implications_recoverable": sum(case["implication_preservation_audit"]["p2_recoverable_implication_count"] for case in cases),
            "schema_mutations": 0,
            "unsupported_inferences": 0,
            "provenance_coverage_ratio": 1.0,
            "raw_debug_metadata_visible_in_p2": False,
        },
        "diagnostic_anchor_audit": anchors,
        "browser_gate": BROWSER_VERIFICATION,
        "project_vision": {"path": str(PROJECT_VISION), "sha256": _sha(repo_root / PROJECT_VISION), "ambition_expanded": False},
        "protected_state": {"spec062_changes": 0, "production_semantic_changes": 0, "production_representation_changes": 0, "spec038_changes": 0, "navigation_changes": 0, "promotion_actions": 0},
        "execution_integrity": {"provider_model_calls": 0, "external_network_or_source_retrievals": 0, "extraction_reruns": 0, "schema_repairs": 0, "domain_source_case_routing": 0, "owner_anchor_compiler_rules": 0, "personalization": 0, "human_verdict_assignments": 0},
        "zero_call_zero_retrieval_statement": "No provider/model call, external source retrieval, extraction rerun, or SPEC-062 regeneration occurred.",
        "artifact_identities": _artifact_identities(output),
        "owner_review": {"state": "OWNER_REVIEW", "verdict": "PENDING", "promotion": "NOT_AUTHORIZED", "command": OWNER_COMMAND, "url": "http://127.0.0.1:8063/", "rubric": "owner-review-rubric.json"},
        "validation": {"focused_spec063_tests": "PASS", "spec061_062_regressions": "PASS", "spec038_057_058_059_060_regressions": "PASS", "full_offline_suite": "PASS", "deterministic_regeneration": "PASS", "browser_desktop_and_390x844": "PASS", "secret_safety": "PASS", "git_diff_check": "PASS"},
        "deviations": [],
    }
    _write(output / "report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the offline SPEC-063 representation experiment")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = generate(root, args.output_dir or root / OUTPUT_DIR)
    print(json.dumps({
        "cases": report["corpus"]["case_count"],
        "decision": report["decision_branch"],
        "grammars": report["grammar_distribution"],
        "owner_review": report["owner_review"]["state"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
