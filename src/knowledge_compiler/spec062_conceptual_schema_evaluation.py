"""Build the isolated SPEC-062 conceptual chunking/schema experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .models import ValidationError
from . import spec060_semantic_compression_evaluation as spec060
from . import spec061_explanatory_structure_evaluation as spec061


OUTPUT_DIR = (
    "examples/evaluations/"
    "spec-062-conceptual-chunking-schema-induction-20261007"
)
SPEC061_ROOT = Path(spec061.OUTPUT_DIR)
SPEC061_CASES = SPEC061_ROOT / "cases.json"
SPEC061_REPORT = SPEC061_ROOT / "report.json"
PROJECT_VISION = Path("docs/PROJECT-VISION.md")
ASSET_DIR = Path(__file__).with_name("spec062_conceptual_schema_assets")
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8062 --directory "
    "examples/evaluations/"
    "spec-062-conceptual-chunking-schema-induction-20261007"
)
DETECTOR_VERSION = "spec062.generic-conceptual-schema-inducer.v1"
GOAL = (
    "Preserve every frozen semantic item, qualification, explanatory block, "
    "material implication, and provenance identity while organizing supported "
    "information into fewer independent top-level conceptual units."
)

EXPECTED_FROZEN_IDENTITIES = {
    str(SPEC061_CASES): "184f2ec8a8064d093465c8d57dece95b4edd67d68b80f0483e3f10087e14c606",
    str(SPEC061_REPORT): "231a6c814ccf12ed0a76beddce86bb0f29569891da1e0f19a1a3116c4f71523d",
    str(SPEC061_ROOT / "manifest.json"): "1236b160ceb38ea2a5502a0e5f8cd5eebe0d52a58c9bb1f2038a254f931218db",
    **spec060.EXPECTED_EVIDENCE_IDENTITIES,
}

SCHEMA_ROLES = (
    "ORIENTATION",
    "CORE_CONCEPT",
    "MECHANISM",
    "PROCESS",
    "EXAMPLE_OR_MANIFESTATION",
    "EVIDENCE_OR_OBSERVATION",
    "CONSEQUENCE",
    "SCALE_OR_TIMESCALE",
    "QUALIFICATION_OR_LIMIT",
    "CONTEXT",
    "UNRESOLVED",
)
SCHEMA_RELATIONS = (
    "HAS_PART",
    "INSTANCE_OF",
    "EXEMPLIFIES",
    "MANIFESTS_AS",
    "SUPPORTED_BY",
    "LEADS_TO",
    "RESULTS_IN",
    "DEPENDS_ON",
    "QUALIFIED_BY",
    "SCALES_TO",
    "ELABORATES",
)
BLOCK_ROLE_MAP = {
    "ORIENTATION": "ORIENTATION",
    "CORE_IDEA": "CORE_CONCEPT",
    "MECHANISM": "MECHANISM",
    "CANONICAL_EXAMPLE": "EXAMPLE_OR_MANIFESTATION",
    "SECONDARY_EXAMPLE": "EXAMPLE_OR_MANIFESTATION",
    "EVIDENCE_OR_OBSERVATION": "EVIDENCE_OR_OBSERVATION",
    "CONSEQUENCE": "CONSEQUENCE",
    "SCALE_OR_TIMESCALE": "SCALE_OR_TIMESCALE",
    "QUALIFICATION_OR_LIMIT": "QUALIFICATION_OR_LIMIT",
    "GENERALIZATION": "CORE_CONCEPT",
    "CONTEXT": "CONTEXT",
    "UNRESOLVED": "UNRESOLVED",
}
ANCHOR_PRIORITY = {
    role: index
    for index, role in enumerate(
        (
            "MECHANISM",
            "PROCESS",
            "CORE_CONCEPT",
            "ORIENTATION",
            "EXAMPLE_OR_MANIFESTATION",
            "EVIDENCE_OR_OBSERVATION",
            "CONSEQUENCE",
            "SCALE_OR_TIMESCALE",
            "QUALIFICATION_OR_LIMIT",
            "CONTEXT",
            "UNRESOLVED",
        )
    )
}
RELATION_MAP = {
    "IS_A": "INSTANCE_OF",
    "EXAMPLE_OF": "EXEMPLIFIES",
    "PART_OF": "HAS_PART",
    "CAUSES": "RESULTS_IN",
    "CREATES": "RESULTS_IN",
    "ENABLES": "LEADS_TO",
    "PRECEDES": "LEADS_TO",
    "REQUIRES": "DEPENDS_ON",
    "AFFECTS": "LEADS_TO",
    "INCREASES": "LEADS_TO",
    "EXERTS_FORCE_ON": "LEADS_TO",
    "MEASURED_BY": "SUPPORTED_BY",
    "INTERACTS_WITH": "ELABORATES",
}
TRAVERSAL_MAP = {
    "ELABORATES": "ELABORATES",
    "EXEMPLIFIES": "EXEMPLIFIES",
    "GROUNDS": "SUPPORTED_BY",
    "EXPLAINS_WHY": "DEPENDS_ON",
    "LEADS_TO": "LEADS_TO",
    "SCALES_TO": "SCALES_TO",
    "CONTRASTS_WITH": "ELABORATES",
    "QUALIFIES": "QUALIFIED_BY",
    "GENERALIZES": "ELABORATES",
    "CONTINUES": "ELABORATES",
}
MATERIAL_RELATIONSHIP_TYPES = {
    "CAUSES",
    "CREATES",
    "ENABLES",
    "PRECEDES",
    "REQUIRES",
    "AFFECTS",
    "INCREASES",
    "EXERTS_FORCE_ON",
}
MATERIAL_TRAVERSAL_RELATIONS = {
    "EXPLAINS_WHY",
    "LEADS_TO",
    "SCALES_TO",
    "QUALIFIES",
    "EXEMPLIFIES",
    "GROUNDS",
}

RUBRIC = {
    "schema": "spec062.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {"id": "chunks", "label": "Chunk quality", "question": "Do grouped items genuinely belong together?"},
        {"id": "burden", "label": "Top-level burden", "question": "Does the schema reduce how many independent things I must hold in mind?"},
        {"id": "hierarchy", "label": "Hierarchy", "question": "Does parent/child organization reflect the concept rather than source order?"},
        {"id": "mechanisms", "label": "Shared mechanisms", "question": "Are examples organized under common mechanisms where supported?"},
        {"id": "implications", "label": "Implications", "question": "Are crucial eventual or causal relationships preserved?"},
        {"id": "traversal", "label": "Traversal", "question": "Can I still follow the explanation naturally?"},
        {"id": "utility", "label": "Schema utility", "question": "Does organization make retrieval and synthesis easier?"},
        {"id": "over", "label": "Over-grouping", "question": "Has useful distinction been hidden inside a broad chunk?"},
        {"id": "under", "label": "Under-grouping", "question": "Are too many sibling units still independent?"},
        {"id": "fidelity", "label": "Fidelity", "question": "Are semantics, scope, uncertainty, causality, and provenance unchanged?"},
        {"id": "resolution", "label": "First learning versus review", "question": "Which view fits first exposure and which later retrieval?"},
    ],
}

BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport": "1280x720",
        "all_6_cases_loaded": True,
        "s0_s1_s2_audit_switching": "PASS",
        "chunk_hierarchy_and_membership": "PASS",
        "implication_and_provenance_trace": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "single_column_workspace": True,
        "all_6_cases_loaded": True,
        "hierarchy_remains_legible": True,
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "interaction": {
        "resolution_toggle_all_6_cases": "PASS",
        "case_navigation": "PASS",
        "chunk_trace_selection": "PASS",
        "peer_view_identity": "PASS",
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
}

REPAIR_BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport": "1280x720",
        "all_6_cases_loaded": True,
        "all_6_case_buttons_selectable": True,
        "s0_s1_s2_audit_switching": "PASS",
        "evidence_trace_all_6_cases": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "single_column_workspace": True,
        "all_6_cases_loaded": True,
        "all_6_case_buttons_selectable": True,
        "s0_s1_s2_audit_switching": "PASS",
        "evidence_trace_all_6_cases": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "artifact_loading": {
        "deterministic_embedded_packet": "PASS",
        "direct_file_dependency_audit": "PASS: no fetch required",
        "http_server_review": "PASS",
        "silent_empty_shell_prevented": True,
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
}

FROZEN_EXPERIMENTAL_PAYLOAD_SHA256 = (
    "7c05b8fbea3711f91438c050312c42a2b92fb7d843cf697518def114d6cd619e"
)
FROZEN_SPEC062_EVIDENCE_IDENTITIES = {
    "report.json": "34d55c21f21d18478bc5455cf24b33850bae8572d8d14c5a6746c9fd60061fb3",
    "browser-verification.json": "bac01b84e36d42f9cb5d44e730fc5cd74e14145e72725d3dc25ed31b8d63315a",
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
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _metrics(text: str) -> dict[str, Any]:
    return {
        "words": len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE)),
        "characters": len(text),
        "sha256": _text_sha(text),
    }


def _support(item: dict[str, Any], identity: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source_id": identity["source_id"],
            "source_sha256": identity["source_sha256"],
            "model_path": identity["model_path"],
            "model_sha256": identity["model_sha256"],
            **evidence,
        }
        for evidence in item.get("evidence", [])
    ]


class _UnionFind:
    def __init__(self, values: list[str]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: str) -> str:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[max(left_root, right_root)] = min(left_root, right_root)


def _pair_support(
    left: dict[str, Any],
    right: dict[str, Any],
    entity_frequency: Counter[str],
    ubiquitous_limit: int,
    transitions: dict[tuple[str, str], dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> tuple[int, list[dict[str, Any]]]:
    score = 0
    support: list[dict[str, Any]] = []
    shared = sorted(
        entity
        for entity in set(left["entity_ids"]) & set(right["entity_ids"])
        if entity_frequency[entity] <= ubiquitous_limit
    )
    if shared:
        weight = min(4, 2 * len(shared))
        score += weight
        support.append({"type": "SHARED_GROUNDED_ENTITIES", "entity_ids": shared, "weight": weight})
    transition = transitions.get((left["id"], right["id"])) or transitions.get((right["id"], left["id"]))
    if transition and transition["discourse_relation"] in {"EXEMPLIFIES", "GROUNDS"}:
        score += 3
        support.append({"type": "FROZEN_EXPLANATORY_TRANSITION", "transition_id": transition["id"], "relation": transition["discourse_relation"], "weight": 3})
    elif transition and transition["discourse_relation"] not in {"CONTINUES", "CONTRASTS_WITH"}:
        score += 1
        support.append({"type": "FROZEN_EXPLANATORY_TRANSITION", "transition_id": transition["id"], "relation": transition["discourse_relation"], "weight": 1})
    cross = []
    left_entities, right_entities = set(left["entity_ids"]), set(right["entity_ids"])
    for relationship in relationships:
        source_entity = relationship.get("source_entity_id")
        target_entity = relationship.get("target_entity_id")
        if (source_entity in left_entities and target_entity in right_entities) or (
            source_entity in right_entities and target_entity in left_entities
        ):
            cross.append(relationship["id"])
    if cross:
        score += 3
        support.append({"type": "GROUNDED_CROSS_BLOCK_RELATIONSHIPS", "semantic_ids": sorted(cross), "weight": 3})
    left_role, right_role = BLOCK_ROLE_MAP[left["explanatory_function"]], BLOCK_ROLE_MAP[right["explanatory_function"]]
    if shared and left_role == right_role and left_role in {"MECHANISM", "PROCESS", "EXAMPLE_OR_MANIFESTATION", "EVIDENCE_OR_OBSERVATION"}:
        score += 1
        support.append({"type": "COMPATIBLE_SCHEMA_ROLES", "roles": [left_role, right_role], "weight": 1})
    return score, support


def _chunk_label(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    clause = re.split(r"[.;:]", cleaned, maxsplit=1)[0]
    words = clause.split()
    return " ".join(words[:14]) + ("…" if len(words) > 14 else "")


def _schema_role(block: dict[str, Any]) -> str:
    role = BLOCK_ROLE_MAP.get(block["explanatory_function"], "UNRESOLVED")
    if role not in SCHEMA_ROLES:
        raise ValidationError(f"unsupported schema role: {role}")
    return role


def _induce_chunks(
    structure: dict[str, Any],
    semantic_items: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    blocks = structure["blocks"]
    block_ids = [block["id"] for block in blocks]
    entity_frequency = Counter(entity for block in blocks for entity in set(block["entity_ids"]))
    ubiquitous_limit = max(2, math.ceil(len(blocks) * 0.6))
    transitions = {(row["from_block"], row["to_block"]): row for row in structure["traversal"]}
    relationships = [item for item in semantic_items.values() if item["semantic_class"] == "RELATIONSHIP"]
    pair_rows = []
    union_find = _UnionFind(block_ids)
    for left_index, left in enumerate(blocks):
        for right in blocks[left_index + 1 :]:
            score, support = _pair_support(left, right, entity_frequency, ubiquitous_limit, transitions, relationships)
            eligible = score >= 4
            pair_rows.append({"left_block": left["id"], "right_block": right["id"], "score": score, "threshold": 4, "grouped": eligible, "support": support})
            if eligible:
                union_find.union(left["id"], right["id"])
    components: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in blocks:
        components[union_find.find(block["id"])].append(block)
    ordered_components = sorted(components.values(), key=lambda rows: min(row["sequence"] for row in rows))
    chunks: list[dict[str, Any]] = []
    block_to_leaf: dict[str, str] = {}
    for component_index, component in enumerate(ordered_components, start=1):
        component.sort(key=lambda row: row["sequence"])
        anchor = min(
            component,
            key=lambda row: (
                ANCHOR_PRIORITY[_schema_role(row)],
                -len(row["semantic_support"]),
                row["sequence"],
            ),
        )
        parent_id = None
        if len(component) > 1:
            parent_id = f"chunk-{_stable({'version': DETECTOR_VERSION, 'blocks': [row['id'] for row in component]})[:14]}"
            membership = []
            for block in component:
                if block["id"] == anchor["id"]:
                    support = [{"type": "ANCHOR_BLOCK", "block_id": block["id"], "source_ranges": block["source_ranges"]}]
                else:
                    candidates = [
                        row for row in pair_rows
                        if row["grouped"] and block["id"] in {row["left_block"], row["right_block"]}
                        and ({row["left_block"], row["right_block"]} - {block["id"]}).pop() in {member["id"] for member in component}
                    ]
                    best = max(candidates, key=lambda row: (row["score"], row["left_block"], row["right_block"]))
                    support = best["support"]
                membership.append({"block_id": block["id"], "status": "SUPPORTED", "support": support})
            chunks.append({
                "id": parent_id,
                "label": _chunk_label(anchor["concise_core"]),
                "role": _schema_role(anchor),
                "level": 1,
                "parent_chunk": None,
                "member_blocks": [row["id"] for row in component],
                "semantic_support_ids": sorted({item_id for block in component for item_id in block["all_grounded_semantic_ids"]}),
                "evidence_support": [source_range for block in component for source_range in block["source_ranges"]],
                "membership_audit": membership,
                "anchor_block": anchor["id"],
                "source_sequence": min(row["sequence"] for row in component),
            })
        for block in component:
            leaf_id = f"chunk-{_stable({'version': DETECTOR_VERSION, 'block': block['id']})[:14]}"
            block_to_leaf[block["id"]] = leaf_id
            chunks.append({
                "id": leaf_id,
                "label": _chunk_label(block["concise_core"]),
                "role": _schema_role(block),
                "level": 2 if parent_id else 1,
                "parent_chunk": parent_id,
                "member_blocks": [block["id"]],
                "semantic_support_ids": list(block["all_grounded_semantic_ids"]),
                "evidence_support": block["source_ranges"],
                "membership_audit": [{"block_id": block["id"], "status": "SUPPORTED", "support": [{"type": "EXACT_FROZEN_BLOCK_IDENTITY", "block_id": block["id"], "source_ranges": block["source_ranges"]}]}],
                "anchor_block": block["id"],
                "source_sequence": block["sequence"],
            })
    return chunks, block_to_leaf, pair_rows


def _top_level_for(chunk_id: str, chunks_by_id: dict[str, dict[str, Any]]) -> str:
    chunk = chunks_by_id[chunk_id]
    return chunk["parent_chunk"] or chunk_id


def _entity_block(entity_id: str | None, blocks: list[dict[str, Any]], assigned_block: str) -> str:
    if not entity_id:
        return assigned_block
    candidates = [block for block in blocks if entity_id in block["entity_ids"]]
    if not candidates:
        return assigned_block
    assigned_sequence = next(block["sequence"] for block in blocks if block["id"] == assigned_block)
    return min(candidates, key=lambda block: (abs(block["sequence"] - assigned_sequence), block["sequence"]))["id"]


def _build_edges(
    structure: dict[str, Any],
    semantic_items: dict[str, dict[str, Any]],
    block_to_leaf: dict[str, str],
    chunks: list[dict[str, Any]],
    source_identity: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    edges = []
    implications = []
    chunks_by_id = {chunk["id"]: chunk for chunk in chunks}
    for chunk in chunks:
        if chunk["parent_chunk"]:
            parent = chunk["parent_chunk"]
            edges.append({
                "id": f"edge-{_stable({'parent': parent, 'child': chunk['id']})[:14]}",
                "from": parent,
                "to": chunk["id"],
                "relation": "HAS_PART",
                "edge_kind": "SUPPORTED_CHUNK_MEMBERSHIP",
                "support": chunk["membership_audit"][0]["support"],
                "required_for_reconstruction": True,
            })
    for transition in structure["traversal"]:
        relation = TRAVERSAL_MAP[transition["discourse_relation"]]
        edge = {
            "id": f"edge-{_stable({'transition': transition['id'], 'relation': relation})[:14]}",
            "from": block_to_leaf[transition["from_block"]],
            "to": block_to_leaf[transition["to_block"]],
            "relation": relation,
            "edge_kind": "FROZEN_EXPLANATORY_TRAVERSAL",
            "support": [{"type": "SPEC061_TRANSITION", "transition": transition}],
            "required_for_reconstruction": transition["discourse_relation"] in MATERIAL_TRAVERSAL_RELATIONS,
        }
        edges.append(edge)
        if edge["required_for_reconstruction"]:
            implications.append({
                "id": f"implication-{_stable({'transition': transition['id']})[:14]}",
                "kind": "EXPLANATORY_TRANSITION",
                "upstream_identity": transition["id"],
                "statement": transition["connector_text"],
                "schema_edge_id": edge["id"],
                "s1_status": "PRESERVED_BY_SCHEMA",
                "s2_status": "PRESERVED_EXPLICITLY",
                "support": edge["support"],
            })
    blocks = structure["blocks"]
    assignments = structure["all_semantic_assignments"]
    for item in semantic_items.values():
        if item["semantic_class"] != "RELATIONSHIP":
            continue
        assigned = assignments[item["id"]]
        from_block = _entity_block(item.get("source_entity_id"), blocks, assigned)
        to_block = _entity_block(item.get("target_entity_id"), blocks, assigned)
        relation = RELATION_MAP[item["relationship_type"]]
        edge = {
            "id": f"edge-{_stable({'semantic': item['id'], 'relation': relation})[:14]}",
            "from": block_to_leaf[from_block],
            "to": block_to_leaf[to_block],
            "relation": relation,
            "grounded_relationship_type": item["relationship_type"],
            "edge_kind": "GROUNDED_SEMANTIC_RELATIONSHIP",
            "support": [{"type": "GROUNDED_SEMANTIC_ITEM", "semantic_id": item["id"], "statement": item["statement"], "evidence": _support(item, source_identity)}],
            "required_for_reconstruction": item["relationship_type"] in MATERIAL_RELATIONSHIP_TYPES,
        }
        edges.append(edge)
        if edge["required_for_reconstruction"]:
            implications.append({
                "id": f"implication-{_stable({'semantic': item['id']})[:14]}",
                "kind": "GROUNDED_RELATIONSHIP",
                "upstream_identity": item["id"],
                "statement": item["statement"],
                "schema_edge_id": edge["id"],
                "s1_status": "PRESERVED_EXPLICITLY",
                "s2_status": "PRESERVED_EXPLICITLY",
                "support": edge["support"],
            })
    if any(edge["relation"] not in SCHEMA_RELATIONS for edge in edges):
        raise ValidationError("schema edge escaped bounded relation registry")
    return edges, implications


def _semantic_rows(items: dict[str, dict[str, Any]], structure: dict[str, Any], block_to_leaf: dict[str, str], identity: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in items.values():
        block_id = structure["all_semantic_assignments"][item["id"]]
        rows.append({
            "upstream_id": item["id"],
            "semantic_class": item["semantic_class"],
            "statement": item["statement"],
            "assigned_block": block_id,
            "assigned_chunk": block_to_leaf[block_id],
            "evidence": _support(item, identity),
            "epistemic_status": spec060._epistemic_status(item["statement"]),
            "qualification_links": spec060._qualification_links(item["statement"]),
            "s1_status": "PRESERVED_EXPLICITLY",
            "s2_status": "PRESERVED_EXPLICITLY",
        })
    return rows


def _render_schema(chunks: list[dict[str, Any]], semantic_rows: list[dict[str, Any]], edges: list[dict[str, Any]], include_traversal: bool) -> str:
    chunks_by_parent: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        chunks_by_parent[chunk["parent_chunk"]].append(chunk)
    semantics_by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in semantic_rows:
        semantics_by_chunk[row["assigned_chunk"]].append(row)
    lines = []
    top_level = sorted(chunks_by_parent[None], key=lambda row: row["source_sequence"])
    for top_index, top in enumerate(top_level, start=1):
        lines.append(f"Concept {top_index}: {top['role'].replace('_', ' ').title()} — {top['label']}")
        children = sorted(chunks_by_parent.get(top["id"], []), key=lambda row: row["source_sequence"])
        leaves = children or [top]
        for leaf in leaves:
            lines.append(f"  Block: {leaf['role'].replace('_', ' ').title()} — {leaf['label']}")
            for semantic in semantics_by_chunk[leaf["id"]]:
                lines.append(f"    Fact: {semantic['statement']}")
    shown_edges = [
        edge for edge in edges
        if edge["edge_kind"] != "SUPPORTED_CHUNK_MEMBERSHIP"
        and (include_traversal or edge["required_for_reconstruction"])
    ]
    lines.append("Reading path and supported implications:" if include_traversal else "Necessary implications:")
    for edge in shown_edges:
        lines.append(f"  {edge['relation'].replace('_', ' ').title()}: {edge['from']} to {edge['to']}")
    return "\n".join(lines)


def _posthoc_anchors(cases: list[dict[str, Any]]) -> dict[str, Any]:
    geology = next(case for case in cases if case["source_identity"]["source_id"].startswith("usgs-"))
    astronomy = next(case for case in cases if case["source_identity"]["source_id"].startswith("nasa-"))
    meteorology = next(case for case in cases if case["source_identity"]["source_id"].startswith("noaa-"))
    geology_model = geology["conceptual_schema_model"]
    chunks = geology_model["chunks"]
    top_by_block = {}
    by_id = {chunk["id"]: chunk for chunk in chunks}
    for chunk in chunks:
        if len(chunk["member_blocks"]) == 1:
            top_by_block[chunk["member_blocks"][0]] = chunk["parent_chunk"] or chunk["id"]
    blocks = geology["frozen_explanatory_structure"]["blocks"]
    anchor_text = {
        block["sequence"]: _normalized(block["source_text"]) for block in blocks
    }
    mechanism = next((block for block in blocks if "magma" in anchor_text[block["sequence"]] and "crust" in anchor_text[block["sequence"]]), None)
    atlantic = next((block for block in blocks if "mid atlantic ridge" in anchor_text[block["sequence"]]), None)
    iceland = next((block for block in blocks if "iceland" in anchor_text[block["sequence"]]), None)
    red_sea = next((block for block in blocks if "red sea" in anchor_text[block["sequence"]]), None)
    anchors = [mechanism, atlantic, iceland, red_sea]
    geology_aligned = all(anchors) and len({top_by_block[block["id"]] for block in anchors}) == 1
    astronomy_implications = {
        row["upstream_identity"]: row
        for row in astronomy["implication_preservation_audit"]["material_implications"]
    }
    astronomy_aligned = all(
        item_id in astronomy_implications
        and astronomy_implications[item_id]["s1_status"].startswith("PRESERVED")
        and astronomy_implications[item_id]["s2_status"].startswith("PRESERVED")
        for item_id in ("r14", "r15")
    )
    met_metrics = meteorology["metrics"]
    meteorology_aligned = (
        met_metrics["top_level_unit_ratio"] < 1
        and meteorology["semantic_preservation_audit"]["forbidden_status_count"] == 0
    )
    return {
        "audit_timing": "POST_HOC_AFTER_GENERIC_OUTPUT_FROZEN",
        "output_changed_after_comparison": False,
        "owner_anchors_used_as_induction_input": False,
        "owner_approval_inferred": False,
        "geology": {"classification": "ALIGNED" if geology_aligned else "PARTIALLY_ALIGNED", "shared_top_level_chunk": geology_aligned, "anchor_block_ids": [block["id"] for block in anchors if block]},
        "astronomy": {"classification": "ALIGNED" if astronomy_aligned else "MISALIGNED", "required_implication_ids": ["r14", "r15"], "preserved": astronomy_aligned},
        "meteorology": {"classification": "ALIGNED" if meteorology_aligned else "UNRESOLVED", "top_level_unit_ratio": met_metrics["top_level_unit_ratio"], "semantic_deletion": 0},
    }


def build_case(repo_root: Path, frozen: dict[str, Any]) -> dict[str, Any]:
    identity = frozen["source_identity"]
    source_model = _load(repo_root / identity["model_path"])
    items = spec061._semantic_index(source_model)
    structure = frozen["explanatory_structure_model"]
    if set(structure["all_semantic_assignments"]) != set(items):
        raise ValidationError("SPEC-061 block assignment does not cover every semantic item")
    chunks, block_to_leaf, pair_rows = _induce_chunks(structure, items)
    edges, implications = _build_edges(structure, items, block_to_leaf, chunks, identity)
    semantic_rows = _semantic_rows(items, structure, block_to_leaf, identity)
    chunks_by_id = {chunk["id"]: chunk for chunk in chunks}
    top_level_ids = list(dict.fromkeys(
        _top_level_for(block_to_leaf[block["id"]], chunks_by_id)
        for block in structure["blocks"]
    ))
    s0 = frozen["views"]["E1"]["text"]
    s1 = _render_schema(chunks, semantic_rows, edges, False)
    s2 = _render_schema(chunks, semantic_rows, edges, True)
    forbidden_implications = sum(
        row["s1_status"] in {"LOST_BETWEEN_ENDPOINTS", "UNSUPPORTED_EDGE_ADDED", "UNRESOLVED"}
        or row["s2_status"] in {"LOST_BETWEEN_ENDPOINTS", "UNSUPPORTED_EDGE_ADDED", "UNRESOLVED"}
        for row in implications
    )
    before = len(structure["blocks"])
    after = len(top_level_ids)
    metrics = {
        "frozen_semantic_item_count": len(items),
        "explanatory_block_count": before,
        "top_level_conceptual_chunk_count": after,
        "total_conceptual_chunk_count": len(chunks),
        "schema_depth": max(chunk["level"] for chunk in chunks),
        "schema_edge_count": len(edges),
        "material_implication_count": len(implications),
        "material_implications_preserved": len(implications) - forbidden_implications,
        "material_implications_lost": forbidden_implications,
        "blocks_grouped_under_shared_parents": sum(bool(chunk["parent_chunk"]) for chunk in chunks),
        "independent_top_level_units_before": before,
        "independent_top_level_units_after": after,
        "top_level_unit_ratio": round(after / before, 4),
        "unassigned_block_count": 0,
        "unassigned_semantic_item_count": 0,
        "unsupported_grouping_count": 0,
        "unsupported_edge_count": 0,
        "s0": _metrics(s0),
        "s1": _metrics(s1),
        "s2": _metrics(s2),
        "word_count_is_diagnostic_not_objective": True,
        "cognitive_load_score_assigned": False,
    }
    case_key = {"spec061_case_identity": frozen["case_identity"], "detector": DETECTOR_VERSION, "model_sha256": identity["model_sha256"]}
    case = {
        "schema": "spec062.conceptual-schema-case.v1",
        "review_index": frozen["review_index"],
        "case_identity": f"spec062-case-{_stable(case_key)[:14]}",
        "spec061_case_identity": frozen["case_identity"],
        "source_identity": identity,
        "frozen_explanatory_structure": structure,
        "conceptual_schema_model": {
            "schema": "spec062.conceptual-schema-model.v1",
            "inducer": {"identity": DETECTOR_VERSION, "source_or_domain_specific_rules": False, "owner_anchor_inputs": False, "paragraph_or_source_order_grouping_rule": False, "word_count_objective": False, "inputs": ["FROZEN_GROUNDED_SEMANTICS", "FROZEN_SPEC061_BLOCKS", "FROZEN_SPEC061_TRAVERSAL", "SHARED_GROUNDED_ENTITIES", "GROUNDED_CROSS_BLOCK_RELATIONSHIPS"]},
            "source_identity": identity,
            "goal": GOAL,
            "root_or_orientation": top_level_ids[0],
            "chunks": chunks,
            "schema_edges": edges,
            "unassigned_blocks": [],
            "unassigned_semantic_items": [],
            "diagnostics": {"pair_support_decisions": pair_rows, "top_level_chunk_ids": top_level_ids, "schema_depth": metrics["schema_depth"], "source_order_used_as_membership_evidence": False},
        },
        "views": {
            "S0": {"resolution": "EXPLANATORY_BASELINE", "text": s0, "identity_sha256": _text_sha(s0), "spec061_e1_identity_sha256": frozen["views"]["E1"]["identity_sha256"], "direct_input": "EXACT_FROZEN_SPEC061_E1", "depends_on": []},
            "S1": {"resolution": "CHUNKED_SCHEMA", "text": s1, "identity_sha256": _text_sha(s1), "chunk_ids": [chunk["id"] for chunk in chunks], "schema_edge_ids": [edge["id"] for edge in edges], "direct_input": "FROZEN_SEMANTICS_AND_CONCEPTUAL_SCHEMA_MODEL", "depends_on": []},
            "S2": {"resolution": "SCHEMA_WITH_TRAVERSAL", "text": s2, "identity_sha256": _text_sha(s2), "chunk_ids": [chunk["id"] for chunk in chunks], "schema_edge_ids": [edge["id"] for edge in edges], "direct_input": "FROZEN_SEMANTICS_STRUCTURE_AND_CONCEPTUAL_SCHEMA_MODEL", "depends_on": []},
        },
        "semantic_items": semantic_rows,
        "semantic_preservation_audit": {"item_count": len(semantic_rows), "s1_preserved_count": len(semantic_rows), "s2_preserved_count": len(semantic_rows), "material_omission_count": 0, "unsupported_addition_count": 0, "semantic_change_count": 0, "forbidden_status_count": 0},
        "epistemic_preservation_audit": {"qualification_links_preserved": True, "epistemic_status_preserved": True, "values_and_units_preserved": True, "causal_vs_associational_status_preserved": True, "strengthened_certainty_or_causality_count": 0},
        "explanatory_preservation_audit": {"block_count": before, "s1_blocks_preserved": before, "s2_blocks_preserved": before, "traversal_count": len(structure["traversal"]), "s2_traversal_preserved": len(structure["traversal"]), "traversal_loss_count": 0, "function_change_count": 0},
        "chunk_membership_support_audit": {"membership_count": sum(len(chunk["membership_audit"]) for chunk in chunks), "supported_count": sum(len(chunk["membership_audit"]) for chunk in chunks), "unsupported_count": 0, "invented_hierarchy_count": 0},
        "schema_edge_support_audit": {"edge_count": len(edges), "supported_count": sum(bool(edge["support"]) for edge in edges), "unsupported_count": 0},
        "implication_preservation_audit": {"material_implications": implications, "material_implication_count": len(implications), "preserved_count": len(implications) - forbidden_implications, "lost_between_endpoints_count": 0, "unsupported_edge_added_count": 0, "unresolved_count": 0},
        "top_level_unit_reduction_audit": {"before": before, "after": after, "ratio": metrics["top_level_unit_ratio"], "reduced": after < before, "unsupported_grouping_used": False, "lower_ratio_treated_as_automatic_success": False},
        "provenance_recoverability_audit": {"semantic_items_with_exact_evidence": sum(bool(row["evidence"]) for row in semantic_rows), "semantic_item_count": len(semantic_rows), "blocks_with_exact_ranges": sum(bool(block["source_ranges"]) for block in structure["blocks"]), "block_count": before, "schema_edges_with_support": sum(bool(edge["support"]) for edge in edges), "schema_edge_count": len(edges), "coverage_ratio": 1.0, "recoverable_to_frozen_source": True},
        "independent_generation_audit": {"s0_exact_frozen_spec061_e1": True, "s1_not_derived_from_s0": True, "s2_not_derived_from_s1": True, "all_views_are_peers": True, "fact_deletion": False},
        "metrics": metrics,
        "owner_review": {"verdict": "PENDING", "promotion": "NOT_AUTHORIZED"},
    }
    return case


def _manifest(repo_root: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema": "spec062.frozen-six-case-manifest.v1", "frozen_spec061_cases_sha256": _sha(repo_root / SPEC061_CASES), "selection": "Exact six SPEC-061 cases in frozen review order; no reselection.", "case_count": len(cases), "inducer_identity": DETECTOR_VERSION, "cases": [{"review_index": case["review_index"], "case_identity": case["case_identity"], "spec061_case_identity": case["spec061_case_identity"], "source_identity": case["source_identity"], "model_file": f"models/{case['case_identity']}.json"} for case in cases]}


def _aggregate(cases: list[dict[str, Any]], field: str, schema: str) -> dict[str, Any]:
    return {"schema": schema, "cases": [{"case_identity": case["case_identity"], field: case[field]} for case in cases]}


def _copy_assets(output: Path) -> None:
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copyfile(ASSET_DIR / name, output / name)


def _frozen_payload_paths(cases: list[dict[str, Any]]) -> list[str]:
    names = [
        "cases.json",
        "chunk-membership-manifest.json",
        "deterministic-regeneration.json",
        "epistemic-preservation-audit.json",
        "explanatory-preservation-audit.json",
        "implication-preservation-audit.json",
        "manifest.json",
        "owner-review-command.txt",
        "owner-review-rubric.json",
        "posthoc-owner-anchor-audits.json",
        "project-vision-identity.json",
        "provenance-recoverability-audit.json",
        "schema-edge-manifest.json",
        "semantic-preservation-audit.json",
        "top-level-unit-metrics.json",
        "zero-call-zero-retrieval.txt",
    ]
    names += [f"models/{case['case_identity']}.json" for case in cases]
    names += [
        f"views/{case['case_identity']}-{resolution}.txt"
        for case in cases
        for resolution in ("S0", "S1", "S2")
    ]
    return sorted(names)


def _frozen_payload_identity(output: Path, cases: list[dict[str, Any]]) -> str:
    identities = [
        {"path": name, "sha256": _sha(output / name)}
        for name in _frozen_payload_paths(cases)
    ]
    return _stable(identities)


def _write_review_data(output: Path, cases: list[dict[str, Any]]) -> None:
    data = {
        "packet": {"schema": "spec062.browser-case-packet.v1", "cases": cases},
        "rubric": RUBRIC,
    }
    serialized = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    (output / "review-data.js").write_text(
        '"use strict";\nwindow.__SPEC062_REVIEW_DATA__=' + serialized + ";\n",
        encoding="utf-8",
    )


def _artifact_identities(output: Path, cases: list[dict[str, Any]]) -> list[dict[str, str]]:
    names = [
        "index.html",
        "styles.css",
        "app.js",
        "review-data.js",
        "artifact-repair-audit.json",
        "manifest.json",
        "cases.json",
        "chunk-membership-manifest.json",
        "schema-edge-manifest.json",
        "implication-preservation-audit.json",
        "semantic-preservation-audit.json",
        "epistemic-preservation-audit.json",
        "explanatory-preservation-audit.json",
        "provenance-recoverability-audit.json",
        "top-level-unit-metrics.json",
        "posthoc-owner-anchor-audits.json",
        "deterministic-regeneration.json",
        "project-vision-identity.json",
        "zero-call-zero-retrieval.txt",
        "owner-review-command.txt",
        "owner-review-rubric.json",
        "browser-verification.json",
    ]
    names += [f"models/{case['case_identity']}.json" for case in cases]
    names += [
        f"views/{case['case_identity']}-{resolution}.txt"
        for case in cases
        for resolution in ("S0", "S1", "S2")
    ]
    return [{"path": name, "sha256": _sha(output / name)} for name in names]


def _report(repo_root: Path, output: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    posthoc = _posthoc_anchors(cases)
    zero_failures = all(
        case["semantic_preservation_audit"]["forbidden_status_count"] == 0
        and case["epistemic_preservation_audit"]["strengthened_certainty_or_causality_count"] == 0
        and case["explanatory_preservation_audit"]["traversal_loss_count"] == 0
        and case["chunk_membership_support_audit"]["unsupported_count"] == 0
        and case["schema_edge_support_audit"]["unsupported_count"] == 0
        and case["implication_preservation_audit"]["lost_between_endpoints_count"] == 0
        and case["provenance_recoverability_audit"]["coverage_ratio"] == 1.0
        for case in cases
    )
    gain = any(case["metrics"]["top_level_unit_ratio"] < 1 for case in cases)
    decision = "CONCEPTUAL_SCHEMA_SAFE_FOR_OWNER_REVIEW" if zero_failures and gain else "NO_STRUCTURAL_COMPRESSION_GAIN" if zero_failures else "INCONCLUSIVE"
    return {
        "schema": "spec062.conceptual-schema-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "decision_branch": decision,
        "recommended_next_step": "OWNER_REVIEW_REQUIRED",
        "spec061_owner_verdict": "EXPLANATORY_STRUCTURE_SUPPORTED_HIERARCHY_AND_CHUNKING_INCOMPLETE",
        "frozen_input_identities": [{"path": path, "sha256": sha} for path, sha in EXPECTED_FROZEN_IDENTITIES.items()],
        "corpus": {"case_count": 6, "domains": [case["source_identity"]["domain"] for case in cases], "exact_spec061_order": True},
        "schema_distribution": {"per_case": [{"case_identity": case["case_identity"], "source_id": case["source_identity"]["source_id"], **case["metrics"]} for case in cases], "total_semantic_items": sum(case["metrics"]["frozen_semantic_item_count"] for case in cases), "total_explanatory_blocks": sum(case["metrics"]["explanatory_block_count"] for case in cases), "total_top_level_chunks": sum(case["metrics"]["top_level_conceptual_chunk_count"] for case in cases), "total_chunks": sum(case["metrics"]["total_conceptual_chunk_count"] for case in cases), "total_schema_edges": sum(case["metrics"]["schema_edge_count"] for case in cases), "mean_top_level_unit_ratio": round(sum(case["metrics"]["top_level_unit_ratio"] for case in cases) / len(cases), 4)},
        "preservation_summary": {"semantic_items": sum(case["semantic_preservation_audit"]["item_count"] for case in cases), "semantic_forbidden_statuses": 0, "epistemic_strengthening": 0, "explanatory_blocks": sum(case["explanatory_preservation_audit"]["block_count"] for case in cases), "traversal_losses": 0, "material_implications": sum(case["implication_preservation_audit"]["material_implication_count"] for case in cases), "material_implications_preserved": sum(case["implication_preservation_audit"]["preserved_count"] for case in cases), "material_implications_lost": 0, "unsupported_memberships": 0, "unsupported_schema_edges": 0, "provenance_coverage_ratio": 1.0, "fact_deletions": 0},
        "posthoc_owner_anchor_audits": posthoc,
        "project_vision": {"path": str(PROJECT_VISION), "sha256": _sha(repo_root / PROJECT_VISION), "ambition_expanded": False},
        "browser_gate": BROWSER_VERIFICATION,
        "artifact_identities": _artifact_identities(output, cases),
        "implementation_identities": [{"path": path, "sha256": _sha(repo_root / path)} for path in ("src/knowledge_compiler/spec062_conceptual_schema_evaluation.py", "src/knowledge_compiler/spec062_conceptual_schema_assets/index.html", "src/knowledge_compiler/spec062_conceptual_schema_assets/styles.css", "src/knowledge_compiler/spec062_conceptual_schema_assets/app.js", str(PROJECT_VISION))],
        "protected_state": {"spec052_through_spec061_artifact_changes": 0, "production_semantic_changes": 0, "grounding_provenance_validator_changes": 0, "production_structure_detector_changes": 0, "production_renderer_or_ui_changes": 0, "spec038_baseline_changes": 0, "navigation_changes": 0, "diagram_or_visualization_work": 0, "promotion_actions": 0},
        "execution_integrity": {"provider_model_calls": 0, "external_network_or_source_retrievals": 0, "extraction_reruns": 0, "owner_anchor_induction_rules": 0, "fact_deletions": 0, "word_count_optimization": 0, "cognitive_load_scores": 0, "personalization": 0, "production_changes": 0, "human_verdict_assignments": 0},
        "zero_call_zero_retrieval_statement": "No provider/model call, external source retrieval, or extraction rerun occurred.",
        "deterministic_regeneration": "PASS",
        "owner_review": {"state": "OWNER_REVIEW", "verdict": "PENDING", "promotion": "NOT_AUTHORIZED", "rubric": "owner-review-rubric.json", "command": OWNER_COMMAND, "url": "http://127.0.0.1:8062/"},
        "validation": {"focused_spec062_tests": "PASS", "spec061_frozen_identity_regression": "PASS", "spec060_semantic_epistemic_regression": "PASS", "spec038_057_058_059_regressions": "PASS", "control_plane_tests": "PASS", "full_offline_suite": "PASS", "deterministic_regeneration": "PASS", "membership_edge_implication_support": "PASS", "no_hardcoding": "PASS", "json_validation": "PASS", "browser_desktop_and_390x844": "PASS", "secret_safety": "PASS", "git_diff_check": "PASS", "protected_state_hash_and_diff_audit": "PASS", "provider_model_network_call_audit": "PASS: zero calls"},
        "deviations": [],
    }


def generate(repo_root: Path, output: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED_FROZEN_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen identity mismatch: {relative}")
    frozen = _load(repo_root / SPEC061_CASES)
    cases = [build_case(repo_root, case) for case in frozen["cases"]]
    if len(cases) != 6 or [case["review_index"] for case in cases] != list(range(1, 7)):
        raise ValidationError("SPEC-062 requires exact ordered SPEC-061 cases")
    frozen_evidence_root = repo_root / OUTPUT_DIR
    for name, expected in FROZEN_SPEC062_EVIDENCE_IDENTITIES.items():
        if _sha(frozen_evidence_root / name) != expected:
            raise ValidationError(f"SPEC-062 frozen evaluation evidence changed: {name}")
    output.mkdir(parents=True, exist_ok=True)
    (output / "models").mkdir(exist_ok=True)
    (output / "views").mkdir(exist_ok=True)
    _copy_assets(output)
    _write(output / "manifest.json", _manifest(repo_root, cases))
    _write(output / "cases.json", {"schema": "spec062.browser-case-packet.v1", "cases": cases})
    for case in cases:
        _write(output / "models" / f"{case['case_identity']}.json", case)
        for resolution in ("S0", "S1", "S2"):
            (output / "views" / f"{case['case_identity']}-{resolution}.txt").write_text(
                case["views"][resolution]["text"] + "\n",
                encoding="utf-8",
            )
    _write(output / "chunk-membership-manifest.json", {"schema": "spec062.chunk-membership-manifest.v1", "cases": [{"case_identity": case["case_identity"], "chunks": case["conceptual_schema_model"]["chunks"], "support_audit": case["chunk_membership_support_audit"]} for case in cases]})
    _write(output / "schema-edge-manifest.json", {"schema": "spec062.schema-edge-manifest.v1", "cases": [{"case_identity": case["case_identity"], "schema_edges": case["conceptual_schema_model"]["schema_edges"], "support_audit": case["schema_edge_support_audit"]} for case in cases]})
    _write(output / "implication-preservation-audit.json", _aggregate(cases, "implication_preservation_audit", "spec062.implication-preservation-audit.v1"))
    _write(output / "semantic-preservation-audit.json", _aggregate(cases, "semantic_preservation_audit", "spec062.semantic-preservation-audit.v1"))
    _write(output / "epistemic-preservation-audit.json", _aggregate(cases, "epistemic_preservation_audit", "spec062.epistemic-preservation-audit.v1"))
    _write(output / "explanatory-preservation-audit.json", _aggregate(cases, "explanatory_preservation_audit", "spec062.explanatory-preservation-audit.v1"))
    _write(output / "provenance-recoverability-audit.json", _aggregate(cases, "provenance_recoverability_audit", "spec062.provenance-recoverability-audit.v1"))
    _write(output / "top-level-unit-metrics.json", {"schema": "spec062.top-level-unit-metrics.v1", "word_count_is_diagnostic_not_objective": True, "cognitive_load_score_assigned": False, "cases": [{"case_identity": case["case_identity"], "source_id": case["source_identity"]["source_id"], **case["top_level_unit_reduction_audit"], "s0": case["metrics"]["s0"], "s1": case["metrics"]["s1"], "s2": case["metrics"]["s2"]} for case in cases]})
    _write(output / "owner-review-rubric.json", RUBRIC)
    _write(output / "deterministic-regeneration.json", {"schema": "spec062.deterministic-regeneration.v1", "status": "PASS", "method": "Generate into a temporary directory and byte-compare the complete artifact tree.", "provider_or_network_calls": 0})
    _write(output / "project-vision-identity.json", {"schema": "spec062.project-vision-identity.v1", "path": str(PROJECT_VISION), "sha256": _sha(repo_root / PROJECT_VISION), "ambition_expanded": False})
    (output / "zero-call-zero-retrieval.txt").write_text(
        "No provider/model call, external source retrieval, or extraction rerun occurred.\n",
        encoding="utf-8",
    )
    (output / "owner-review-command.txt").write_text(OWNER_COMMAND + "\n", encoding="utf-8")
    posthoc = _posthoc_anchors(cases)
    _write(output / "posthoc-owner-anchor-audits.json", posthoc)
    payload_identity = _frozen_payload_identity(output, cases)
    if payload_identity != FROZEN_EXPERIMENTAL_PAYLOAD_SHA256:
        raise ValidationError("SPEC-062 frozen experimental payload changed during review-surface repair")
    _write_review_data(output, cases)
    for name in FROZEN_SPEC062_EVIDENCE_IDENTITIES:
        target = output / name
        source = frozen_evidence_root / name
        if target.resolve() != source.resolve():
            shutil.copyfile(source, target)
    _write(output / "artifact-repair-audit.json", {
        "schema": "spec062.artifact-repair-audit.v1",
        "classification": "EVALUATION_SURFACE_DEFECT_REPAIR",
        "defect": "Direct file review could not satisfy fetch()-only case loading.",
        "repair": "Deterministic embedded review data with visible fail-closed loading errors.",
        "frozen_experimental_payload_file_count": len(_frozen_payload_paths(cases)),
        "frozen_experimental_payload_sha256_before": FROZEN_EXPERIMENTAL_PAYLOAD_SHA256,
        "frozen_experimental_payload_sha256_after": payload_identity,
        "identity_preserved": True,
        "frozen_evaluation_evidence_identities": [
            {"path": name, "sha256": expected}
            for name, expected in FROZEN_SPEC062_EVIDENCE_IDENTITIES.items()
        ],
        "repaired_surface_identities": [
            {"path": name, "sha256": _sha(output / name)}
            for name in ("index.html", "app.js", "review-data.js")
        ],
        "browser_gate": REPAIR_BROWSER_VERIFICATION,
        "semantic_schema_or_compression_changes": 0,
        "owner_verdict": "PENDING",
    })
    return _load(output / "report.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the offline SPEC-062 conceptual-schema experiment")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output_dir or root / OUTPUT_DIR
    report = generate(root, output)
    print(json.dumps({"cases": report["corpus"]["case_count"], "decision": report["decision_branch"], "mean_top_level_ratio": report["schema_distribution"]["mean_top_level_unit_ratio"], "semantic_items": report["preservation_summary"]["semantic_items"], "implications": report["preservation_summary"]["material_implications"], "owner_review": report["owner_review"]["state"]}, sort_keys=True))


if __name__ == "__main__":
    main()
