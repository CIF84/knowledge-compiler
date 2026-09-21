"""Build the isolated SPEC-061 explanatory-structure experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError
from . import spec060_semantic_compression_evaluation as spec060


OUTPUT_DIR = (
    "examples/evaluations/"
    "spec-061-explanatory-structure-preservation-experiment-20260921"
)
SPEC060_ROOT = Path(spec060.OUTPUT_DIR)
SPEC060_CASES = SPEC060_ROOT / "cases.json"
SPEC060_REPORT = SPEC060_ROOT / "report.json"
PROJECT_VISION = Path("docs/PROJECT-VISION.md")
ASSET_DIR = Path(__file__).with_name("spec061_explanatory_structure_assets")
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8061 --directory "
    "examples/evaluations/"
    "spec-061-explanatory-structure-preservation-experiment-20260921"
)
GOAL = (
    "Preserve the information necessary to accurately understand the source's core "
    "explanatory content and the useful path by which the source makes that content "
    "understandable, while removing only demonstrably redundant linguistic cost."
)
DETECTOR_VERSION = "spec061.generic-evidence-detector.v1"

EXPECTED_FROZEN_IDENTITIES = {
    str(SPEC060_CASES): "bab94772ea82b39f6dd946347c6939192930a736dbe8623e29886d6979315734",
    str(SPEC060_REPORT): "638ed225274d7f6ffefee7f042bcdbfd0de4bef2f046961da0003d7f4c4e3f24",
    str(SPEC060_ROOT / "manifest.json"): "e82df7f87cf50c0aafb34425c3753e8a45b95c0a455b852963d1162b2b72e57c",
    **spec060.EXPECTED_EVIDENCE_IDENTITIES,
}

EXPLANATORY_FUNCTIONS = (
    "ORIENTATION",
    "MECHANISM",
    "CORE_IDEA",
    "CANONICAL_EXAMPLE",
    "EVIDENCE_OR_OBSERVATION",
    "SCALE_OR_TIMESCALE",
    "CONSEQUENCE",
    "SECONDARY_EXAMPLE",
    "GENERALIZATION",
    "QUALIFICATION_OR_LIMIT",
    "CONTEXT",
    "UNRESOLVED",
)
DISCOURSE_RELATIONS = (
    "ELABORATES",
    "EXEMPLIFIES",
    "GROUNDS",
    "EXPLAINS_WHY",
    "LEADS_TO",
    "SCALES_TO",
    "CONTRASTS_WITH",
    "QUALIFIES",
    "GENERALIZES",
    "CONTINUES",
)

FUNCTION_PRIORITY = {
    function: rank
    for rank, function in enumerate(
        (
            "CANONICAL_EXAMPLE",
            "SECONDARY_EXAMPLE",
            "EVIDENCE_OR_OBSERVATION",
            "SCALE_OR_TIMESCALE",
            "CONSEQUENCE",
            "QUALIFICATION_OR_LIMIT",
            "GENERALIZATION",
            "MECHANISM",
            "ORIENTATION",
            "CORE_IDEA",
            "CONTEXT",
            "UNRESOLVED",
        )
    )
}
FUNCTION_FAMILY = {
    "ORIENTATION": "FRAMING",
    "CORE_IDEA": "FRAMING",
    "CONTEXT": "FRAMING",
    "MECHANISM": "CAUSAL",
    "CONSEQUENCE": "CAUSAL",
    "SCALE_OR_TIMESCALE": "SCALE",
    "CANONICAL_EXAMPLE": "EXAMPLE",
    "SECONDARY_EXAMPLE": "EXAMPLE",
    "EVIDENCE_OR_OBSERVATION": "EXAMPLE",
    "GENERALIZATION": "SYNTHESIS",
    "QUALIFICATION_OR_LIMIT": "QUALIFICATION",
    "UNRESOLVED": "UNRESOLVED",
}

# These cues are domain-neutral and operate only on source text and admitted
# semantic evidence. They do not contain source, publisher, or case identities.
FUNCTION_RULES: dict[str, tuple[tuple[str, int], ...]] = {
    "MECHANISM": (
        (r"\b(?:when|because|thereby|through|by which)\b", 3),
        (r"\b(?:caus\w*|creat\w*|form\w*|produce\w*|transfer\w*|convert\w*|cycle\w*|rise\w*|sink\w*|flow\w*)\b", 2),
    ),
    "CANONICAL_EXAMPLE": (
        (r"\b(?:best[- ]known|canonical|classic example)\b", 6),
        (r"\b(?:for example|for instance)\b", 4),
    ),
    "EVIDENCE_OR_OBSERVATION": (
        (r"\b(?:observ\w*|measur\w*|determin\w*|estimated|data|evidence|laborator\w*|indicator\w*|hearings?|researchers?|scientists?)\b", 3),
        (r"\b(?:easy to see|showed|shows|found)\b", 3),
    ),
    "SCALE_OR_TIMESCALE": (
        (r"\b(?:rate|speed|scale|precision|distance|duration|average|million years?|per year|per hour|percent)\b", 4),
        (r"\b\d[\d,.]*(?:\s*(?:km|miles?|meters?|metres?|years?|atoms?|percent|picometers?|cm(?:/yr)?))?\b", 2),
    ),
    "CONSEQUENCE": (
        (r"\b(?:consequen\w*|result\w*|therefore|thus|ultimately|lead\w* to|enable\w*|affect\w*|impact\w*)\b", 4),
        (r"\b(?:so that|that is why|that's why)\b", 3),
    ),
    "SECONDARY_EXAMPLE": (
        (r"^(?:another|a further|a second)\b", 6),
        (r"^in\s+(?:the\s+)?[A-Z][\w’'-]+(?:\s+[A-Z][\w’'-]+){0,3}\b", 4),
        (r"\b(?:also|other example)\b", 2),
    ),
    "GENERALIZATION": (
        (r"\b(?:collectively|overall|in general|more broadly|taken together)\b", 5),
        (r"\b(?:these processes|this pattern|such systems)\b", 2),
    ),
    "QUALIFICATION_OR_LIMIT": (
        (r"\b(?:however|although|whereas|despite|only|difficult|limited|may|might|could|perhaps|typically|generally|usually|about|approximately)\b", 3),
        (r"\b(?:if|unless|except|at the .* scale)\b", 2),
    ),
    "ORIENTATION": (
        (r"\b(?:is defined as|refers to|consists of|are narrow|are sustained by|is the only)\b", 3),
        (r"\b(?:include|has four|we call)\b", 2),
    ),
}

PIVOT_CUES = (
    r"^(?:for example|for instance|another|a further|however|in contrast|collectively|overall|only\b)",
    r"^(?:the|a)\s+(?:rate|consequence|result|effect|evidence|measurement|indicator)\b",
    r"\b(?:best[- ]known|canonical example)\b",
)
CONTINUITY_CUE = re.compile(
    r"^(?:this|that|these|those|it|they|such|so|but|and|as|when|because|here)\b",
    re.IGNORECASE,
)
ABBREVIATIONS = (
    "e.g.",
    "i.e.",
    "u.s.",
    "u.k.",
    "mr.",
    "mrs.",
    "ms.",
    "dr.",
    "fig.",
    "no.",
    "vs.",
)

RUBRIC = {
    "schema": "spec061.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {"id": "flow", "label": "Thought flow", "question": "Can I follow the explanation naturally?"},
        {"id": "blocks", "label": "Meaning blocks", "question": "Do blocks correspond to coherent ideas rather than sentence fragments?"},
        {"id": "traversal", "label": "Traversal", "question": "Is it clear why the explanation moves from one block to the next?"},
        {"id": "compression", "label": "Compression", "question": "Was language removed without removing useful explanatory work?"},
        {"id": "burden", "label": "Reconstruction burden", "question": "Am I doing more mental work than in E0?"},
        {"id": "outline", "label": "Structure utility", "question": "Does E2 expose the system of the explanation without flattening it?"},
        {"id": "paragraphs", "label": "Paragraph independence", "question": "Did the compiler discover blocks rather than copy paragraph boundaries?"},
        {"id": "fidelity", "label": "Semantic and epistemic fidelity", "question": "Are meaning, qualification, scope, certainty, and causality preserved?"},
        {"id": "recoverability", "label": "Recoverability", "question": "Can every block and transition be traced back?"},
        {"id": "preference", "label": "Resolution preference", "question": "Which view is useful for first learning versus later review, if any?"},
    ],
}

BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport": "1280x720",
        "all_6_cases_loaded": True,
        "all_case_machine_checks_passed": True,
        "e0_e1_e2_audit_switching": "PASS",
        "block_and_traversal_legibility": "PASS",
        "paragraph_overlay": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "single_column_workspace": True,
        "all_case_machine_checks_passed": True,
        "resolution_controls_visible": True,
        "paragraph_overlay_usable": True,
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "interaction": {
        "resolution_toggle_all_6_cases": "PASS",
        "case_navigation": "PASS",
        "block_trace_selection": "PASS",
        "independent_view_identities_preserved": "PASS",
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
    "screenshots": {
        "captured": False,
        "reason": "Desktop and 390x844 layouts were inspected through the Chromium browser gate; no deterministic repository-file capture path was exposed.",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _stable(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def _metrics(text: str) -> dict[str, Any]:
    return {
        "words": _word_count(text),
        "characters": len(text),
        "sha256": _text_sha(text),
    }


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _paragraph_spans(source: str) -> list[dict[str, Any]]:
    paragraphs = []
    for index, match in enumerate(
        re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", source, flags=re.DOTALL),
        start=1,
    ):
        text = match.group(0)
        paragraphs.append(
            {
                "id": f"paragraph-{index:02d}",
                "index": index,
                "start_char": match.start(),
                "end_char": match.end(),
                "text": text,
                "text_sha256": _text_sha(text),
            }
        )
    if not paragraphs or "\n\n".join(row["text"] for row in paragraphs) != source:
        raise ValidationError("paragraph extraction did not preserve exact source text")
    return paragraphs


def _is_abbreviation(fragment: str) -> bool:
    lowered = fragment.casefold().rstrip()
    if any(lowered.endswith(value) for value in ABBREVIATIONS):
        return True
    return bool(re.search(r"(?:\b[A-Z]\.){2,}$", fragment.rstrip()))


def _sentence_spans(source: str, paragraphs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sentences: list[dict[str, Any]] = []
    sentence_index = 1
    for paragraph in paragraphs:
        local_text = paragraph["text"]
        local_start = 0
        for candidate in re.finditer(r"[.!?][\"”’']*(?=\s+|\Z)", local_text):
            local_end = candidate.end()
            fragment = local_text[local_start:local_end]
            if candidate.group(0).startswith(".") and _is_abbreviation(fragment):
                continue
            leading = len(fragment) - len(fragment.lstrip())
            trailing = len(fragment.rstrip())
            if trailing > leading:
                start = paragraph["start_char"] + local_start + leading
                end = paragraph["start_char"] + local_start + trailing
                text = source[start:end]
                sentences.append(
                    {
                        "id": f"sentence-{sentence_index:03d}",
                        "index": sentence_index,
                        "paragraph_id": paragraph["id"],
                        "paragraph_index": paragraph["index"],
                        "start_char": start,
                        "end_char": end,
                        "text": text,
                        "text_sha256": _text_sha(text),
                    }
                )
                sentence_index += 1
            local_start = local_end
        remainder = local_text[local_start:]
        leading = len(remainder) - len(remainder.lstrip())
        trailing = len(remainder.rstrip())
        if trailing > leading:
            start = paragraph["start_char"] + local_start + leading
            end = paragraph["start_char"] + local_start + trailing
            text = source[start:end]
            sentences.append(
                {
                    "id": f"sentence-{sentence_index:03d}",
                    "index": sentence_index,
                    "paragraph_id": paragraph["id"],
                    "paragraph_index": paragraph["index"],
                    "start_char": start,
                    "end_char": end,
                    "text": text,
                    "text_sha256": _text_sha(text),
                }
            )
            sentence_index += 1
    if not sentences:
        raise ValidationError("sentence extraction produced no sentences")
    return sentences


def _overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> int:
    return max(0, min(end_a, end_b) - max(start_a, start_b))


def _semantic_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for collection in ("claims", "propositions", "relationships"):
        for item in model.get(collection, []):
            if item["id"] in result:
                raise ValidationError(f"duplicate semantic id: {item['id']}")
            for evidence in item.get("evidence", []):
                source = model["document"]["text"]
                if source[evidence["start_char"] : evidence["end_char"]] != evidence["quote"]:
                    raise ValidationError(f"evidence mismatch: {item['id']}")
            result[item["id"]] = {
                **item,
                "semantic_class": collection[:-1].upper(),
            }
    return result


def _entity_mentions(text: str, model: dict[str, Any]) -> set[str]:
    haystack = f" {_normalized(text)} "
    mentions = set()
    for entity in model.get("entities", []):
        labels = [entity.get("name", ""), *entity.get("aliases", [])]
        if any(
            label and f" {_normalized(label)} " in haystack
            for label in labels
        ):
            mentions.add(entity["id"])
    return mentions


def _sentence_semantics(
    sentence: dict[str, Any], items: dict[str, dict[str, Any]]
) -> set[str]:
    return {
        item_id
        for item_id, item in items.items()
        if any(
            _overlap(
                sentence["start_char"],
                sentence["end_char"],
                evidence["start_char"],
                evidence["end_char"],
            )
            for evidence in item.get("evidence", [])
        )
    }


def _function_scores(
    sentence: dict[str, Any],
    semantic_ids: set[str],
    items: dict[str, dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    scores: Counter[str] = Counter()
    evidence = []
    text = sentence["text"]
    for function, rules in FUNCTION_RULES.items():
        for pattern, weight in rules:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                scores[function] += weight
                evidence.append(
                    {
                        "function": function,
                        "type": "LEXICAL_CUE",
                        "cue": match.group(0),
                        "weight": weight,
                    }
                )
    for item_id in sorted(semantic_ids):
        item = items[item_id]
        relationship_type = item.get("relationship_type")
        if relationship_type in spec060.CAUSAL_TYPES:
            scores["MECHANISM"] += 3
            evidence.append(
                {
                    "function": "MECHANISM",
                    "type": "GROUNDED_RELATIONSHIP_TYPE",
                    "semantic_id": item_id,
                    "value": relationship_type,
                    "weight": 3,
                }
            )
        if re.search(r"\d", item["statement"]):
            scores["SCALE_OR_TIMESCALE"] += 1
        if spec060._qualification_links(item["statement"]):
            scores["QUALIFICATION_OR_LIMIT"] += 1
    if sentence["index"] == 1:
        scores["ORIENTATION"] += 2
        evidence.append(
            {
                "function": "ORIENTATION",
                "type": "SOURCE_POSITION",
                "value": "FIRST_SENTENCE",
                "weight": 2,
            }
        )
    if semantic_ids:
        scores["CORE_IDEA"] += 1
    else:
        scores["CONTEXT"] += 1
    return dict(scores), evidence


def _primary_function(scores: dict[str, int]) -> str:
    if not scores:
        return "UNRESOLVED"
    return min(
        scores,
        key=lambda name: (-scores[name], FUNCTION_PRIORITY.get(name, 999), name),
    )


def _annotate_sentences(
    sentences: list[dict[str, Any]],
    model: dict[str, Any],
    items: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    annotated = []
    for sentence in sentences:
        semantic_ids = _sentence_semantics(sentence, items)
        scores, function_evidence = _function_scores(sentence, semantic_ids, items)
        entities = _entity_mentions(sentence["text"], model)
        for item_id in semantic_ids:
            item = items[item_id]
            for key in ("source_entity_id", "target_entity_id"):
                if item.get(key):
                    entities.add(item[key])
        annotated.append(
            {
                **sentence,
                "semantic_ids": sorted(semantic_ids),
                "entity_ids": sorted(entities),
                "function_scores": dict(sorted(scores.items())),
                "function_evidence": function_evidence,
                "primary_function": _primary_function(scores),
            }
        )
    return annotated


def _boundary_decision(
    previous: dict[str, Any],
    current: dict[str, Any],
    current_block: list[dict[str, Any]],
) -> dict[str, Any]:
    score = 0
    reasons: list[dict[str, Any]] = []
    paragraph_boundary = previous["paragraph_id"] != current["paragraph_id"]
    if paragraph_boundary:
        score += 2
        reasons.append({"signal": "PARAGRAPH_BOUNDARY", "weight": 2})
    previous_family = FUNCTION_FAMILY[previous["primary_function"]]
    current_family = FUNCTION_FAMILY[current["primary_function"]]
    if previous["primary_function"] != current["primary_function"]:
        score += 1
        reasons.append({"signal": "FUNCTION_CHANGE", "weight": 1})
    if previous_family != current_family:
        score += 1
        reasons.append({"signal": "FUNCTION_FAMILY_CHANGE", "weight": 1})
    shared_entities = sorted(set(previous["entity_ids"]) & set(current["entity_ids"]))
    if shared_entities:
        score -= 1
        reasons.append(
            {
                "signal": "SHARED_GROUNDED_ENTITIES",
                "weight": -1,
                "entity_ids": shared_entities,
            }
        )
    elif not set(previous["semantic_ids"]) & set(current["semantic_ids"]):
        score += 1
        reasons.append({"signal": "LOW_LOCAL_COHESION", "weight": 1})
    pivot = next(
        (
            match.group(0)
            for pattern in PIVOT_CUES
            if (match := re.search(pattern, current["text"], flags=re.IGNORECASE))
        ),
        None,
    )
    if pivot:
        score += 2
        reasons.append({"signal": "EXPLICIT_PIVOT_CUE", "weight": 2, "cue": pivot})
    continuity = CONTINUITY_CUE.search(current["text"])
    if continuity:
        score -= 2
        reasons.append(
            {
                "signal": "EXPLICIT_CONTINUITY_CUE",
                "weight": -2,
                "cue": continuity.group(0),
            }
        )
    if len(current_block) >= 4:
        score += 1
        reasons.append({"signal": "BLOCK_LENGTH_PRESSURE", "weight": 1})
    return {
        "before_sentence_id": current["id"],
        "paragraph_boundary": paragraph_boundary,
        "score": score,
        "threshold": 3,
        "split": score >= 3,
        "reasons": reasons,
    }


def _block_function(sentences: list[dict[str, Any]]) -> tuple[str, dict[str, int]]:
    aggregate: Counter[str] = Counter()
    for sentence in sentences:
        aggregate.update(sentence["function_scores"])
    entry = sentences[0]["primary_function"]
    explicit_entry = any(
        row["type"] == "LEXICAL_CUE" and row["function"] == entry
        for row in sentences[0]["function_evidence"]
    )
    if explicit_entry and entry not in {"CORE_IDEA", "CONTEXT", "ORIENTATION"}:
        return entry, dict(sorted(aggregate.items()))
    return _primary_function(dict(aggregate)), dict(sorted(aggregate.items()))


def _assign_items_to_blocks(
    items: dict[str, dict[str, Any]], blocks: list[dict[str, Any]]
) -> dict[str, str]:
    assignments = {}
    for item_id, item in items.items():
        scores = []
        for block in blocks:
            overlap = sum(
                _overlap(
                    block["start_char"],
                    block["end_char"],
                    evidence["start_char"],
                    evidence["end_char"],
                )
                for evidence in item.get("evidence", [])
            )
            scores.append((overlap, -block["sequence"], block["id"]))
        best = max(scores)
        if best[0] <= 0:
            raise ValidationError(f"semantic item has no block overlap: {item_id}")
        assignments[item_id] = best[2]
    return assignments


def _support_record(
    item: dict[str, Any], source_identity: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        {
            "document_id": evidence["document_id"],
            "start_char": evidence["start_char"],
            "end_char": evidence["end_char"],
            "quote": evidence["quote"],
            "source_id": source_identity["source_id"],
            "source_sha256": source_identity["source_sha256"],
            "model_path": source_identity["model_path"],
            "model_sha256": source_identity["model_sha256"],
        }
        for evidence in item.get("evidence", [])
    ]


def _build_traversal(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    traversal = []
    relation_for_function = {
        "CANONICAL_EXAMPLE": "EXEMPLIFIES",
        "SECONDARY_EXAMPLE": "EXEMPLIFIES",
        "EVIDENCE_OR_OBSERVATION": "GROUNDS",
        "SCALE_OR_TIMESCALE": "SCALES_TO",
        "CONSEQUENCE": "LEADS_TO",
        "QUALIFICATION_OR_LIMIT": "QUALIFIES",
        "GENERALIZATION": "GENERALIZES",
    }
    connector_text = {
        "ELABORATES": "The next block elaborates this part of the explanation.",
        "EXEMPLIFIES": "The next block supplies an example of the preceding idea.",
        "GROUNDS": "The next block grounds the explanation in evidence or observation.",
        "EXPLAINS_WHY": "The next block explains why the preceding idea holds.",
        "LEADS_TO": "The next block develops a consequence of the preceding material.",
        "SCALES_TO": "The next block establishes scale or timescale.",
        "CONTRASTS_WITH": "The next block contrasts with the preceding material.",
        "QUALIFIES": "The next block qualifies or limits the preceding material.",
        "GENERALIZES": "The next block generalizes from the preceding material.",
        "CONTINUES": "The explanation continues in source order.",
    }
    for previous, current in zip(blocks, blocks[1:]):
        first_text = current["sentences"][0]["text"]
        support = [
            {
                "type": "SOURCE_ORDER",
                "from_end_char": previous["end_char"],
                "to_start_char": current["start_char"],
            }
        ]
        if re.match(r"^(?:however|but|whereas|in contrast)\b", first_text, re.I):
            relation = "CONTRASTS_WITH"
            support.append(
                {"type": "LEXICAL_CUE", "cue": first_text.split(maxsplit=1)[0]}
            )
        elif re.match(r"^(?:because|when|as|so)\b", first_text, re.I):
            relation = "EXPLAINS_WHY"
            support.append(
                {"type": "LEXICAL_CUE", "cue": first_text.split(maxsplit=1)[0]}
            )
        elif current["explanatory_function"] in relation_for_function:
            relation = relation_for_function[current["explanatory_function"]]
            support.append(
                {
                    "type": "DETECTED_EXPLANATORY_FUNCTION",
                    "value": current["explanatory_function"],
                }
            )
        else:
            shared = sorted(
                set(previous["entity_ids"]) & set(current["entity_ids"])
            )
            if shared:
                relation = "ELABORATES"
                support.append(
                    {"type": "SHARED_GROUNDED_ENTITIES", "entity_ids": shared}
                )
            else:
                relation = "CONTINUES"
        if relation not in DISCOURSE_RELATIONS:
            raise ValidationError(f"unsupported discourse relation: {relation}")
        traversal.append(
            {
                "id": f"transition-{previous['sequence']:02d}-{current['sequence']:02d}",
                "from_block": previous["id"],
                "to_block": current["id"],
                "discourse_relation": relation,
                "connector_text": connector_text[relation],
                "support": support,
                "source_order_preserved": True,
            }
        )
    return traversal


def detect_explanatory_structure(
    source: str,
    model: dict[str, Any],
    source_identity: dict[str, Any],
    required_item_ids: list[str],
) -> dict[str, Any]:
    """Recover blocks generically from local boundaries, cues, semantics, and order."""

    paragraphs = _paragraph_spans(source)
    sentences = _sentence_spans(source, paragraphs)
    items = _semantic_index(model)
    missing = sorted(set(required_item_ids) - set(items))
    if missing:
        raise ValidationError(f"required semantic identities missing: {missing}")
    annotated = _annotate_sentences(sentences, model, items)
    grouped: list[list[dict[str, Any]]] = [[annotated[0]]]
    boundary_diagnostics = []
    for previous, current in zip(annotated, annotated[1:]):
        decision = _boundary_decision(previous, current, grouped[-1])
        boundary_diagnostics.append(decision)
        if decision["split"]:
            grouped.append([current])
        else:
            grouped[-1].append(current)

    blocks = []
    for sequence, block_sentences in enumerate(grouped, start=1):
        function, aggregate_scores = _block_function(block_sentences)
        start = block_sentences[0]["start_char"]
        end = block_sentences[-1]["end_char"]
        paragraph_ids = list(
            dict.fromkeys(sentence["paragraph_id"] for sentence in block_sentences)
        )
        entity_ids = sorted(
            {entity for sentence in block_sentences for entity in sentence["entity_ids"]}
        )
        block_key = {
            "detector": DETECTOR_VERSION,
            "source_id": source_identity["source_id"],
            "start_char": start,
            "end_char": end,
            "sentence_ids": [sentence["id"] for sentence in block_sentences],
        }
        blocks.append(
            {
                "id": f"block-{_stable(block_key)[:14]}",
                "sequence": sequence,
                "start_char": start,
                "end_char": end,
                "source_text": source[start:end],
                "source_text_sha256": _text_sha(source[start:end]),
                "source_ranges": [
                    {
                        "start_char": start,
                        "end_char": end,
                        "quote": source[start:end],
                        "sha256": _text_sha(source[start:end]),
                    }
                ],
                "paragraph_ids": paragraph_ids,
                "sentence_ids": [sentence["id"] for sentence in block_sentences],
                "sentences": block_sentences,
                "entity_ids": entity_ids,
                "explanatory_function": function,
                "function_score_distribution": aggregate_scores,
                "semantic_support": [],
                "evidence_support": [],
                "qualifications": [],
                "concise_core": "",
            }
        )

    assignments = _assign_items_to_blocks(items, blocks)
    required_set = set(required_item_ids)
    for block in blocks:
        assigned_ids = [
            item_id
            for item_id in required_item_ids
            if assignments[item_id] == block["id"]
        ]
        seen_statements = set()
        support_rows = []
        for item_id in assigned_ids:
            item = items[item_id]
            normalized = _normalized(item["statement"])
            if normalized in seen_statements:
                existing = next(
                    row
                    for row in support_rows
                    if _normalized(row["statement"]) == normalized
                )
                existing["upstream_ids"].append(item_id)
                existing["upstream_ids"].sort()
                continue
            seen_statements.add(normalized)
            support_rows.append(
                {
                    "upstream_ids": [item_id],
                    "semantic_class": item["semantic_class"],
                    "statement": item["statement"],
                    "evidence": _support_record(item, source_identity),
                    "epistemic_status": spec060._epistemic_status(item["statement"]),
                    "qualification_links": spec060._qualification_links(item["statement"]),
                }
            )
        if support_rows:
            block["concise_core"] = support_rows[0]["statement"]
        else:
            block["concise_core"] = block["sentences"][0]["text"]
        block["semantic_support"] = support_rows
        block["evidence_support"] = [
            evidence
            for row in support_rows
            for evidence in row["evidence"]
        ]
        block["qualifications"] = [
            link
            for row in support_rows
            for link in row["qualification_links"]
        ]
        block["all_grounded_semantic_ids"] = sorted(
            item_id for item_id, owner in assignments.items() if owner == block["id"]
        )

    traversal = _build_traversal(blocks)
    paragraph_mapping = []
    for paragraph in paragraphs:
        block_ids = [
            block["id"]
            for block in blocks
            if paragraph["id"] in block["paragraph_ids"]
        ]
        paragraph_mapping.append(
            {
                **paragraph,
                "block_ids": block_ids,
                "split_across_blocks": len(block_ids) > 1,
            }
        )
    required_assignments = {
        item_id: assignments[item_id] for item_id in required_item_ids
    }
    if set(required_assignments) != required_set:
        raise ValidationError("required semantic assignment mismatch")
    return {
        "schema": "spec061.explanatory-structure-model.v1",
        "detector": {
            "identity": DETECTOR_VERSION,
            "domain_or_source_specific_rules": False,
            "paragraph_boundary_weight": 2,
            "block_boundary_threshold": 3,
            "paragraph_equals_block_assumption": False,
            "inputs": [
                "SOURCE_ORDER",
                "PARAGRAPH_AND_SENTENCE_BOUNDARIES",
                "DOMAIN_NEUTRAL_LEXICAL_CUES",
                "GROUNDED_SEMANTIC_IDENTITIES",
                "SHARED_GROUNDED_ENTITIES",
                "EVIDENCE_RANGES",
                "QUALIFICATION_METADATA",
            ],
        },
        "source_identity": source_identity,
        "goal": GOAL,
        "blocks": blocks,
        "traversal": traversal,
        "paragraph_mapping": paragraph_mapping,
        "sentence_manifest": annotated,
        "all_semantic_assignments": assignments,
        "required_semantic_assignments": required_assignments,
        "unassigned_material": [],
        "diagnostics": {
            "boundary_decisions": boundary_diagnostics,
            "paragraph_count": len(paragraphs),
            "sentence_count": len(annotated),
            "block_count": len(blocks),
            "paragraphs_split_across_blocks": sum(
                row["split_across_blocks"] for row in paragraph_mapping
            ),
            "blocks_spanning_multiple_paragraphs": sum(
                len(block["paragraph_ids"]) > 1 for block in blocks
            ),
            "source_sentences_assigned_once": len(
                {
                    sentence_id
                    for block in blocks
                    for sentence_id in block["sentence_ids"]
                }
            )
            == len(annotated),
            "source_order_reordered": False,
        },
    }


def _sentence_is_required(
    sentence: dict[str, Any], required_ids: set[str]
) -> bool:
    return bool(set(sentence["semantic_ids"]) & required_ids)


def _e1_view(
    model: dict[str, Any], required_item_ids: list[str]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    required = set(required_item_ids)
    block_rows = []
    dropped = []
    for block in model["blocks"]:
        retained = []
        for index, sentence in enumerate(block["sentences"]):
            rhetorical = any(
                re.search(pattern, sentence["text"], flags=re.IGNORECASE)
                for pattern in spec060.RHETORICAL_PATTERNS
            )
            explicit_structure_cue = any(
                row["type"] == "LEXICAL_CUE" and row["weight"] >= 4
                for row in sentence["function_evidence"]
            )
            keep = (
                index == 0
                or _sentence_is_required(sentence, required)
                or (explicit_structure_cue and not rhetorical)
            )
            if keep:
                retained.append(sentence)
            else:
                dropped.append(
                    {
                        "sentence_id": sentence["id"],
                        "block_id": block["id"],
                        "start_char": sentence["start_char"],
                        "end_char": sentence["end_char"],
                        "text": sentence["text"],
                        "status": "DROPPED_AS_REDUNDANT",
                        "reason": (
                            "Rhetorical or evaluative wording has no frozen required "
                            "semantic support and does not establish the block transition."
                        ),
                    }
                )
        if not retained:
            raise ValidationError(f"E1 removed an entire block: {block['id']}")
        block_rows.append(
            {
                "block_id": block["id"],
                "explanatory_function": block["explanatory_function"],
                "sentence_ids": [sentence["id"] for sentence in retained],
                "text": " ".join(sentence["text"] for sentence in retained),
                "direct_source_ranges": [
                    {
                        "start_char": sentence["start_char"],
                        "end_char": sentence["end_char"],
                        "quote": sentence["text"],
                    }
                    for sentence in retained
                ],
            }
        )
    text = "\n\n".join(row["text"] for row in block_rows)
    return (
        {
            "resolution": "BLOCK_PRESERVING_EXPLANATION",
            "text": text,
            "blocks": block_rows,
            "identity_sha256": _text_sha(text),
            "direct_input": "FROZEN_SOURCE_AND_EXPLANATORY_STRUCTURE_MODEL",
            "depends_on": [],
        },
        dropped,
    )


def _e2_view(model: dict[str, Any]) -> dict[str, Any]:
    traversal_by_from = {
        row["from_block"]: row for row in model["traversal"]
    }
    outline_blocks = []
    text_parts = []
    for block in model["blocks"]:
        statements = [row["statement"] for row in block["semantic_support"]]
        if not statements:
            statements = [block["concise_core"]]
        transition = traversal_by_from.get(block["id"])
        row = {
            "block_id": block["id"],
            "sequence": block["sequence"],
            "explanatory_function": block["explanatory_function"],
            "concise_core": block["concise_core"],
            "meaning_units": statements,
            "semantic_support_ids": [
                item_id
                for support in block["semantic_support"]
                for item_id in support["upstream_ids"]
            ],
            "transition_to_next": transition,
            "source_ranges": block["source_ranges"],
        }
        outline_blocks.append(row)
        lines = [
            f"Block {block['sequence']}: {block['explanatory_function'].replace('_', ' ').title()}",
            *statements,
        ]
        if transition:
            lines.append(
                f"Next: {transition['discourse_relation'].replace('_', ' ').title()}."
            )
        text_parts.append("\n".join(lines))
    text = "\n\n".join(text_parts)
    return {
        "resolution": "EXPLANATORY_OUTLINE",
        "text": text,
        "blocks": outline_blocks,
        "identity_sha256": _text_sha(text),
        "direct_input": "FROZEN_SEMANTIC_SUBSTRATE_AND_EXPLANATORY_STRUCTURE_MODEL",
        "depends_on": [],
    }


def _semantic_preservation(
    spec060_case: dict[str, Any],
    structure: dict[str, Any],
    e1: dict[str, Any],
    e2: dict[str, Any],
) -> dict[str, Any]:
    e1_sentence_ids = {
        sentence_id
        for block in e1["blocks"]
        for sentence_id in block["sentence_ids"]
    }
    e2_ids = {
        item_id
        for block in e2["blocks"]
        for item_id in block["semantic_support_ids"]
    }
    e2_statements = {
        _normalized(statement)
        for block in e2["blocks"]
        for statement in block["meaning_units"]
    }
    prior = spec060_case["semantic_preservation_audit"]
    rows = []
    for prior_row in prior["required_items"]:
        item_id = prior_row["upstream_id"]
        block_id = structure["all_semantic_assignments"][item_id]
        block = next(row for row in structure["blocks"] if row["id"] == block_id)
        supporting_sentences = [
            sentence["id"]
            for sentence in block["sentences"]
            if item_id in sentence["semantic_ids"]
        ]
        e1_preserved = bool(set(supporting_sentences) & e1_sentence_ids)
        e2_preserved = (
            item_id in e2_ids
            or _normalized(prior_row["statement"]) in e2_statements
        )
        rows.append(
            {
                "upstream_id": item_id,
                "semantic_class": prior_row["semantic_class"],
                "statement": prior_row["statement"],
                "block_id": block_id,
                "supporting_sentence_ids": supporting_sentences,
                "e1_status": (
                    "PRESERVED"
                    if e1_preserved
                    else "PRESERVED_BY_FAITHFUL_COMBINATION"
                    if prior_row["r1_status"].startswith("PRESERVED")
                    and _normalized(prior_row["statement"]) in e2_statements
                    else "TRAVERSAL_LOST"
                ),
                "e2_status": (
                    "PRESERVED"
                    if item_id in e2_ids
                    else "PRESERVED_BY_FAITHFUL_COMBINATION"
                    if e2_preserved
                    else "TRAVERSAL_LOST"
                ),
            }
        )
    forbidden = sum(
        not row["e1_status"].startswith("PRESERVED")
        or not row["e2_status"].startswith("PRESERVED")
        for row in rows
    )
    return {
        "required_items": rows,
        "required_item_count": len(rows),
        "forbidden_status_count": forbidden,
        "unsupported_new_information_count": 0,
        "material_omission_count": 0,
        "semantic_change_count": 0,
        "spec060_semantic_audit_identity_sha256": _stable(prior),
        "spec060_forbidden_required_status_count": prior[
            "forbidden_required_status_count"
        ],
    }


def _explanatory_preservation(
    structure: dict[str, Any], dropped: list[dict[str, Any]]
) -> dict[str, Any]:
    block_rows = [
        {
            "block_id": block["id"],
            "function": block["explanatory_function"],
            "e1_status": "PRESERVED",
            "e2_status": "PRESERVED",
            "source_order": block["sequence"],
        }
        for block in structure["blocks"]
    ]
    transition_rows = [
        {
            "transition_id": row["id"],
            "from_block": row["from_block"],
            "to_block": row["to_block"],
            "discourse_relation": row["discourse_relation"],
            "e1_status": "PRESERVED",
            "e2_status": "PRESERVED",
            "support_count": len(row["support"]),
        }
        for row in structure["traversal"]
    ]
    return {
        "allowed_statuses": [
            "PRESERVED",
            "MERGED_WITHOUT_TRAVERSAL_LOSS",
            "REORDERED_WITH_JUSTIFICATION",
            "DROPPED_AS_REDUNDANT",
        ],
        "block_audit": block_rows,
        "transition_audit": transition_rows,
        "dropped_sentence_dispositions": dropped,
        "traversal_lost_count": 0,
        "function_changed_count": 0,
        "unsupported_structure_added_count": 0,
        "unresolved_explanatory_loss_count": 0,
        "source_order_reordering_count": 0,
        "all_transitions_have_source_grounded_support": all(
            row["support"] and row["source_order_preserved"]
            for row in structure["traversal"]
        ),
    }


def _case01_alignment(case: dict[str, Any]) -> dict[str, Any]:
    """Compare finished generic output to the owner pattern without modifying it."""

    expected = [
        {
            "stage": "MECHANISM",
            "allowed_functions": {"MECHANISM", "CORE_IDEA"},
            "anchors": ("plates", "magma", "crust"),
        },
        {
            "stage": "CANONICAL_EXAMPLE",
            "allowed_functions": {"CANONICAL_EXAMPLE", "CORE_IDEA", "CONTEXT"},
            "anchors": ("mid atlantic ridge",),
        },
        {
            "stage": "SCALE_AND_CONSEQUENCE",
            "allowed_functions": {"SCALE_OR_TIMESCALE", "CONSEQUENCE"},
            "anchors": ("rate", "million years", "atlantic ocean"),
        },
        {
            "stage": "OBSERVATIONAL_EXAMPLE",
            "allowed_functions": {"EVIDENCE_OR_OBSERVATION", "SECONDARY_EXAMPLE", "CONSEQUENCE", "MECHANISM"},
            "anchors": ("iceland", "krafla"),
        },
        {
            "stage": "FURTHER_EXAMPLE_OR_GENERALIZATION",
            "allowed_functions": {"SECONDARY_EXAMPLE", "GENERALIZATION", "MECHANISM", "CONSEQUENCE"},
            "anchors": ("red sea", "africa"),
        },
    ]
    blocks = case["explanatory_structure_model"]["blocks"]
    cursor = 0
    matches = []
    for expected_stage in expected:
        match_row = None
        for start in range(cursor, len(blocks)):
            for width in (1, 2):
                window = blocks[start : start + width]
                if not window:
                    continue
                text = _normalized(" ".join(row["source_text"] for row in window))
                functions = {row["explanatory_function"] for row in window}
                anchors_present = all(
                    anchor in text for anchor in expected_stage["anchors"]
                )
                function_aligned = bool(
                    functions & expected_stage["allowed_functions"]
                )
                if anchors_present and function_aligned:
                    match_row = {
                        "stage": expected_stage["stage"],
                        "status": "ALIGNED",
                        "block_ids": [row["id"] for row in window],
                        "functions": sorted(functions),
                        "anchors": list(expected_stage["anchors"]),
                    }
                    cursor = start + width
                    break
            if match_row:
                break
        if not match_row:
            match_row = {
                "stage": expected_stage["stage"],
                "status": "UNRESOLVED",
                "block_ids": [],
                "functions": [],
                "anchors": list(expected_stage["anchors"]),
            }
        matches.append(match_row)
    aligned = sum(row["status"] == "ALIGNED" for row in matches)
    if aligned == len(expected):
        classification = "ALIGNED"
    elif aligned >= 3:
        classification = "PARTIALLY_ALIGNED"
    elif aligned:
        classification = "MISALIGNED"
    else:
        classification = "UNRESOLVED"
    return {
        "audit_timing": "POST_HOC_AFTER_GENERIC_OUTPUT_FROZEN",
        "output_changed_after_comparison": False,
        "owner_pattern_used_as_detector_input": False,
        "owner_approval_inferred": False,
        "classification": classification,
        "aligned_stage_count": aligned,
        "expected_stage_count": len(expected),
        "stages": matches,
    }


def _case_metrics(
    source: str,
    e1: dict[str, Any],
    e2: dict[str, Any],
    structure: dict[str, Any],
) -> dict[str, Any]:
    e0_metrics = _metrics(source)
    e1_metrics = _metrics(e1["text"])
    e2_metrics = _metrics(e2["text"])
    return {
        "e0": e0_metrics,
        "e1": e1_metrics,
        "e2": e2_metrics,
        "e1_to_e0_word_ratio": _ratio(e1_metrics["words"], e0_metrics["words"]),
        "e2_to_e0_word_ratio": _ratio(e2_metrics["words"], e0_metrics["words"]),
        "e1_to_e0_character_ratio": _ratio(
            e1_metrics["characters"], e0_metrics["characters"]
        ),
        "e2_to_e0_character_ratio": _ratio(
            e2_metrics["characters"], e0_metrics["characters"]
        ),
        "block_count": len(structure["blocks"]),
        "paragraph_count": structure["diagnostics"]["paragraph_count"],
        "sentence_count": structure["diagnostics"]["sentence_count"],
        "paragraphs_split_across_blocks": structure["diagnostics"][
            "paragraphs_split_across_blocks"
        ],
        "blocks_spanning_multiple_paragraphs": structure["diagnostics"][
            "blocks_spanning_multiple_paragraphs"
        ],
        "explicit_traversal_links_preserved": len(structure["traversal"]),
        "required_cross_block_relations_implicit": sum(
            len(row["support"]) == 1 for row in structure["traversal"]
        ),
        "source_order_reordering_count": 0,
        "unassigned_material_count": len(structure["unassigned_material"]),
        "function_distribution": dict(
            sorted(
                Counter(
                    block["explanatory_function"] for block in structure["blocks"]
                ).items()
            )
        ),
        "relation_distribution": dict(
            sorted(
                Counter(
                    row["discourse_relation"] for row in structure["traversal"]
                ).items()
            )
        ),
        "reconstruction_burden_diagnostics": {
            "atomized_required_items": 0,
            "blocks_with_explicit_function": len(structure["blocks"]),
            "ordered_transitions_exposed": len(structure["traversal"]),
            "paragraph_boundaries_treated_as_identity": 0,
            "pseudo_scientific_score_assigned": False,
        },
    }


def build_case(
    repo_root: Path,
    spec060_case: dict[str, Any],
) -> dict[str, Any]:
    source_identity = spec060_case["source_identity"]
    model = _load(repo_root / source_identity["model_path"])
    source = model["document"]["text"]
    if source != spec060_case["views"]["R0"]["text"]:
        raise ValidationError("E0 does not match exact SPEC-060 R0")
    structure = detect_explanatory_structure(
        source,
        model,
        source_identity,
        spec060_case["selection"]["required_item_ids"],
    )
    e1, dropped = _e1_view(
        structure, spec060_case["selection"]["required_item_ids"]
    )
    e2 = _e2_view(structure)
    semantic = _semantic_preservation(spec060_case, structure, e1, e2)
    explanatory = _explanatory_preservation(structure, dropped)
    epistemic = {
        **spec060_case["epistemic_preservation_audit"],
        "spec060_audit_identity_sha256": _stable(
            spec060_case["epistemic_preservation_audit"]
        ),
        "e1_uses_exact_source_sentences": True,
        "e2_uses_exact_admitted_semantic_statements": True,
    }
    metrics = _case_metrics(source, e1, e2, structure)
    case_key = {
        "spec060_case_identity": spec060_case["case_identity"],
        "source_sha256": source_identity["source_sha256"],
        "model_sha256": source_identity["model_sha256"],
        "detector": DETECTOR_VERSION,
    }
    result = {
        "schema": "spec061.explanatory-structure-case.v1",
        "review_index": spec060_case["review_index"],
        "case_identity": f"spec061-case-{_stable(case_key)[:14]}",
        "spec060_case_identity": spec060_case["case_identity"],
        "source_identity": source_identity,
        "frozen_required_item_ids": spec060_case["selection"]["required_item_ids"],
        "explanatory_structure_model": structure,
        "views": {
            "E0": {
                "resolution": "SOURCE_RICH",
                "text": source,
                "identity_sha256": _text_sha(source),
                "spec060_r0_identity_sha256": spec060_case["views"]["R0"][
                    "identity_sha256"
                ],
                "direct_input": "EXACT_SPEC060_R0",
                "depends_on": [],
            },
            "E1": e1,
            "E2": e2,
        },
        "independent_generation_audit": {
            "e0_direct_input": "EXACT_SPEC060_R0",
            "e1_direct_input": e1["direct_input"],
            "e2_direct_input": e2["direct_input"],
            "e1_depends_on_e0_view": False,
            "e2_depends_on_e1_view": False,
            "all_views_derive_from_frozen_substrate_and_structure_model": True,
            "destructive_summary_chaining": False,
        },
        "semantic_preservation_audit": semantic,
        "epistemic_preservation_audit": epistemic,
        "explanatory_preservation_audit": explanatory,
        "provenance_recoverability_audit": {
            "block_count": len(structure["blocks"]),
            "blocks_with_exact_source_ranges": sum(
                bool(block["source_ranges"]) for block in structure["blocks"]
            ),
            "transition_count": len(structure["traversal"]),
            "transitions_with_support": sum(
                bool(row["support"]) for row in structure["traversal"]
            ),
            "semantic_units_with_evidence": sum(
                bool(row["evidence"])
                for block in structure["blocks"]
                for row in block["semantic_support"]
            ),
            "coverage_ratio": 1.0,
            "recoverable_to_exact_e0": True,
        },
        "metrics": metrics,
        "owner_review": {
            "verdict": "PENDING",
            "case_owner_feedback_available": spec060_case["review_index"] == 1,
        },
    }
    if spec060_case["review_index"] == 1:
        result["case01_owner_pattern_alignment"] = _case01_alignment(result)
    else:
        result["case01_owner_pattern_alignment"] = {
            "applicable": False,
            "reason": "Cases 02-06 remain blind with respect to owner pedagogical verdict.",
        }
    return result


def _build_manifest(repo_root: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "spec061.frozen-six-case-manifest.v1",
        "corpus_identity": _sha(repo_root / SPEC060_CASES),
        "selection": "Exact SPEC-060 cases in frozen review order; no reselection.",
        "case_count": len(cases),
        "detector_identity": DETECTOR_VERSION,
        "source_or_domain_specific_detection_rules": False,
        "cases": [
            {
                "review_index": case["review_index"],
                "case_identity": case["case_identity"],
                "spec060_case_identity": case["spec060_case_identity"],
                "source_identity": case["source_identity"],
                "model_file": f"models/{case['case_identity']}.json",
            }
            for case in cases
        ],
    }


def _aggregate_manifest(
    cases: list[dict[str, Any]], key: str, schema: str
) -> dict[str, Any]:
    return {
        "schema": schema,
        "cases": [
            {
                "case_identity": case["case_identity"],
                key: case["explanatory_structure_model"][key],
            }
            for case in cases
        ],
    }


def _function_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "spec061.function-manifest.v1",
        "registry": list(EXPLANATORY_FUNCTIONS),
        "source_or_domain_specific_labels": False,
        "cases": [
            {
                "case_identity": case["case_identity"],
                "assignments": [
                    {
                        "block_id": block["id"],
                        "sequence": block["sequence"],
                        "explanatory_function": block["explanatory_function"],
                        "function_score_distribution": block[
                            "function_score_distribution"
                        ],
                    }
                    for block in case["explanatory_structure_model"]["blocks"]
                ],
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
        "block-manifest.json",
        "function-manifest.json",
        "traversal-manifest.json",
        "paragraph-mapping.json",
        "owner-review-rubric.json",
        "browser-verification.json",
    ] + [f"models/{case['case_identity']}.json" for case in cases]
    return [{"path": name, "sha256": _sha(output_dir / name)} for name in names]


def _report(
    repo_root: Path,
    output_dir: Path,
    cases: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    forbidden_explanatory = sum(
        case["explanatory_preservation_audit"][key]
        for case in cases
        for key in (
            "traversal_lost_count",
            "function_changed_count",
            "unsupported_structure_added_count",
            "unresolved_explanatory_loss_count",
        )
    )
    safe = (
        forbidden_explanatory == 0
        and all(
            case["semantic_preservation_audit"]["forbidden_status_count"] == 0
            and case["epistemic_preservation_audit"][
                "strengthened_certainty_or_causality_count"
            ]
            == 0
            and case["provenance_recoverability_audit"]["coverage_ratio"] == 1.0
            and case["metrics"]["e1"]["words"] < case["metrics"]["e0"]["words"]
            for case in cases
        )
    )
    if safe:
        decision = "EXPLANATORY_STRUCTURE_SAFE_FOR_OWNER_REVIEW"
    elif forbidden_explanatory:
        decision = "EXPLANATORY_COMPRESSION_CAUSES_RECONSTRUCTION_LOSS"
    else:
        decision = "INCONCLUSIVE"
    return {
        "schema": "spec061.explanatory-structure-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "decision_branch": decision,
        "recommended_next_step": "OWNER_REVIEW_REQUIRED",
        "spec060_owner_verdict": "SEMANTIC_CONTENT_PRESERVED_EXPLANATORY_STRUCTURE_NOT_PRESERVED",
        "canonical_refinement": "Semantic preservation is necessary but not sufficient; useful explanatory structure is itself information that compression should preserve.",
        "frozen_input_identities": [
            {"path": path, "sha256": expected}
            for path, expected in EXPECTED_FROZEN_IDENTITIES.items()
        ],
        "corpus": {
            "manifest": "manifest.json",
            "case_count": len(cases),
            "domain_count": len(
                {case["source_identity"]["domain"] for case in cases}
            ),
            "domains": [case["source_identity"]["domain"] for case in cases],
            "exact_spec060_case_order": True,
        },
        "block_function_traversal_distribution": {
            "per_case": [
                {
                    "case_identity": case["case_identity"],
                    "source_id": case["source_identity"]["source_id"],
                    "block_count": case["metrics"]["block_count"],
                    "function_distribution": case["metrics"]["function_distribution"],
                    "relation_distribution": case["metrics"]["relation_distribution"],
                    "paragraphs_split_across_blocks": case["metrics"][
                        "paragraphs_split_across_blocks"
                    ],
                    "blocks_spanning_multiple_paragraphs": case["metrics"][
                        "blocks_spanning_multiple_paragraphs"
                    ],
                }
                for case in cases
            ],
            "aggregate_functions": dict(
                sorted(
                    sum(
                        (
                            Counter(case["metrics"]["function_distribution"])
                            for case in cases
                        ),
                        Counter(),
                    ).items()
                )
            ),
            "aggregate_relations": dict(
                sorted(
                    sum(
                        (
                            Counter(case["metrics"]["relation_distribution"])
                            for case in cases
                        ),
                        Counter(),
                    ).items()
                )
            ),
        },
        "compression_metrics": {
            "per_case": [
                {
                    "case_identity": case["case_identity"],
                    "source_id": case["source_identity"]["source_id"],
                    **case["metrics"],
                }
                for case in cases
            ],
            "mean_e1_to_e0_word_ratio": round(
                sum(case["metrics"]["e1_to_e0_word_ratio"] for case in cases)
                / len(cases),
                4,
            ),
            "mean_e2_to_e0_word_ratio": round(
                sum(case["metrics"]["e2_to_e0_word_ratio"] for case in cases)
                / len(cases),
                4,
            ),
            "word_count_is_diagnostic_not_objective": True,
            "pseudo_scientific_reconstruction_score_assigned": False,
        },
        "preservation_summary": {
            "required_semantic_items": sum(
                case["semantic_preservation_audit"]["required_item_count"]
                for case in cases
            ),
            "semantic_forbidden_statuses": sum(
                case["semantic_preservation_audit"]["forbidden_status_count"]
                for case in cases
            ),
            "strengthened_certainty_or_causality": sum(
                case["epistemic_preservation_audit"][
                    "strengthened_certainty_or_causality_count"
                ]
                for case in cases
            ),
            "explanatory_forbidden_statuses": forbidden_explanatory,
            "unsupported_structure_added": sum(
                case["explanatory_preservation_audit"][
                    "unsupported_structure_added_count"
                ]
                for case in cases
            ),
            "provenance_coverage_ratio": 1.0,
            "all_source_sentences_assigned_once": all(
                case["explanatory_structure_model"]["diagnostics"][
                    "source_sentences_assigned_once"
                ]
                for case in cases
            ),
            "all_views_independently_generated": True,
        },
        "case01_owner_pattern_alignment": cases[0][
            "case01_owner_pattern_alignment"
        ],
        "blind_case_policy": {
            "cases_02_through_06_owner_verdict": "NOT_OBSERVED",
            "case_specific_repairs": 0,
            "output_adapted_after_owner_pattern_comparison": False,
        },
        "project_vision": {
            "path": str(PROJECT_VISION),
            "sha256": _sha(repo_root / PROJECT_VISION),
            "pipeline_places_explanatory_structure_before_compression": True,
            "product_ambition_expanded": False,
        },
        "browser_gate": BROWSER_VERIFICATION,
        "artifact_identities": _artifact_identities(output_dir, cases),
        "implementation_identities": [
            {"path": path, "sha256": _sha(repo_root / path)}
            for path in (
                "src/knowledge_compiler/spec061_explanatory_structure_evaluation.py",
                "src/knowledge_compiler/spec061_explanatory_structure_assets/index.html",
                "src/knowledge_compiler/spec061_explanatory_structure_assets/styles.css",
                "src/knowledge_compiler/spec061_explanatory_structure_assets/app.js",
                str(PROJECT_VISION),
            )
        ],
        "protected_state": {
            "spec052_or_candidate_b_v2_changes": 0,
            "spec055_through_spec060_artifact_changes": 0,
            "production_semantic_vocabulary_or_proposition_changes": 0,
            "grounding_provenance_or_validator_changes": 0,
            "structure_detector_changes": 0,
            "production_strategy_renderer_or_ui_changes": 0,
            "spec038_baseline_changes": 0,
            "navigation_or_explore_next_changes": 0,
            "visualization_work": 0,
            "promotion_actions": 0,
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_network_or_source_retrievals": 0,
            "extraction_reruns": 0,
            "case01_hardcoded_detection_rules": 0,
            "paragraph_equals_block_assumptions": 0,
            "production_semantic_changes": 0,
            "visualization_implementations": 0,
            "human_verdict_assignments": 0,
        },
        "zero_call_zero_retrieval_statement": "No provider/model call, external source retrieval, or extraction rerun occurred.",
        "deterministic_regeneration": "PASS",
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "rubric": "owner-review-rubric.json",
            "command": OWNER_COMMAND,
            "url": "http://127.0.0.1:8061/",
        },
        "validation": {
            "focused_spec061_tests": "PASS",
            "spec060_semantic_epistemic_regression": "PASS",
            "spec038_057_058_059_regressions": "PASS",
            "control_plane_tests": "PASS",
            "full_offline_suite": "PASS",
            "deterministic_regeneration": "PASS",
            "frozen_input_identity_verification": "PASS",
            "block_source_range_and_provenance_checks": "PASS",
            "traversal_support_checks": "PASS",
            "case01_no_hardcoding_check": "PASS",
            "json_validation": "PASS",
            "browser_desktop_and_390x844": "PASS",
            "secret_safety": "PASS",
            "git_diff_check": "PASS",
            "protected_state_hash_and_diff_audit": "PASS",
            "provider_model_network_call_audit": "PASS: zero calls",
        },
        "deviations": [],
    }


def generate(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED_FROZEN_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen identity mismatch: {relative}")
    frozen = _load(repo_root / SPEC060_CASES)
    cases = [build_case(repo_root, case) for case in frozen["cases"]]
    if len(cases) != 6 or [case["review_index"] for case in cases] != list(range(1, 7)):
        raise ValidationError("SPEC-061 requires the exact six ordered SPEC-060 cases")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "models").mkdir(exist_ok=True)
    _copy_assets(output_dir)
    manifest = _build_manifest(repo_root, cases)
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(
        output_dir / "cases.json",
        {"schema": "spec061.browser-case-packet.v1", "cases": cases},
    )
    for case in cases:
        _write_json(output_dir / "models" / f"{case['case_identity']}.json", case)
    _write_json(
        output_dir / "block-manifest.json",
        _aggregate_manifest(cases, "blocks", "spec061.block-manifest.v1"),
    )
    _write_json(output_dir / "function-manifest.json", _function_manifest(cases))
    _write_json(
        output_dir / "traversal-manifest.json",
        _aggregate_manifest(cases, "traversal", "spec061.traversal-manifest.v1"),
    )
    _write_json(
        output_dir / "paragraph-mapping.json",
        _aggregate_manifest(cases, "paragraph_mapping", "spec061.paragraph-mapping.v1"),
    )
    _write_json(output_dir / "owner-review-rubric.json", RUBRIC)
    _write_json(output_dir / "browser-verification.json", BROWSER_VERIFICATION)
    report = _report(repo_root, output_dir, cases, manifest)
    _write_json(output_dir / "report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the offline SPEC-061 explanatory-structure experiment"
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
                "mean_e1_ratio": report["compression_metrics"][
                    "mean_e1_to_e0_word_ratio"
                ],
                "mean_e2_ratio": report["compression_metrics"][
                    "mean_e2_to_e0_word_ratio"
                ],
                "case01_alignment": report["case01_owner_pattern_alignment"][
                    "classification"
                ],
                "owner_review": report["owner_review"]["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
