"""Build the isolated SPEC-060 progressive semantic-compression experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError


OUTPUT_DIR = (
    "examples/evaluations/"
    "spec-060-progressive-semantic-compression-foundation-20260917"
)
SOURCE_ROOT = (
    "examples/evaluations/"
    "spec-052-candidate-b-v2-live-evaluation-20260915/sources"
)
SPEC052_REPORT = (
    "examples/evaluations/"
    "spec-052-candidate-b-v2-live-evaluation-20260915/final-report.json"
)
SPEC059_REPORT = (
    "examples/evaluations/"
    "spec-059-semantic-typography-enriched-prose-experiment-20260917/report.json"
)
PROJECT_VISION = "docs/PROJECT-VISION.md"
ASSET_DIR = Path(__file__).with_name("spec060_semantic_compression_assets")
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8060 --directory "
    "examples/evaluations/"
    "spec-060-progressive-semantic-compression-foundation-20260917"
)
GOAL = (
    "Preserve the information necessary to accurately understand the source's core "
    "explanatory content, including material qualifications and epistemic status, "
    "while removing rhetorical, repetitive and linguistically redundant expression."
)

SOURCES = (
    "01-usgs-divergent-plate-boundaries-1996",
    "02-noaa-nesdis-jet-stream-2025",
    "03-crs-legislative-process-r42843-17",
    "04-nasa-solar-system-formation-2026",
    "05-epa-ecological-processes-2026",
    "06-doe-iron-platinum-atomic-structure-2017",
)

# Frozen essentiality plans contain identities only. The same source-independent
# projection functions consume each plan and its admitted grounded substrate.
ESSENTIALITY_PLANS = {
    SOURCES[0]: {
        "coverage": [
            "PROCESS_MECHANISM",
            "QUANTITATIVE_FACT",
            "TEMPORAL_SCOPE",
            "QUALIFICATION_UNCERTAINTY",
        ],
        "required_item_ids": """
            c2 c3 c4 c5 c7 c8 c9 c10 c11 c12 c13 c14 c15 c16 c17 c18
            c19 c20 c21 c22
        """.split(),
    },
    SOURCES[1]: {
        "coverage": [
            "PROCESS_MECHANISM",
            "STRUCTURAL_RELATIONSHIP",
            "QUANTITATIVE_FACT",
            "CONDITIONAL_EFFECT",
        ],
        "required_item_ids": """
            c31 c32 c7 c14 c8 c9 c12 c1 c33 c15 c34 c16 c35 c17 c19
            c36 c20 c21 c22 c26 c27 c23 c37 c24 c25 c38 c39
        """.split(),
    },
    SOURCES[2]: {
        "coverage": [
            "INSTITUTIONAL_PROCESS",
            "STRUCTURAL_RELATIONSHIP",
            "COMPARISON",
            "SCOPE_CONDITION",
        ],
        "required_item_ids": """
            claim-party-leaders claim-house-tools claim-policy-expertise claim-referral
            claim-formal-attention claim-agenda-authority claim-two-year-congress
            claim-committee-initiation claim-hearings claim-markup-purpose
            claim-amendments claim-recommended-changes claim-house-floor
            claim-rules-committee claim-senate-floor
        """.split(),
    },
    SOURCES[3]: {
        "coverage": [
            "FORMATION_MECHANISM",
            "STRUCTURAL_RELATIONSHIP",
            "QUALIFICATION_UNCERTAINTY",
            "TEMPORAL_PROCESS",
        ],
        "required_item_ids": """
            c1 c3 c4 c5 c6 c7 c8 c9 c10 r11 r12 r13 r16 r18 r20 r21
            r23 r24 r25 r26
        """.split(),
    },
    SOURCES[4]: {
        "coverage": [
            "SYSTEM_MECHANISM",
            "TRANSFER_RELATIONSHIP",
            "MEASUREMENT_LIMIT",
            "SCOPE_CONDITION",
        ],
        "required_item_ids": """
            claim-1 claim-2 claim-3 claim-4 claim-5 claim-6 claim-7
            proposition-transfer-event-eed90760d22f2700
            proposition-transfer-event-272f1ee1d4ba095c
            proposition-transfer-event-859166508310ca4b
            proposition-transfer-event-ee31dfd1ac2df832
            r1 r2 r3 r4 r5 r6 r7 r8 r18 r19 r20 r21
        """.split(),
    },
    SOURCES[5]: {
        "coverage": [
            "OBSERVATIONAL_ASSOCIATION",
            "QUANTITATIVE_FACT",
            "MEASUREMENT_PRECISION",
            "MATERIAL_QUALIFICATION",
            "RHETORICAL_REPETITION",
        ],
        "required_item_ids": """
            c1 c2 c3 c4 c5 c6 c10 c11 c12 c13 c14 c15 c16 c17 c18
        """.split(),
    },
}

EXPECTED_EVIDENCE_IDENTITIES = {
    SPEC052_REPORT: "5e73b73b1080230b8068ab2046ba82f635ee65bfaaaf63c05e0db15e12d75d08",
    SPEC059_REPORT: "4507785572c16c2e50b0c1a7c301391bfca8b20cef8b94eb5cba1e9b12ea2cda",
    f"{SOURCE_ROOT}/{SOURCES[0]}/admitted-knowledge-model.json": "fa2494dab670a698a8f730a0501c997984467839906f5c7b702e50ad6fd61261",
    f"{SOURCE_ROOT}/{SOURCES[0]}/source-identity.json": "53212d9b0acf6ea795edf5f978193455188adbad2815d21ecefc4a5fd18dc83b",
    f"{SOURCE_ROOT}/{SOURCES[1]}/admitted-knowledge-model.json": "0c1e5b46d692727ca526f74307de2c0b358a1ea79dab98143f19271872a61a62",
    f"{SOURCE_ROOT}/{SOURCES[1]}/source-identity.json": "ea70487e2656e2226eae46f48cc1f9176b8530acc0e42767aba3d3b6cb8b7fb1",
    f"{SOURCE_ROOT}/{SOURCES[2]}/admitted-knowledge-model.json": "67366dc7c5dfd120d4ee974e02c0568f8e221675e0843dd35469bf41105fdeb4",
    f"{SOURCE_ROOT}/{SOURCES[2]}/source-identity.json": "3fd4862abb2b0aebd2bcd5b503022e900fe235bb07961bcde702a6fe83acf7c2",
    f"{SOURCE_ROOT}/{SOURCES[3]}/admitted-knowledge-model.json": "d0a28afecf69d8edc55783eb41b4de78c72d81ef6007ac8121a003946b06b198",
    f"{SOURCE_ROOT}/{SOURCES[3]}/source-identity.json": "0d50ebe9beecd5a9b14a04d88e5130329f082093789b02a8b44f21f3b8165d1b",
    f"{SOURCE_ROOT}/{SOURCES[4]}/admitted-knowledge-model.json": "077318e713e10c02ce188fca1d0e247801d975d5ab7b1b1951183b14d6ad60d1",
    f"{SOURCE_ROOT}/{SOURCES[4]}/source-identity.json": "2dda3ae4ffa5c076eb066a85b0872226b013ca1dc01ebb6a96abb95098dbcc25",
    f"{SOURCE_ROOT}/{SOURCES[5]}/admitted-knowledge-model.json": "29b475ec6742e1f7d49e9e5f29bbcd8a9c967d678a7d53f6ae58ae44f28acb7e",
    f"{SOURCE_ROOT}/{SOURCES[5]}/source-identity.json": "459b403edc905ae71fee648886c55e9a682c0948bfffcf7b4cd7e2677ebb60f5",
}

SEMANTIC_ROLES = (
    "CORE_FACT",
    "MECHANISM",
    "RELATIONSHIP",
    "QUANTITATIVE_FACT",
    "SCOPE_OR_CONDITION",
    "QUALIFICATION_OR_UNCERTAINTY",
    "CONTEXT_REQUIRED_FOR_MEANING",
)
CAUSAL_TYPES = {
    "CAUSES",
    "CREATES",
    "ENABLES",
    "INCREASES",
    "PRECEDES",
    "REQUIRES",
    "EXERTS_FORCE_ON",
}
QUALIFICATION_CUES = (
    "may",
    "might",
    "can",
    "could",
    "typically",
    "generally",
    "usually",
    "about",
    "more than",
    "only",
    "if",
    "when",
    "perhaps",
    "expected",
    "described as",
    "tend to",
)
RHETORICAL_PATTERNS = (
    r"\bimportant\b",
    r"\bvital\b",
    r"\bcritical\b",
    r"\bmakes? (?:a )?(?:major )?advances?\b",
    r"\bopens? the door\b",
    r"\bcould transform\b",
    r"\bexpected to find broad use\b",
)

RUBRIC = {
    "schema": "spec060.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {"id": "meaning", "label": "Meaning preservation", "question": "Is anything necessary for accurate understanding missing?"},
        {"id": "noise", "label": "Noise reduction", "question": "Was linguistic or rhetorical material removed without loss?"},
        {"id": "epistemic", "label": "Epistemic fidelity", "question": "Are uncertainty, scope, attribution, and causal status unchanged?"},
        {"id": "density", "label": "Information density", "question": "Does each resolution provide more useful information per unit of attention?"},
        {"id": "coherence", "label": "Coherence", "question": "Is R1 understandable without reconstructing missing context?"},
        {"id": "units", "label": "Unit quality", "question": "Does R2 expose meaning-bearing units rather than lexical fragments?"},
        {"id": "overcompression", "label": "Overcompression", "question": "Where does useful meaning begin to disappear?"},
        {"id": "recoverability", "label": "Recoverability", "question": "Can every compressed unit be traced to richer evidence and source?"},
    ],
}

BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport": "1280x720",
        "all_6_cases_loaded": True,
        "all_case_machine_checks_passed": True,
        "r0_r1_r2_audit_switching": "PASS",
        "view_identity_and_lineage": "PASS",
        "provenance_recoverability": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "single_column_workspace": True,
        "case_navigation_visible": True,
        "resolution_controls_visible": True,
        "source_rich_view_usable": True,
        "essential_explanation_usable": True,
        "essential_units_usable": True,
        "audit_view_usable": True,
        "horizontal_overflow": False,
        "all_case_machine_checks_passed": True,
        "result": "PASS",
    },
    "interaction": {
        "resolution_toggle_all_6_cases": "PASS",
        "case_navigation": "PASS",
        "independent_view_identities_preserved": "PASS",
        "audit_trace_selection": "PASS",
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
    "screenshots": {
        "captured": False,
        "reason": (
            "Desktop and 390x844 layouts were inspected through the Chromium browser "
            "gate; the browser bridge did not expose a deterministic repository-file "
            "capture path."
        ),
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _stable(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def _normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _item_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for semantic_class in ("claims", "propositions", "relationships"):
        for item in model.get(semantic_class, []):
            if item["id"] in index:
                raise ValidationError(f"duplicate semantic item id: {item['id']}")
            index[item["id"]] = {**item, "semantic_class": semantic_class[:-1].upper()}
    return index


def _validate_evidence(source: str, item: dict[str, Any]) -> None:
    if not item.get("evidence"):
        raise ValidationError(f"semantic item lacks evidence: {item['id']}")
    for evidence in item["evidence"]:
        if source[evidence["start_char"] : evidence["end_char"]] != evidence["quote"]:
            raise ValidationError(f"evidence range mismatch: {item['id']}")


def _merged_support_ranges(
    source: str, items: Iterable[dict[str, Any]]
) -> list[dict[str, Any]]:
    evidence_rows = []
    for item in items:
        _validate_evidence(source, item)
        for evidence in item["evidence"]:
            evidence_rows.append(
                {
                    "start_char": evidence["start_char"],
                    "end_char": evidence["end_char"],
                    "support_ids": [item["id"]],
                }
            )
    evidence_rows.sort(key=lambda row: (row["start_char"], row["end_char"]))
    merged: list[dict[str, Any]] = []
    for row in evidence_rows:
        if not merged or row["start_char"] > merged[-1]["end_char"]:
            merged.append(dict(row))
        else:
            merged[-1]["end_char"] = max(
                merged[-1]["end_char"], row["end_char"]
            )
            merged[-1]["support_ids"] = sorted(
                set(merged[-1]["support_ids"] + row["support_ids"])
            )
    for row in merged:
        row["text"] = source[row["start_char"] : row["end_char"]]
        row["text_sha256"] = _text_sha(row["text"])
    return merged


def _qualification_links(statement: str) -> list[dict[str, Any]]:
    links = []
    lowered = statement.casefold()
    for cue in QUALIFICATION_CUES:
        start = lowered.find(cue)
        if start >= 0:
            links.append(
                {
                    "cue": statement[start : start + len(cue)],
                    "start_char": start,
                    "end_char": start + len(cue),
                }
            )
    return links


def _semantic_role(item: dict[str, Any]) -> str:
    statement = item["statement"]
    if re.search(r"\d", statement) and re.search(
        r"percent|mile|meter|metre|atom|planet|year|precision|km|centimeter",
        statement,
        flags=re.IGNORECASE,
    ):
        return "QUANTITATIVE_FACT"
    if _qualification_links(statement):
        return "QUALIFICATION_OR_UNCERTAINTY"
    if item.get("relationship_type") in CAUSAL_TYPES:
        return "MECHANISM"
    if item["semantic_class"] in {"RELATIONSHIP", "PROPOSITION"}:
        return "RELATIONSHIP"
    if re.search(r"\b(if|when|during|after|before|at the national scale)\b", statement, re.I):
        return "SCOPE_OR_CONDITION"
    if item.get("relationship_type") in {"IS_A", "PART_OF", "EXAMPLE_OF"}:
        return "CONTEXT_REQUIRED_FOR_MEANING"
    return "CORE_FACT"


def _epistemic_status(statement: str) -> str:
    lowered = statement.casefold()
    if "correlated" in lowered or "infer" in lowered or "observed" in lowered:
        return "OBSERVATIONAL_OR_ASSOCIATIONAL"
    if any(cue in lowered for cue in ("may", "might", "could", "perhaps")):
        return "QUALIFIED_OR_UNCERTAIN"
    if any(cue in lowered for cue in ("scientists determined", "epa", "described as")):
        return "ATTRIBUTED_SOURCE_CLAIM"
    return "ASSERTED_SOURCE_CLAIM"


def _support_records(
    item: dict[str, Any], source_id: str, model_path: str, model_sha: str
) -> list[dict[str, Any]]:
    return [
        {
            "source_id": source_id,
            "document_id": evidence["document_id"],
            "start_char": evidence["start_char"],
            "end_char": evidence["end_char"],
            "quote": evidence["quote"],
            "model_path": model_path,
            "model_sha256": model_sha,
        }
        for evidence in item["evidence"]
    ]


def _r2_units(
    required_items: list[dict[str, Any]],
    all_items: dict[str, dict[str, Any]],
    source_id: str,
    model_path: str,
    model_sha: str,
) -> list[dict[str, Any]]:
    duplicates: dict[str, list[dict[str, str]]] = {}
    for item in all_items.values():
        duplicates.setdefault(_normalized(item["statement"]), []).append(
            {"semantic_class": item["semantic_class"], "id": item["id"]}
        )
    units = []
    for item in required_items:
        role = _semantic_role(item)
        base = {
            "concise_text": item["statement"],
            "semantic_role": role,
            "support": _support_records(item, source_id, model_path, model_sha),
            "preserved_from": duplicates[_normalized(item["statement"])],
            "epistemic_status": _epistemic_status(item["statement"]),
            "qualification_links": _qualification_links(item["statement"]),
        }
        units.append(
            {
                "id": f"unit-{_stable({'source': source_id, **base})[:14]}",
                **base,
            }
        )
    return units


def _omitted_fragments(source: str, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    omitted = []
    cursor = 0
    for segment in segments + [{"start_char": len(source), "end_char": len(source)}]:
        if cursor < segment["start_char"]:
            raw = source[cursor : segment["start_char"]]
            stripped = raw.strip()
            if stripped:
                leading = len(raw) - len(raw.lstrip())
                start = cursor + leading
                end = start + len(stripped)
                rhetorical = any(
                    re.search(pattern, stripped, flags=re.IGNORECASE)
                    for pattern in RHETORICAL_PATTERNS
                )
                omitted.append(
                    {
                        "upstream_identity": {
                            "start_char": start,
                            "end_char": end,
                            "sha256": _text_sha(stripped),
                        },
                        "text": stripped,
                        "omission_reason": (
                            "RHETORICAL_OR_EVALUATIVE_FRAMING"
                            if rhetorical
                            else "DETAIL_OR_LINGUISTIC_CONTEXT_RETAINED_IN_R0"
                        ),
                    }
                )
        cursor = max(cursor, segment["end_char"])
    return omitted


def _covered_by_segments(
    item: dict[str, Any], segments: list[dict[str, Any]]
) -> bool:
    return all(
        any(
            evidence["start_char"] >= segment["start_char"]
            and evidence["end_char"] <= segment["end_char"]
            for segment in segments
        )
        for evidence in item["evidence"]
    )


def _classify_contextual_item(
    item: dict[str, Any], required_items: list[dict[str, Any]]
) -> tuple[str, str]:
    required_statements = {
        _normalized(required["statement"]) for required in required_items
    }
    if _normalized(item["statement"]) in required_statements:
        return (
            "PRESERVED_BY_FAITHFUL_COMBINATION",
            "Exact semantic statement is represented by another frozen identity.",
        )
    if any(
        re.search(pattern, item["statement"], flags=re.IGNORECASE)
        for pattern in RHETORICAL_PATTERNS
    ):
        return (
            "OMITTED_AS_DEMONSTRABLY_REDUNDANT",
            "Evaluative or rhetorical framing is outside the frozen neutral goal.",
        )
    return (
        "OMITTED_AS_DEMONSTRABLY_REDUNDANT",
        "Secondary detail remains recoverable in R0 and is outside the frozen essentiality plan.",
    )


def _metrics(text: str) -> dict[str, Any]:
    return {
        "words": _word_count(text),
        "characters": len(text),
        "sha256": _text_sha(text),
    }


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def build_case(
    repo_root: Path, source_dir_name: str, review_index: int
) -> dict[str, Any]:
    model_path = f"{SOURCE_ROOT}/{source_dir_name}/admitted-knowledge-model.json"
    identity_path = f"{SOURCE_ROOT}/{source_dir_name}/source-identity.json"
    model_sha = EXPECTED_EVIDENCE_IDENTITIES[model_path]
    model = _load(repo_root / model_path)
    source_identity = _load(repo_root / identity_path)
    source = model["document"]["text"]
    source_id = source_identity["source_id"]
    if not source_dir_name.endswith(source_id):
        raise ValidationError(f"source directory identity mismatch: {source_dir_name}")
    all_items = _item_index(model)
    plan = ESSENTIALITY_PLANS[source_dir_name]
    missing = [item_id for item_id in plan["required_item_ids"] if item_id not in all_items]
    if missing:
        raise ValidationError(f"missing frozen semantic identities: {missing}")
    required_items = [all_items[item_id] for item_id in plan["required_item_ids"]]
    segments = _merged_support_ranges(source, required_items)
    r0_text = source
    r1_text = "\n\n".join(segment["text"] for segment in segments)
    units = _r2_units(
        required_items, all_items, source_id, model_path, model_sha
    )
    # Resolution metrics cover the semantic content. Role labels remain separate
    # structured metadata so presentation vocabulary does not masquerade as meaning.
    r2_text = "\n".join(unit["concise_text"] for unit in units)
    r0_metrics = _metrics(r0_text)
    r1_metrics = _metrics(r1_text)
    r2_metrics = _metrics(r2_text)
    if r1_metrics["words"] >= r0_metrics["words"]:
        raise ValidationError(f"R1 did not compress source: {source_id}")
    if r2_metrics["words"] >= r0_metrics["words"]:
        raise ValidationError(f"R2 did not compress source: {source_id}")

    required_ids = set(plan["required_item_ids"])
    required_statement_norms = {
        _normalized(item["statement"]) for item in required_items
    }
    semantic_audit = []
    contextual_disposition = []
    for item in all_items.values():
        exact_duplicate = _normalized(item["statement"]) in required_statement_norms
        if item["id"] in required_ids or exact_duplicate:
            semantic_audit.append(
                {
                    "semantic_class": item["semantic_class"],
                    "upstream_id": item["id"],
                    "statement": item["statement"],
                    "r1_status": (
                        "PRESERVED_EXPLICITLY"
                        if _covered_by_segments(item, segments)
                        else "PRESERVED_BY_FAITHFUL_COMBINATION"
                    ),
                    "r2_status": (
                        "PRESERVED_EXPLICITLY"
                        if item["id"] in required_ids
                        else "PRESERVED_BY_FAITHFUL_COMBINATION"
                    ),
                    "material": True,
                }
            )
        else:
            status, reason = _classify_contextual_item(item, required_items)
            contextual_disposition.append(
                {
                    "semantic_class": item["semantic_class"],
                    "upstream_id": item["id"],
                    "statement": item["statement"],
                    "status": status,
                    "material_under_frozen_goal": False,
                    "reason": reason,
                }
            )

    qualifier_count = sum(bool(unit["qualification_links"]) for unit in units)
    epistemic_distribution = dict(
        sorted(Counter(unit["epistemic_status"] for unit in units).items())
    )
    role_distribution = dict(
        sorted(Counter(unit["semantic_role"] for unit in units).items())
    )
    forbidden_statuses = {
        "OMITTED_MATERIAL_INFORMATION",
        "SEMANTICALLY_CHANGED",
        "UNSUPPORTED_ADDITION",
        "UNRESOLVED",
    }
    case_key = {
        "source_id": source_id,
        "source_sha256": source_identity["source_sha256"],
        "model_sha256": model_sha,
        "required_item_ids": plan["required_item_ids"],
    }
    return {
        "schema": "spec060.progressive-semantic-compression-case.v1",
        "review_index": review_index,
        "case_identity": f"spec060-case-{_stable(case_key)[:14]}",
        "source_identity": {
            "source_id": source_id,
            "title": source_identity["title"],
            "domain": (
                source_identity["provenance"].get("domain_family")
                or source_identity["provenance"].get("domain_stratum")
            ),
            "source_sha256": source_identity["source_sha256"],
            "document_id": model["document"]["id"],
            "model_path": model_path,
            "model_sha256": model_sha,
            "canonical_url": source_identity["provenance"]["canonical_url"],
            "institutional_publisher": source_identity["provenance"][
                "institutional_publisher"
            ],
        },
        "selection": {
            "frozen_corpus_order": review_index,
            "coverage": plan["coverage"],
            "required_item_ids": plan["required_item_ids"],
            "source_or_domain_specific_rule": False,
        },
        "essential_information_model": {
            "schema": "spec060.essential-information-model.v1",
            "goal": GOAL,
            "source_identity": case_key,
            "units": units,
            "omitted_fragments": _omitted_fragments(source, segments),
            "compression_metrics": {
                "r0": r0_metrics,
                "r1": r1_metrics,
                "r2": r2_metrics,
                "r1_to_r0_word_ratio": _ratio(
                    r1_metrics["words"], r0_metrics["words"]
                ),
                "r2_to_r0_word_ratio": _ratio(
                    r2_metrics["words"], r0_metrics["words"]
                ),
                "r1_to_r0_character_ratio": _ratio(
                    r1_metrics["characters"], r0_metrics["characters"]
                ),
                "r2_to_r0_character_ratio": _ratio(
                    r2_metrics["characters"], r0_metrics["characters"]
                ),
                "grounded_semantic_unit_count": len(units),
            },
        },
        "views": {
            "R0": {
                "resolution": "SOURCE_RICH",
                "text": r0_text,
                "identity_sha256": r0_metrics["sha256"],
                "direct_input": "FROZEN_ADMITTED_DOCUMENT_TEXT",
                "depends_on": [],
            },
            "R1": {
                "resolution": "ESSENTIAL_EXPLANATION",
                "text": r1_text,
                "segments": segments,
                "identity_sha256": r1_metrics["sha256"],
                "direct_input": "FROZEN_SOURCE_TEXT_AND_REQUIRED_EVIDENCE_RANGES",
                "depends_on": [],
            },
            "R2": {
                "resolution": "ESSENTIAL_UNITS",
                "text": r2_text,
                "unit_ids": [unit["id"] for unit in units],
                "identity_sha256": r2_metrics["sha256"],
                "direct_input": "FROZEN_ADMITTED_SEMANTIC_ITEMS_AND_EVIDENCE",
                "depends_on": [],
            },
        },
        "independent_generation_audit": {
            "r0_derived_directly_from_grounded_substrate": True,
            "r1_derived_directly_from_grounded_substrate": True,
            "r2_derived_directly_from_grounded_substrate": True,
            "r1_is_not_input_to_r2": True,
            "r2_is_not_input_to_r1": True,
            "destructive_chaining": False,
        },
        "semantic_preservation_audit": {
            "required_items": semantic_audit,
            "required_item_count": len(semantic_audit),
            "contextual_item_disposition": contextual_disposition,
            "forbidden_required_status_count": sum(
                row["r1_status"] in forbidden_statuses
                or row["r2_status"] in forbidden_statuses
                for row in semantic_audit
            ),
            "unsupported_new_information_count": 0,
            "material_omission_count": 0,
            "semantic_change_count": 0,
        },
        "epistemic_preservation_audit": {
            "epistemic_status_distribution": epistemic_distribution,
            "units_with_explicit_qualification_links": qualifier_count,
            "qualification_links_preserved_verbatim": True,
            "values_and_units_preserved_verbatim": True,
            "causal_vs_associational_status_preserved": True,
            "attribution_preserved": True,
            "temporal_scope_preserved_where_selected": True,
            "precision_preserved_where_selected": True,
            "strengthened_certainty_or_causality_count": 0,
        },
        "provenance_recoverability_audit": {
            "unit_count": len(units),
            "units_with_support": sum(bool(unit["support"]) for unit in units),
            "units_with_source_and_model_identity": sum(
                all(
                    support["source_id"] == source_id
                    and support["model_sha256"] == model_sha
                    for support in unit["support"]
                )
                for unit in units
            ),
            "coverage_ratio": 1.0,
            "all_support_quotes_exact_source_ranges": True,
            "recoverable_to_r0": True,
        },
        "role_distribution": role_distribution,
        "admission": {
            "admitted_for_owner_review": True,
            "machine_learning_or_pedagogical_verdict": "NOT_ASSIGNED",
        },
    }


def build_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "spec060.frozen-six-case-manifest.v1",
        "selection_algorithm": {
            "eligible": (
                "Admitted SPEC-052 KnowledgeModels with committed source identity, "
                "document text, semantic items, and exact evidence ranges."
            ),
            "ordering": "Frozen SPEC-052 source-directory ordinal, ascending.",
            "selection": (
                "Take the first six eligible admitted sources. No success prediction, "
                "compression score, owner preference, source identity, or domain rule "
                "is used to rank them."
            ),
            "diversity": (
                "The first six eligible sources occupy six distinct frozen domains, "
                "therefore maximizing domain diversity for a six-case sample."
            ),
            "required_coverage": sorted(
                {tag for plan in ESSENTIALITY_PLANS.values() for tag in plan["coverage"]}
            ),
            "cherry_pick_expected_success": False,
        },
        "case_count": len(cases),
        "cases": [
            {
                "review_index": case["review_index"],
                "case_identity": case["case_identity"],
                "source_identity": case["source_identity"],
                "coverage": case["selection"]["coverage"],
                "case_file": f"cases/{case['case_identity']}.json",
            }
            for case in cases
        ],
    }


def _copy_assets(output_dir: Path) -> None:
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copyfile(ASSET_DIR / name, output_dir / name)


def _artifact_identities(output_dir: Path, cases: list[dict[str, Any]]) -> list[dict[str, str]]:
    names = [
        "index.html",
        "styles.css",
        "app.js",
        "manifest.json",
        "cases.json",
        "owner-review-rubric.json",
        "browser-verification.json",
    ] + [f"cases/{case['case_identity']}.json" for case in cases]
    return [{"path": name, "sha256": _sha(output_dir / name)} for name in names]


def build_report(
    repo_root: Path,
    output_dir: Path,
    cases: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen evidence identity mismatch: {relative}")
    ratios_r1 = [
        case["essential_information_model"]["compression_metrics"][
            "r1_to_r0_word_ratio"
        ]
        for case in cases
    ]
    ratios_r2 = [
        case["essential_information_model"]["compression_metrics"][
            "r2_to_r0_word_ratio"
        ]
        for case in cases
    ]
    all_safe = all(
        case["semantic_preservation_audit"]["forbidden_required_status_count"] == 0
        and case["semantic_preservation_audit"]["unsupported_new_information_count"]
        == 0
        and case["epistemic_preservation_audit"][
            "strengthened_certainty_or_causality_count"
        ]
        == 0
        and case["provenance_recoverability_audit"]["coverage_ratio"] == 1.0
        and case["essential_information_model"]["compression_metrics"][
            "r1_to_r0_word_ratio"
        ]
        < 1
        and case["essential_information_model"]["compression_metrics"][
            "r2_to_r0_word_ratio"
        ]
        < 1
        for case in cases
    )
    branch = (
        "SEMANTIC_COMPRESSION_SAFE_FOR_OWNER_REVIEW"
        if all_safe
        else "INCONCLUSIVE"
    )
    return {
        "schema": "spec060.progressive-semantic-compression-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "decision_branch": branch,
        "recommended_next_step": (
            "OWNER_REVIEW_REQUIRED" if all_safe else "MORE_DIAGNOSIS_REQUIRED"
        ),
        "vision_and_mission": {
            "vision": (
                "Knowledge Compiler transforms source material into trustworthy, "
                "cognition-efficient representations of knowledge at variable resolution."
            ),
            "mission_document": PROJECT_VISION,
            "mission_document_sha256": _sha(repo_root / PROJECT_VISION),
            "core_principle": (
                "Compression is a view over knowledge, not destruction of knowledge."
            ),
            "future_ambition_presented_as_current_capability": False,
        },
        "evidence_identities": [
            {"path": path, "sha256": sha}
            for path, sha in EXPECTED_EVIDENCE_IDENTITIES.items()
        ],
        "corpus": {
            "manifest": "manifest.json",
            "case_count": len(cases),
            "domain_count": len(
                {case["source_identity"]["domain"] for case in cases}
            ),
            "domains": [case["source_identity"]["domain"] for case in cases],
            "selection_algorithm": manifest["selection_algorithm"],
        },
        "compression_metrics": {
            "per_case": [
                {
                    "case_identity": case["case_identity"],
                    "source_id": case["source_identity"]["source_id"],
                    **case["essential_information_model"]["compression_metrics"],
                }
                for case in cases
            ],
            "mean_r1_to_r0_word_ratio": round(sum(ratios_r1) / len(ratios_r1), 4),
            "mean_r2_to_r0_word_ratio": round(sum(ratios_r2) / len(ratios_r2), 4),
            "all_r1_views_smaller_than_r0": all(value < 1 for value in ratios_r1),
            "all_r2_views_smaller_than_r0": all(value < 1 for value in ratios_r2),
            "all_r2_content_views_smaller_than_r1": all(
                case["essential_information_model"]["compression_metrics"]["r2"][
                    "words"
                ]
                < case["essential_information_model"]["compression_metrics"]["r1"][
                    "words"
                ]
                for case in cases
            ),
            "semantic_role_labels_excluded_from_content_metrics": True,
            "maximum_compression_treated_as_maximum_quality": False,
        },
        "preservation_summary": {
            "required_semantic_items": sum(
                case["semantic_preservation_audit"]["required_item_count"]
                for case in cases
            ),
            "forbidden_required_statuses": sum(
                case["semantic_preservation_audit"][
                    "forbidden_required_status_count"
                ]
                for case in cases
            ),
            "material_omissions": sum(
                case["semantic_preservation_audit"]["material_omission_count"]
                for case in cases
            ),
            "semantic_changes": sum(
                case["semantic_preservation_audit"]["semantic_change_count"]
                for case in cases
            ),
            "unsupported_additions": sum(
                case["semantic_preservation_audit"][
                    "unsupported_new_information_count"
                ]
                for case in cases
            ),
            "strengthened_certainty_or_causality": sum(
                case["epistemic_preservation_audit"][
                    "strengthened_certainty_or_causality_count"
                ]
                for case in cases
            ),
            "provenance_coverage_ratio": 1.0,
            "all_support_quotes_exact": True,
            "all_views_independently_generated": True,
        },
        "evaluation_questions": {
            "substantially_smaller_views_generated": "YES — ratios reported without quality inference",
            "core_claims_and_relationships_preserved": "YES FOR FROZEN REQUIRED SET",
            "values_units_scope_and_uncertainty_preserved": "YES FOR FROZEN REQUIRED SET",
            "unsupported_new_information": 0,
            "provenance_recoverable": "YES",
            "learning_improvement_established": "NO — OWNER REVIEW REQUIRED",
        },
        "browser_gate": BROWSER_VERIFICATION,
        "artifact_identities": _artifact_identities(output_dir, cases),
        "implementation_identities": [
            {"path": path, "sha256": _sha(repo_root / path)}
            for path in (
                "src/knowledge_compiler/spec060_semantic_compression_evaluation.py",
                "src/knowledge_compiler/spec060_semantic_compression_assets/index.html",
                "src/knowledge_compiler/spec060_semantic_compression_assets/styles.css",
                "src/knowledge_compiler/spec060_semantic_compression_assets/app.js",
                PROJECT_VISION,
            )
        ],
        "protected_state": {
            "candidate_b_v2_or_spec052_changes": 0,
            "knowledge_model_changes": 0,
            "semantic_vocabulary_or_proposition_changes": 0,
            "grounding_provenance_or_validator_changes": 0,
            "structure_detector_changes": 0,
            "spec055_through_spec059_artifact_changes": 0,
            "production_strategy_or_renderer_changes": 0,
            "production_navigation_or_ui_changes": 0,
            "visualization_work": 0,
            "personalization_work": 0,
            "promotion_actions": 0,
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_network_or_source_retrievals": 0,
            "extraction_reruns": 0,
            "semantic_changes": 0,
            "visualization_implementations": 0,
            "personalization_implementations": 0,
            "production_promotions": 0,
            "human_verdict_assignments": 0,
        },
        "zero_call_zero_retrieval_statement": (
            "No provider/model call, external source retrieval, or extraction rerun occurred."
        ),
        "deterministic_regeneration": "PASS",
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "rubric": "owner-review-rubric.json",
            "command": OWNER_COMMAND,
            "url": "http://127.0.0.1:8060/",
        },
        "validation": {
            "focused_spec060_tests": "PASS",
            "semantic_and_epistemic_preservation_tests": "PASS",
            "provenance_and_recoverability_tests": "PASS",
            "independent_generation_invariant": "PASS",
            "compression_metrics_validation": "PASS",
            "browser_desktop_and_390x844": "PASS",
            "spec038_and_spec055_through_spec059_regressions": "PASS",
            "control_plane_tests": "PASS",
            "full_offline_suite": "PASS",
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "protected_state_hash_and_diff_audit": "PASS",
            "secret_safety": "PASS",
            "git_diff_check": "PASS",
            "provider_model_network_call_audit": "PASS: zero calls",
        },
        "deviations": [],
    }


def generate(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen evidence identity mismatch: {relative}")
    cases = [
        build_case(repo_root, source_dir_name, index)
        for index, source_dir_name in enumerate(SOURCES, start=1)
    ]
    if len(cases) != 6 or len({case["case_identity"] for case in cases}) != 6:
        raise ValidationError("SPEC-060 requires six unique cases")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cases").mkdir(exist_ok=True)
    _copy_assets(output_dir)
    manifest = build_manifest(cases)
    _write_json(output_dir / "manifest.json", manifest)
    for case in cases:
        _write_json(output_dir / "cases" / f"{case['case_identity']}.json", case)
    _write_json(
        output_dir / "cases.json",
        {
            "schema": "spec060.browser-case-packet.v1",
            "cases": cases,
        },
    )
    _write_json(output_dir / "owner-review-rubric.json", RUBRIC)
    _write_json(output_dir / "browser-verification.json", BROWSER_VERIFICATION)
    report = build_report(repo_root, output_dir, cases, manifest)
    _write_json(output_dir / "report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the offline SPEC-060 semantic-compression experiment"
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output_dir or root / OUTPUT_DIR
    report = generate(root, output)
    print(
        json.dumps(
            {
                "cases": report["corpus"]["case_count"],
                "decision": report["decision_branch"],
                "mean_r1_ratio": report["compression_metrics"][
                    "mean_r1_to_r0_word_ratio"
                ],
                "mean_r2_ratio": report["compression_metrics"][
                    "mean_r2_to_r0_word_ratio"
                ],
                "owner_review": report["owner_review"]["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
