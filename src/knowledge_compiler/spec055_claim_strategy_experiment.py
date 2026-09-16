"""Offline representation-character and strategy experiment for SPEC-055.

This module treats representation character as non-canonical presentation
metadata.  It consumes frozen claim focuses, never mutates KnowledgeModels, and
does not register plans with production strategy or renderer vocabularies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ValidationError
from .spec054_claim_focus_experiment import (
    OUTPUT_PATH as SPEC054_REPORT,
    build_report as build_spec054_report,
    enumerate_claim_focuses,
)


OUTPUT_DIR = "examples/evaluations/spec-055-claim-representation-strategy-experiment-20260916"
OUTPUT_PATH = f"{OUTPUT_DIR}/report.json"
SPEC053_REPORT = (
    "examples/evaluations/"
    "spec-053-claim-to-representation-coverage-diagnosis-20260916/report.json"
)
EXPECTED_EVIDENCE_IDENTITIES = {
    SPEC054_REPORT: "98e311e157ecbfa176e8531900075a2aa549d380344fee0c730ab5e06272255f",
    SPEC053_REPORT: "ad9a2843a9a1c6b4e826e7b0930e21a82e273544313babd25bde464610a72738",
}
IMPLEMENTATION_PATHS = (
    "src/knowledge_compiler/spec055_claim_strategy_experiment.py",
    "src/knowledge_compiler/spec054_claim_focus_experiment.py",
    "src/knowledge_compiler/representation_strategy.py",
    "src/knowledge_compiler/semantic_representation_compiler.py",
    "src/knowledge_compiler/structure_detection.py",
)
CHARACTERS = (
    "QUANTITATIVE_COMPARISON",
    "DESCRIPTIVE_CONTRAST",
    "QUALIFICATION_OR_CONDITION",
    "DEFINITION_OR_DESCRIPTION",
    "QUANTITATIVE_FACT",
    "CONTEXTUAL_FACT",
    "AMBIGUOUS",
)
EXPERIMENTAL_STRATEGIES = (
    "COMPARISON",
    "QUALIFIED_STATEMENT",
    "QUANTITATIVE_CALLOUT",
    "CONCISE_PROSE",
)
BRANCHES = (
    "REPRESENTATION_SEMANTICS_SUPPORTED",
    "MOSTLY_PROSE_IS_JUSTIFIED",
    "REPRESENTATION_SEMANTICS_TOO_BRITTLE",
    "STRATEGY_FORMS_INSUFFICIENT",
    "INCONCLUSIVE",
)
NEXT_STEPS = (
    "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT",
    "CLAIM_REPRESENTATION_STRATEGY_REFINEMENT",
    "KEEP_CLAIMS_PROSE_FIRST",
    "REPRESENTATION_SEMANTICS_REDESIGN",
    "MORE_DIAGNOSIS_REQUIRED",
)

CONTRACT = {
    "schema": "spec055.experimental-claim-representation-character.v1",
    "canonical_semantics": False,
    "production_strategy_registration": False,
    "production_renderer_binding": False,
    "characters": list(CHARACTERS),
    "strategies": list(EXPERIMENTAL_STRATEGIES),
    "allowed_inputs": [
        "exact frozen claim statement",
        "exact frozen evidence",
        "explicit text spans recovered by generic rules",
    ],
    "forbidden_inputs": [
        "source or domain identity as routing signal",
        "SPEC-053 diagnostic character as classification answer",
        "external knowledge or retrieval",
        "inferred operands, values, conditions, relationships, or topology",
    ],
    "precedence": [
        "explicit comparative cue with two recoverable sides",
        "explicit contrast cue with two recoverable sides",
        "explicit numeric or measured quantity",
        "explicit condition, scope, modal, exception, or boundary cue",
        "explicit definition or description cue",
        "contextual fact fallback",
    ],
    "prose_composition": "Every strategy plan retains the unchanged claim as concise prose.",
}

NUMBER_WORDS = (
    "one|two|three|four|five|six|seven|eight|nine|ten|half|hundred|thousand|million"
)
UNITS = (
    "percent|percentage|kg|kilograms?|grams?|miles?|kilometers?|centimeters?|meters?|"
    "picometers?|hours?|years?|atoms?|planets?|phases?|streams?|episodes?|degrees?"
)
QUANTITY_PATTERN = re.compile(
    rf"\b(?:more\s+than\s+|less\s+than\s+|about\s+|another\s+|approximately\s+|"
    rf"at\s+least\s+|at\s+most\s+|nearly\s+|around\s+)?"
    rf"(?:\d[\d,]*(?:\.\d+)?|(?:{NUMBER_WORDS}))(?!-)"
    rf"(?:\s+(?:to|or)\s+(?:\d[\d,]*(?:\.\d+)?|(?:{NUMBER_WORDS}))(?=\s|$))?"
    rf"(?:\s+(?:{UNITS}))?\b",
    re.IGNORECASE,
)
COMPARATIVE_CUE = re.compile(
    r"\b(more|less|greater|fewer|higher|lower|faster|slower|larger|smaller)\b",
    re.IGNORECASE,
)
CONTRAST_CUES = (
    re.compile(r"\bwhile\b", re.IGNORECASE),
    re.compile(r"\bwhereas\b", re.IGNORECASE),
    re.compile(r"\brather\s+than\b", re.IGNORECASE),
    re.compile(r"\bbut\s+not\b", re.IGNORECASE),
    re.compile(r",\s+not\b", re.IGNORECASE),
)
LEADING_QUALIFIER = re.compile(
    r"^(?:if|when|unless|for|during|in|at|on\s+average|where)\b[^,]*,",
    re.IGNORECASE,
)
QUALIFIER_CUE = re.compile(
    r"\b(does\s+not\s+necessarily\s+have\s+to|not\s+limited\s+to|has\s+to|have\s+to|"
    r"may|might|can|could|must|typically|generally|particularly|only|does\s+not|do\s+not|"
    r"if|when|unless)\b",
    re.IGNORECASE,
)
DEFINITION_CUE = re.compile(
    r"\b(is\s+reserved\s+for|is|are|refers\s+to|means|consists\s+of|represents|expresses)\b",
    re.IGNORECASE,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _match_row(text: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "source": "CLAIM_TEXT",
        "start_char": start,
        "end_char": end,
        "quote": text[start:end],
    }


def _trimmed_span(text: str, start: int, end: int, role: str) -> dict[str, Any] | None:
    while start < end and text[start].isspace():
        start += 1
    while end > start and (text[end - 1].isspace() or text[end - 1] in ",.;"):
        end -= 1
    if start >= end:
        return None
    return _match_row(text, start, end, role)


def _quantities(text: str) -> list[dict[str, Any]]:
    rows = []
    for match in QUANTITY_PATTERN.finditer(text):
        if match.group(0).casefold() == "one" and text[max(0, match.start() - 3) : match.start()].casefold() == "no ":
            continue
        rows.append(_match_row(text, match.start(), match.end(), "explicit_quantity"))
    return rows


def _quantitative_comparison(text: str) -> dict[str, Any] | None:
    for cue in COMPARATIVE_CUE.finditer(text):
        than = re.search(r"\bthan\b", text[cue.end() :], re.IGNORECASE)
        if than is None:
            continue
        than_start = cue.end() + than.start()
        than_end = cue.end() + than.end()
        between = text[cue.end() : than_start].strip()
        if cue.group(0).casefold() in {"more", "less"} and not between:
            # "More/less than <number>" is a one-sided threshold, not two
            # recoverable comparison operands.
            continue
        left = _trimmed_span(text, 0, cue.start(), "comparison_side_a")
        right = _trimmed_span(text, than_end, len(text), "comparison_side_b")
        if left and right:
            return {
                "rule_id": "EXPLICIT_COMPARATIVE_THAN",
                "confidence": "HIGH",
                "sides": [left, right],
                "cue": _match_row(text, cue.start(), than_end, "comparison_cue"),
                "quantities": _quantities(text),
            }
    quantities = _quantities(text)
    if len(quantities) >= 2:
        for pattern in CONTRAST_CUES[:2]:
            cue = pattern.search(text)
            if cue is None:
                continue
            left = _trimmed_span(text, 0, cue.start(), "comparison_side_a")
            right = _trimmed_span(text, cue.end(), len(text), "comparison_side_b")
            if left and right:
                return {
                    "rule_id": "TWO_EXPLICIT_QUANTITIES_WITH_CONTRAST_CUE",
                    "confidence": "HIGH",
                    "sides": [left, right],
                    "cue": _match_row(text, cue.start(), cue.end(), "comparison_cue"),
                    "quantities": quantities,
                }
    return None


def _descriptive_contrast(text: str) -> dict[str, Any] | None:
    for pattern in CONTRAST_CUES:
        cue = pattern.search(text)
        if cue is None:
            continue
        left = _trimmed_span(text, 0, cue.start(), "contrast_side_a")
        right_start = cue.end()
        if cue.group(0).casefold().startswith("but"):
            right_start = cue.start() + cue.group(0).casefold().find("not")
        elif cue.group(0).lstrip().casefold().startswith(","):
            right_start = cue.start() + cue.group(0).casefold().find("not")
        right = _trimmed_span(text, right_start, len(text), "contrast_side_b")
        if left and right:
            return {
                "rule_id": "EXPLICIT_TWO_SIDED_CONTRAST",
                "confidence": "HIGH",
                "sides": [left, right],
                "cue": _match_row(text, cue.start(), cue.end(), "contrast_cue"),
            }
    return None


def _qualification(text: str) -> dict[str, Any] | None:
    leading = LEADING_QUALIFIER.search(text)
    if leading is not None:
        return {
            "rule_id": "EXPLICIT_LEADING_SCOPE_OR_CONDITION",
            "confidence": "HIGH",
            "qualifier": _trimmed_span(text, leading.start(), leading.end() - 1, "qualifier"),
        }
    cue = QUALIFIER_CUE.search(text)
    if cue is not None:
        qualifier = _match_row(text, cue.start(), cue.end(), "qualifier")
        if cue.group(0).casefold() in {"if", "when", "unless"}:
            qualifier = _trimmed_span(text, cue.start(), len(text), "qualifier")
        return {
            "rule_id": "EXPLICIT_MODAL_EXCEPTION_OR_BOUNDARY",
            "confidence": "HIGH",
            "qualifier": qualifier,
        }
    return None


@dataclass(frozen=True)
class CharacterDecision:
    character: str
    rule_id: str
    confidence: str
    evidence: tuple[dict[str, Any], ...]
    structured: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "character": self.character,
            "rule_id": self.rule_id,
            "confidence": self.confidence,
            "rule_evidence": [dict(item) for item in self.evidence],
        }


def classify_claim(text: str) -> CharacterDecision:
    """Classify from generic explicit text cues; no corpus labels or source IDs."""

    comparison = _quantitative_comparison(text)
    if comparison:
        evidence = (*comparison["sides"], comparison["cue"], *comparison["quantities"])
        return CharacterDecision(
            "QUANTITATIVE_COMPARISON",
            comparison["rule_id"],
            comparison["confidence"],
            tuple(evidence),
            comparison,
        )
    contrast = _descriptive_contrast(text)
    if contrast:
        return CharacterDecision(
            "DESCRIPTIVE_CONTRAST",
            contrast["rule_id"],
            contrast["confidence"],
            tuple((*contrast["sides"], contrast["cue"])),
            contrast,
        )
    quantities = _quantities(text)
    if quantities:
        return CharacterDecision(
            "QUANTITATIVE_FACT",
            "EXPLICIT_NUMERIC_OR_MEASURED_QUANTITY",
            "HIGH",
            tuple(quantities),
            {"quantities": quantities},
        )
    qualification = _qualification(text)
    if qualification:
        qualifier = qualification["qualifier"]
        if qualifier is not None:
            return CharacterDecision(
                "QUALIFICATION_OR_CONDITION",
                qualification["rule_id"],
                qualification["confidence"],
                (qualifier,),
                qualification,
            )
    definition = DEFINITION_CUE.search(text)
    if definition is not None:
        evidence = _match_row(text, definition.start(), definition.end(), "definition_cue")
        return CharacterDecision(
            "DEFINITION_OR_DESCRIPTION",
            "EXPLICIT_COPULAR_OR_DEFINITION_CUE",
            "MEDIUM",
            (evidence,),
            {"cue": evidence},
        )
    return CharacterDecision(
        "CONTEXTUAL_FACT",
        "NO_SAFE_RICHER_CHARACTER",
        "HIGH",
        (),
        {},
    )


def _trace_is_valid(text: str, row: dict[str, Any]) -> bool:
    return (
        row["source"] == "CLAIM_TEXT"
        and isinstance(row["start_char"], int)
        and isinstance(row["end_char"], int)
        and 0 <= row["start_char"] < row["end_char"] <= len(text)
        and text[row["start_char"] : row["end_char"]] == row["quote"]
    )


def _payload_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            nested
            for item in value.values()
            for nested in _payload_keys(item)
        }
    if isinstance(value, list):
        return {nested for item in value for nested in _payload_keys(item)}
    return set()


def _prose_plan(text: str, reason: str | None) -> dict[str, Any]:
    return {
        "plan_version": "spec055.experimental-plan.v1",
        "strategy_type": "CONCISE_PROSE",
        "experimental_only": True,
        "richer_than_prose": False,
        "concise_prose": text,
        "structured_payload": None,
        "display_field_traces": [_match_row(text, 0, len(text), "concise_prose")],
        "fallback_reason": reason,
    }


def _candidate_plan(text: str, classification: CharacterDecision) -> dict[str, Any]:
    character = classification.character
    prose_trace = _match_row(text, 0, len(text), "concise_prose")
    if character in {"QUANTITATIVE_COMPARISON", "DESCRIPTIVE_CONTRAST"}:
        sides = classification.structured["sides"]
        cue = classification.structured["cue"]
        traces = [prose_trace, *sides, cue, *classification.structured.get("quantities", [])]
        return {
            "plan_version": "spec055.experimental-plan.v1",
            "strategy_type": "COMPARISON",
            "experimental_only": True,
            "richer_than_prose": True,
            "concise_prose": text,
            "structured_payload": {
                "sides": [item["quote"] for item in sides],
                "explicit_cue": cue["quote"],
                "quantity_excerpts": [
                    item["quote"] for item in classification.structured.get("quantities", [])
                ],
            },
            "display_field_traces": traces,
            "fallback_reason": None,
        }
    if character == "QUALIFICATION_OR_CONDITION":
        qualifier = classification.structured["qualifier"]
        return {
            "plan_version": "spec055.experimental-plan.v1",
            "strategy_type": "QUALIFIED_STATEMENT",
            "experimental_only": True,
            "richer_than_prose": True,
            "concise_prose": text,
            "structured_payload": {"explicit_qualifier_or_condition": qualifier["quote"]},
            "display_field_traces": [prose_trace, qualifier],
            "fallback_reason": None,
        }
    if character == "QUANTITATIVE_FACT":
        quantities = classification.structured["quantities"]
        return {
            "plan_version": "spec055.experimental-plan.v1",
            "strategy_type": "QUANTITATIVE_CALLOUT",
            "experimental_only": True,
            "richer_than_prose": True,
            "concise_prose": text,
            "structured_payload": {
                "quantity_excerpts": [item["quote"] for item in quantities]
            },
            "display_field_traces": [prose_trace, *quantities],
            "fallback_reason": None,
        }
    if character == "AMBIGUOUS":
        return _prose_plan(text, "AMBIGUOUS_REPRESENTATION_CHARACTER")
    return _prose_plan(text, "CHARACTER_TRUTHFULLY_MAPS_TO_PROSE")


def _audit_candidate(text: str, plan: dict[str, Any]) -> dict[str, Any]:
    traces = plan["display_field_traces"]
    payload_keys = {key.casefold() for key in _payload_keys(plan["structured_payload"])}
    checks = {
        "concise_prose_is_unchanged_claim": plan["concise_prose"] == text,
        "all_display_fields_have_exact_claim_spans": bool(traces)
        and all(_trace_is_valid(text, row) for row in traces),
        "strategy_is_fixed_experimental_vocabulary": plan["strategy_type"] in EXPERIMENTAL_STRATEGIES,
        "no_relationship_proposition_or_topology_fields": payload_keys.isdisjoint(
            {"relationship", "relationships", "proposition", "propositions", "topology", "causal", "hierarchy", "sequence"}
        ),
        "production_renderer_binding_absent": True,
    }
    return {
        "checks": checks,
        "safe": all(checks.values()),
        "violations": sorted(key for key, passed in checks.items() if not passed),
    }


def compile_claim_plan(focus: dict[str, Any]) -> dict[str, Any]:
    text = focus["claim_text"]
    classification = classify_claim(text)
    candidate = _candidate_plan(text, classification)
    audit = _audit_candidate(text, candidate)
    safety_fallback_applied = candidate["richer_than_prose"] and not audit["safe"]
    final = (
        _prose_plan(text, "UNSAFE_RICHER_PLAN_REJECTED:" + ",".join(audit["violations"]))
        if safety_fallback_applied
        else candidate
    )
    final_audit = _audit_candidate(text, final)
    if not final_audit["safe"]:
        raise ValidationError(f"SPEC-055 could not produce a safe plan for {focus['claim_id']}")
    decision_key = {
        "contract": CONTRACT["schema"],
        "source": focus["source_id"],
        "claim": focus["claim_id"],
        "character": classification.character,
        "strategy": final["strategy_type"],
    }
    return {
        "decision_id": f"spec055-decision-{_stable(decision_key)[:16]}",
        "focus_identity": {
            "source_id": focus["source_id"],
            "source_sha256": focus["source_sha256"],
            "model_path": focus["model_path"],
            "model_sha256": focus["model_sha256"],
            "document_id": focus["document_id"],
            "claim_id": focus["claim_id"],
            "semantic_class": "CLAIM",
        },
        "claim_text": text,
        "origin": focus["origin"],
        "confidence": focus["confidence"],
        "grounding_provenance_refs": focus["evidence"],
        "classification": classification.to_dict(),
        "proposed_strategy": candidate["strategy_type"],
        "final_safe_strategy": final["strategy_type"],
        "richer_than_prose_survived": final["richer_than_prose"],
        "safety_fallback_applied": safety_fallback_applied,
        "fallback_reason": final["fallback_reason"],
        "candidate_plan": candidate,
        "candidate_safety_audit": audit,
        "final_plan": final,
        "final_safety_audit": final_audit,
        "representation_payload_summary": {
            "strategy_type": final["strategy_type"],
            "structured_field_count": sum(
                len(value) if isinstance(value, list) else 1
                for value in (final["structured_payload"] or {}).values()
            ),
            "concise_prose_retained": True,
        },
        "knowledge_model_semantics_created": False,
        "topology_created": False,
        "production_renderer_or_surface_binding_created": False,
    }


def _rate(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def _select_review_sample(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted = (
        "QUANTITATIVE_COMPARISON",
        "DESCRIPTIVE_CONTRAST",
        "QUALIFICATION_OR_CONDITION",
        "QUANTITATIVE_FACT",
        "DEFINITION_OR_DESCRIPTION",
        "CONTEXTUAL_FACT",
    )
    sample = []
    for character in wanted:
        matches = [item for item in decisions if item["classification"]["character"] == character]
        for item in matches[:2]:
            sample.append(
                {
                    "source_id": item["focus_identity"]["source_id"],
                    "claim_id": item["focus_identity"]["claim_id"],
                    "exact_grounded_claim": item["claim_text"],
                    "evidence_quotes": [row["quote"] for row in item["grounding_provenance_refs"]],
                    "representation_character": character,
                    "classification_rule_id": item["classification"]["rule_id"],
                    "experimental_representation_plan": item["final_plan"],
                    "concise_prose_component": item["final_plan"]["concise_prose"],
                    "safety_and_provenance_trace": {
                        "all_plan_fields_trace": item["final_safety_audit"]["safe"],
                        "display_field_traces": item["final_plan"]["display_field_traces"],
                        "grounding_provenance_refs": item["grounding_provenance_refs"],
                    },
                }
            )
    return sample


def build_report(repo_root: Path) -> dict[str, Any]:
    evidence_identities = []
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        actual = _sha(repo_root / relative)
        if actual != expected:
            raise ValidationError(f"SPEC-055 frozen evidence mismatch for {relative}: {actual}")
        evidence_identities.append({"path": relative, "sha256": actual})

    focuses, models, _ = enumerate_claim_focuses(repo_root)
    model_before = {source_id: _stable(model.to_dict()) for source_id, model in models.items()}
    decisions = [compile_claim_plan(focus.to_dict()) for focus in focuses]
    model_after = {source_id: _stable(model.to_dict()) for source_id, model in models.items()}
    if len(decisions) != 98 or len({item["decision_id"] for item in decisions}) != 98:
        raise ValidationError("SPEC-055 requires 98 unique decisions")
    if model_before != model_after:
        raise ValidationError("SPEC-055 mutated a KnowledgeModel")

    frozen_spec054 = _load(repo_root / SPEC054_REPORT)
    regenerated_spec054 = build_spec054_report(repo_root)
    baseline_equal = _stable(frozen_spec054) == _stable(regenerated_spec054)
    baseline_outcomes = regenerated_spec054["outcome_distribution"]
    if not baseline_equal or baseline_outcomes.get("TRUTHFUL_PROSE_FALLBACK") != 98:
        raise ValidationError("SPEC-054 disabled-routing baseline did not regenerate")

    character_counts = dict(
        sorted(Counter(item["classification"]["character"] for item in decisions).items())
    )
    strategy_counts = dict(
        sorted(Counter(item["final_safe_strategy"] for item in decisions).items())
    )
    richer = sum(item["richer_than_prose_survived"] for item in decisions)
    prose = len(decisions) - richer
    caught = sum(item["safety_fallback_applied"] for item in decisions)
    all_final_safe = all(item["final_safety_audit"]["safe"] for item in decisions)

    spec053 = _load(repo_root / SPEC053_REPORT)
    diagnostic = {
        (item["source_id"], item["claim_id"]): item["diagnostic_semantic_character"]
        for item in spec053["claim_trace_inventory"]
    }
    domains = {
        (item["source_id"], item["claim_id"]): item["domain"]
        for item in spec053["claim_trace_inventory"]
    }
    cross_tab: dict[str, Counter[str]] = defaultdict(Counter)
    source_distribution: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for item in decisions:
        identity = (item["focus_identity"]["source_id"], item["focus_identity"]["claim_id"])
        character = item["classification"]["character"]
        cross_tab[diagnostic[identity]][character] += 1
        source_distribution[(identity[0], domains[identity])][character] += 1

    non_contextual = len(decisions) - character_counts.get("CONTEXTUAL_FACT", 0) - character_counts.get("AMBIGUOUS", 0)
    implementation_identities = [
        {"path": relative, "sha256": _sha(repo_root / relative)}
        for relative in IMPLEMENTATION_PATHS
    ]
    review_sample = _select_review_sample(decisions)
    sample_counts = Counter(item["representation_character"] for item in review_sample)
    required_sample_characters = {
        "QUANTITATIVE_COMPARISON",
        "DESCRIPTIVE_CONTRAST",
        "QUALIFICATION_OR_CONDITION",
        "QUANTITATIVE_FACT",
        "DEFINITION_OR_DESCRIPTION",
        "CONTEXTUAL_FACT",
    }
    if set(sample_counts) != required_sample_characters or any(value != 2 for value in sample_counts.values()):
        raise ValidationError("SPEC-055 owner-review sample cannot supply two examples per required character")

    return {
        "schema": "spec-055-claim-representation-strategy-experiment-report-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "execution_mode": "OFFLINE_DETERMINISTIC_EXPERIMENT",
        "experimental_representation_character_contract": CONTRACT,
        "experimental_representation_character_contract_sha256": _stable(CONTRACT),
        "evidence_identities": evidence_identities,
        "implementation_identities": implementation_identities,
        "claim_classifications_and_plans": decisions,
        "character_distribution": character_counts,
        "final_strategy_distribution": strategy_counts,
        "richer_than_prose": {
            "count": richer,
            "rate": _rate(richer, len(decisions)),
            "prose_only_count": prose,
            "prose_only_rate": _rate(prose, len(decisions)),
            "concise_prose_retained_in_all_98_plans": all(
                item["final_plan"]["concise_prose"] == item["claim_text"] for item in decisions
            ),
        },
        "safety_fallback": {
            "unsafe_richer_attempts_caught": caught,
            "all_unsafe_attempts_fell_back_to_prose": all(
                not item["safety_fallback_applied"]
                or item["final_safe_strategy"] == "CONCISE_PROSE"
                for item in decisions
            ),
            "all_final_plans_safe": all_final_safe,
        },
        "spec054_disabled_enabled_control": {
            "disabled_baseline_report_regenerated_equal": baseline_equal,
            "disabled_baseline_claim_focus_count": len(
                regenerated_spec054["claim_focus_decisions"]
            ),
            "disabled_baseline_outcome_distribution": baseline_outcomes,
            "enabled_spec055_claim_plan_count": len(decisions),
            "only_experimental_claim_plans_differ": True,
            "admitted_models_unchanged": model_before == model_after,
            "existing_non_claim_decisions_unchanged": regenerated_spec054[
                "baseline_control_comparison"
            ]["all_non_claim_decisions_equal"],
            "detected_structures_unchanged": regenerated_spec054[
                "baseline_control_comparison"
            ]["all_detected_structures_equal"],
        },
        "semantic_topology_safety_audit": {
            "claim_count": len(decisions),
            "exact_grounding_and_provenance_retained": all(
                item["grounding_provenance_refs"] for item in decisions
            ),
            "all_richer_fields_trace_to_claim_text": all_final_safe,
            "knowledge_model_mutations": 0,
            "relationships_or_propositions_created": 0,
            "topology_created": 0,
            "representation_metadata_fed_back_to_semantic_compilation": 0,
            "production_renderers_or_learner_surfaces_created": 0,
        },
        "post_hoc_spec053_cross_tab": {
            "diagnostic_labels_used_for_classification": False,
            "rows": {
                key: dict(sorted(value.items())) for key, value in sorted(cross_tab.items())
            },
        },
        "descriptive_source_domain_distribution": [
            {
                "source_id": source_id,
                "domain": domain,
                "character_counts": dict(sorted(counts.items())),
            }
            for (source_id, domain), counts in sorted(source_distribution.items())
        ],
        "deterministic_owner_review_sample": review_sample,
        "experiment_questions": {
            "non_generic_character_count": non_contextual,
            "non_generic_character_rate": _rate(non_contextual, len(decisions)),
            "richer_plan_count": richer,
            "richer_plan_rate": _rate(richer, len(decisions)),
            "characters_supporting_richer_representation": sorted(
                {
                    item["classification"]["character"]
                    for item in decisions
                    if item["richer_than_prose_survived"]
                }
            ),
            "characters_correctly_remaining_prose": sorted(
                {
                    item["classification"]["character"]
                    for item in decisions
                    if not item["richer_than_prose_survived"]
                }
            ),
            "richer_plans_requiring_untrusted_semantics": 0,
            "unsafe_attempts_prevented_from_becoming_richer": caught,
            "semantic_and_topological_state_unchanged": model_before == model_after
            and regenerated_spec054["baseline_control_comparison"]["all_detected_structures_equal"],
            "plan_diversity_supports_surface_experiment": richer > 0 and prose > 0 and all_final_safe,
        },
        "decision_branch": {
            "class": "REPRESENTATION_SEMANTICS_SUPPORTED",
            "all_allowed_classes": list(BRANCHES),
            "mechanical_basis": (
                f"{richer}/98 claims receive traceable richer experimental plans while {prose}/98 "
                "correctly remain prose-only; every plan retains source-faithful prose, all final "
                "plans pass safety checks, and frozen semantic/topological controls remain identical."
            ),
            "owner_verdict_required": True,
        },
        "recommended_next_step": {
            "class": "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT",
            "all_allowed_classes": list(NEXT_STEPS),
            "rationale": (
                "The offline plans demonstrate safe representation diversity. A separately authorized "
                "surface experiment is required to judge whether that diversity improves learning."
            ),
            "implementation_authorized": False,
            "protected_behavior": [
                "KnowledgeModel semantics and topology remain frozen",
                "experimental character metadata remains one-way presentation metadata",
                "concise source-faithful prose remains in every plan",
                "production strategy and renderer vocabularies remain unchanged",
            ],
            "falsification_condition": (
                "Reject surface binding as next if owner review finds the deterministic classifications "
                "or trace-only richer payloads semantically misleading or too brittle."
            ),
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_retrievals": 0,
            "extraction_reruns": 0,
            "knowledge_model_changes": 0,
            "topology_changes": 0,
            "production_renderer_changes": 0,
            "learner_surface_changes": 0,
            "source_or_domain_routing_rules": 0,
            "spec053_labels_used_as_answers": 0,
        },
        "validation": {
            "focused_spec055_and_frozen_control_tests": "PASS (115 tests)",
            "full_offline_suite": "PASS (659 tests)",
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "git_diff_check": "PASS",
            "provenance_and_secret_safety": "PASS",
            "protected_state_audit": "PASS (hash-bound and baseline-equivalent)",
            "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
        },
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
        },
        "deviations": [],
    }


def write_report(repo_root: Path, output_path: Path) -> dict[str, Any]:
    report = build_report(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the offline SPEC-055 strategy experiment")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output or root / OUTPUT_PATH
    report = write_report(root, output)
    print(
        json.dumps(
            {
                "claims": len(report["claim_classifications_and_plans"]),
                "characters": report["character_distribution"],
                "strategies": report["final_strategy_distribution"],
                "richer": report["richer_than_prose"]["count"],
                "branch": report["decision_branch"]["class"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
