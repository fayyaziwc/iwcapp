#!/usr/bin/env python3
"""Generate app-planning artifacts from plain-English requirements."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PRIORITY_KEYWORDS = {
    "P0": ["must", "critical", "required", "security", "auth", "payment"],
    "P1": ["should", "important", "dashboard", "report", "analytics", "integration"],
    "P2": ["nice", "optional", "later", "polish", "theme", "custom"],
}


@dataclass
class Feature:
    name: str
    description: str
    priority: str
    acceptance_criteria: list[str]


def sentence_split(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [s.strip(" -\t") for s in raw if s.strip()]


def infer_priority(sentence: str) -> str:
    low = sentence.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(k in low for k in keywords):
            return priority
    return "P1"


def titleize_feature(sentence: str, idx: int) -> str:
    clean = re.sub(r"[^A-Za-z0-9\s]", "", sentence).strip()
    words = clean.split()
    if not words:
        return f"Feature {idx}"
    return " ".join(words[:6]).title()


def build_acceptance_criteria(sentence: str) -> list[str]:
    base = sentence.rstrip(".")
    return [
        f"System supports: {base}.",
        "Behavior is testable with at least one happy-path scenario.",
        "Errors are surfaced with clear user-facing messages.",
    ]


def extract_features(requirements: str) -> list[Feature]:
    sentences = sentence_split(requirements)
    features: list[Feature] = []
    for idx, sentence in enumerate(sentences, start=1):
        if len(sentence.split()) < 3:
            continue
        features.append(
            Feature(
                name=titleize_feature(sentence, idx),
                description=sentence,
                priority=infer_priority(sentence),
                acceptance_criteria=build_acceptance_criteria(sentence),
            )
        )

    if not features:
        features.append(
            Feature(
                name="Core Workflow",
                description="Implement the primary app workflow from provided requirements.",
                priority="P0",
                acceptance_criteria=build_acceptance_criteria(
                    "Users can complete the primary workflow end-to-end"
                ),
            )
        )
    return features


def markdown_requirements(app_name: str, requirements: str, features: Iterable[Feature]) -> str:
    lines = [
        f"# Product Requirements: {app_name}",
        "",
        "## Vision",
        f"Build **{app_name}** based on the following high-level input:",
        "",
        f"> {requirements}",
        "",
        "## Derived Feature Scope",
    ]
    for i, feature in enumerate(features, start=1):
        lines.append(f"{i}. **{feature.name}** ({feature.priority}) — {feature.description}")
    lines += ["", "## Non-Functional Requirements", "- Reliability", "- Security", "- Observability"]
    return "\n".join(lines) + "\n"


def markdown_implementation_plan(app_name: str, features: list[Feature]) -> str:
    p0 = [f for f in features if f.priority == "P0"]
    p1 = [f for f in features if f.priority == "P1"]
    p2 = [f for f in features if f.priority == "P2"]

    def bullet(fs: list[Feature]) -> list[str]:
        return [f"- {f.name}: {f.description}" for f in fs] or ["- None"]

    lines = [
        f"# Implementation Plan: {app_name}",
        "",
        "## Milestone 1 — Core (P0)",
        *bullet(p0),
        "",
        "## Milestone 2 — Expansion (P1)",
        *bullet(p1),
        "",
        "## Milestone 3 — Enhancements (P2)",
        *bullet(p2),
        "",
        "## Definition of Done",
        "- Core user flow works end-to-end.",
        "- Tests cover critical paths.",
        "- Deployment checklist completed.",
    ]
    return "\n".join(lines) + "\n"


def features_json(features: list[Feature]) -> str:
    return json.dumps(
        [
            {
                "name": f.name,
                "description": f.description,
                "priority": f.priority,
                "acceptance_criteria": f.acceptance_criteria,
            }
            for f in features
        ],
        indent=2,
    ) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate app planning artifacts")
    gen.add_argument("--name", required=True, help="App/project name")
    group = gen.add_mutually_exclusive_group(required=True)
    group.add_argument("--requirements", help="Inline requirements text")
    group.add_argument("--requirements-file", help="Path to a text file with requirements")
    gen.add_argument("--out", default="./output", help="Output folder")
    gen.add_argument("--stdout", action="store_true", help="Print artifacts instead of writing files")

    return parser.parse_args()


def load_requirements(args: argparse.Namespace) -> str:
    if args.requirements is not None:
        return args.requirements.strip()
    if args.requirements_file is None:
        raise ValueError("Either --requirements or --requirements-file must be provided.")
    return Path(args.requirements_file).read_text(encoding="utf-8").strip()


def generate(args: argparse.Namespace) -> int:
    req = load_requirements(args)
    features = extract_features(req)

    requirements_md = markdown_requirements(args.name, req, features)
    plan_md = markdown_implementation_plan(args.name, features)
    features_payload = features_json(features)

    if args.stdout:
        print("=== product_requirements.md ===")
        print(requirements_md)
        print("=== implementation_plan.md ===")
        print(plan_md)
        print("=== features.json ===")
        print(features_payload)
        return 0

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "product_requirements.md").write_text(requirements_md, encoding="utf-8")
    (out_dir / "implementation_plan.md").write_text(plan_md, encoding="utf-8")
    (out_dir / "features.json").write_text(features_payload, encoding="utf-8")

    print(f"Generated artifacts in: {out_dir}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "generate":
        return generate(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
