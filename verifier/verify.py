#!/usr/bin/env python3
"""Offline integrity and claim-boundary verifier for XCP Research snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PHASES = {"calibration", "validation", "holdout"}
SNAPSHOT_FILES = {
    "README.md",
    "architecture.svg",
    "source-summary.json",
    "target-summary.json",
    "differential-report.json",
}
SCHEMA_FILES = {
    "evidence-manifest.schema.json",
    "source-summary.schema.json",
    "target-summary.schema.json",
    "differential-report.schema.json",
}
ALLOWED_CLAIM = "bounded_scenario_result_supported"
EXPECTED_REASONS = {
    "measured_divergence_within_declared_tolerance",
    "scenario_evidence_complete",
    "global_coverage_incomplete",
}


class VerificationError(ValueError):
    """Raised when a snapshot fails closed."""


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicates
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read canonical JSON {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{path.name} must contain one JSON object")
    return value


def canonical_bytes(value: dict[str, Any], *, omit: str | None = None) -> bytes:
    document = dict(value)
    if omit is not None:
        document.pop(omit, None)
    return json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(value: dict[str, Any], *, omit: str | None = None) -> str:
    return hashlib.sha256(canonical_bytes(value, omit=omit)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_keys(value: Any, expected: set[str], where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{where} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise VerificationError(
            f"{where} keys differ; missing={missing}, extra={extra}"
        )
    return value


def require_string(value: Any, where: str, expected: str | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{where} must be a non-empty string")
    if expected is not None and value != expected:
        raise VerificationError(f"{where} must equal {expected!r}")
    return value


def require_hash(
    value: Any, where: str, pattern: re.Pattern[str] = HEX64
) -> str:
    text = require_string(value, where)
    if not pattern.fullmatch(text):
        raise VerificationError(f"{where} is not a lowercase hexadecimal identity")
    return text


def require_count(value: Any, where: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise VerificationError(f"{where} must be an integer >= {minimum}")
    return value


def _manifest_entries(snapshot: Path, manifest: dict[str, Any]) -> None:
    exact_keys(
        manifest,
        {"schema_version", "snapshot_id", "files", "manifest_sha256"},
        "manifest",
    )
    require_string(
        manifest["schema_version"],
        "manifest.schema_version",
        "xcp-research-evidence-manifest-v1",
    )
    require_string(manifest["snapshot_id"], "manifest.snapshot_id")
    require_hash(manifest["manifest_sha256"], "manifest.manifest_sha256")

    if canonical_sha256(manifest, omit="manifest_sha256") != manifest["manifest_sha256"]:
        raise VerificationError("manifest canonical SHA-256 does not match")

    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise VerificationError("manifest.files must be a non-empty array")

    declared: set[str] = set()
    for index, item in enumerate(files):
        entry = exact_keys(
            item, {"path", "bytes", "sha256"}, f"manifest.files[{index}]"
        )
        relative = require_string(entry["path"], f"manifest.files[{index}].path")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\\" in relative:
            raise VerificationError(f"unsafe manifest path: {relative}")
        if relative in declared:
            raise VerificationError(f"duplicate manifest path: {relative}")
        declared.add(relative)

        expected_bytes = require_count(entry["bytes"], f"{relative}.bytes", 1)
        expected_hash = require_hash(entry["sha256"], f"{relative}.sha256")
        path = snapshot / relative
        if path.is_symlink() or not path.is_file():
            raise VerificationError(
                f"manifested file is missing, non-file, or symlink: {relative}"
            )
        if path.stat().st_size != expected_bytes:
            raise VerificationError(f"byte length mismatch: {relative}")
        if file_sha256(path) != expected_hash:
            raise VerificationError(f"SHA-256 mismatch: {relative}")

    actual_files = {
        path.relative_to(snapshot).as_posix()
        for path in snapshot.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if declared != SNAPSHOT_FILES or actual_files != SNAPSHOT_FILES:
        raise VerificationError(
            f"snapshot file set differs; declared={sorted(declared)}, "
            f"actual={sorted(actual_files)}"
        )


def _schema_contract(repo_root: Path) -> None:
    schema_root = repo_root / "schemas"
    actual = {path.name for path in schema_root.glob("*.json") if path.is_file()}
    if actual != SCHEMA_FILES:
        raise VerificationError(f"schema file set differs: {sorted(actual)}")
    for name in sorted(SCHEMA_FILES):
        schema = load_json(schema_root / name)
        require_string(schema.get("$schema"), f"{name}.$schema")
        require_string(schema.get("$id"), f"{name}.$id")
        if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
            raise VerificationError(f"{name} must be a closed object schema")


def _source_shape(source: dict[str, Any]) -> None:
    exact_keys(
        source,
        {
            "schema_version",
            "snapshot_id",
            "scenario_id",
            "phase",
            "scenario_sha256",
            "source",
        },
        "source summary",
    )
    require_string(
        source["schema_version"],
        "source.schema_version",
        "xcp-research-source-summary-v1",
    )
    require_string(source["snapshot_id"], "source.snapshot_id")
    require_string(source["scenario_id"], "source.scenario_id")
    if source["phase"] not in PHASES:
        raise VerificationError("source.phase is unsupported")
    require_hash(source["scenario_sha256"], "source.scenario_sha256")

    detail = exact_keys(
        source["source"],
        {
            "project",
            "authorization_basis",
            "revision",
            "observation_status",
            "trace_sha256",
        },
        "source.source",
    )
    require_string(detail["project"], "source.source.project")
    require_string(
        detail["authorization_basis"],
        "source.source.authorization_basis",
        "open-source license",
    )
    require_hash(detail["revision"], "source.source.revision", HEX40)
    require_string(
        detail["observation_status"],
        "source.source.observation_status",
        "complete_for_scenario",
    )
    require_hash(detail["trace_sha256"], "source.source.trace_sha256")


def _target_shape(target: dict[str, Any]) -> None:
    exact_keys(
        target,
        {
            "schema_version",
            "snapshot_id",
            "scenario_id",
            "phase",
            "scenario_sha256",
            "source_trace_sha256",
            "target",
        },
        "target summary",
    )
    require_string(
        target["schema_version"],
        "target.schema_version",
        "xcp-research-target-summary-v1",
    )
    require_string(target["snapshot_id"], "target.snapshot_id")
    require_string(target["scenario_id"], "target.scenario_id")
    if target["phase"] not in PHASES:
        raise VerificationError("target.phase is unsupported")
    require_hash(target["scenario_sha256"], "target.scenario_sha256")
    require_hash(target["source_trace_sha256"], "target.source_trace_sha256")

    detail = exact_keys(
        target["target"],
        {
            "class",
            "worker_artifact_sha256",
            "project_sha256",
            "execution_status",
            "lifecycle_operations",
            "lifecycle_receipt_sha256",
            "observation_evidence_sha256",
            "trace_sha256",
        },
        "target.target",
    )
    require_string(
        detail["class"],
        "target.target.class",
        "constrained Xbox Series X public-UWP candidate",
    )
    for field in (
        "worker_artifact_sha256",
        "project_sha256",
        "lifecycle_receipt_sha256",
        "observation_evidence_sha256",
        "trace_sha256",
    ):
        require_hash(detail[field], f"target.target.{field}")

    require_string(
        detail["execution_status"],
        "target.target.execution_status",
        "complete_for_scenario",
    )
    operations = exact_keys(
        detail["lifecycle_operations"],
        {"passed", "total"},
        "target.target.lifecycle_operations",
    )
    passed = require_count(operations["passed"], "lifecycle_operations.passed")
    total = require_count(operations["total"], "lifecycle_operations.total", 1)
    if passed != total:
        raise VerificationError("target lifecycle is incomplete")


def _differential_shape(report: dict[str, Any]) -> None:
    exact_keys(
        report,
        {
            "schema_version",
            "snapshot_id",
            "scenario_id",
            "phase",
            "identities",
            "measurement",
            "interpretation",
            "coverage",
            "decision",
            "historical_note",
        },
        "differential report",
    )
    require_string(
        report["schema_version"],
        "differential.schema_version",
        "xcp-research-differential-report-v1",
    )
    require_string(report["snapshot_id"], "differential.snapshot_id")
    require_string(report["scenario_id"], "differential.scenario_id")
    if report["phase"] not in PHASES:
        raise VerificationError("differential.phase is unsupported")

    identities = exact_keys(
        report["identities"],
        {
            "scenario_sha256",
            "source_trace_sha256",
            "target_trace_sha256",
            "historical_report_sha256",
        },
        "differential.identities",
    )
    for field, value in identities.items():
        require_hash(value, f"differential.identities.{field}")

    measurement = exact_keys(
        report["measurement"],
        {
            "category",
            "published_decimal",
            "canonical_artifact_decimal",
            "unit",
            "tolerance",
            "significant",
        },
        "differential.measurement",
    )
    require_string(measurement["category"], "measurement.category", "trajectory")
    require_string(measurement["unit"], "measurement.unit", "normalized_cell")
    require_string(measurement["published_decimal"], "measurement.published_decimal")
    require_string(
        measurement["canonical_artifact_decimal"],
        "measurement.canonical_artifact_decimal",
    )
    if not isinstance(measurement["significant"], bool):
        raise VerificationError("measurement.significant must be boolean")

    tolerance = exact_keys(
        measurement["tolerance"],
        {"kind", "maximum_decimal", "within_tolerance"},
        "measurement.tolerance",
    )
    require_string(tolerance["kind"], "tolerance.kind", "absolute")
    require_string(tolerance["maximum_decimal"], "tolerance.maximum_decimal")
    if not isinstance(tolerance["within_tolerance"], bool):
        raise VerificationError("tolerance.within_tolerance must be boolean")

    interpretation = exact_keys(
        report["interpretation"], {"classification"}, "differential.interpretation"
    )
    require_string(
        interpretation["classification"],
        "interpretation.classification",
        "runtime_response_difference",
    )

    coverage = exact_keys(
        report["coverage"],
        {
            "scenario_hard_invariants",
            "scenario_perceptual_invariants",
            "motion_triad_hard_invariants",
            "motion_triad_perceptual_invariants",
        },
        "differential.coverage",
    )
    for name in ("scenario_hard_invariants", "scenario_perceptual_invariants"):
        row = exact_keys(
            coverage[name], {"passed", "evaluated"}, f"coverage.{name}"
        )
        if require_count(row["passed"], f"coverage.{name}.passed") != require_count(
            row["evaluated"], f"coverage.{name}.evaluated", 1
        ):
            raise VerificationError(f"{name} is incomplete")

    for name in (
        "motion_triad_hard_invariants",
        "motion_triad_perceptual_invariants",
    ):
        row = exact_keys(
            coverage[name], {"covered", "contract"}, f"coverage.{name}"
        )
        covered = require_count(row["covered"], f"coverage.{name}.covered")
        contract = require_count(row["contract"], f"coverage.{name}.contract", 1)
        if covered >= contract:
            raise VerificationError(
                "Snapshot 001 must preserve incomplete global coverage"
            )

    exact_keys(
        report["decision"],
        {"claim", "status", "global_equivalence", "reason_codes"},
        "differential.decision",
    )
    require_string(report["historical_note"], "differential.historical_note")


def _bindings(
    source: dict[str, Any],
    target: dict[str, Any],
    report: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    common = (
        manifest["snapshot_id"],
        source["scenario_id"],
        source["phase"],
        source["scenario_sha256"],
    )
    if (
        source["snapshot_id"],
        source["scenario_id"],
        source["phase"],
        source["scenario_sha256"],
    ) != common:
        raise VerificationError("source identity is inconsistent")

    if (
        target["snapshot_id"],
        target["scenario_id"],
        target["phase"],
        target["scenario_sha256"],
    ) != common:
        raise VerificationError("target identity is inconsistent")

    identities = report["identities"]
    if (
        report["snapshot_id"],
        report["scenario_id"],
        report["phase"],
        identities["scenario_sha256"],
    ) != common:
        raise VerificationError("differential identity is inconsistent")

    if target["source_trace_sha256"] != source["source"]["trace_sha256"]:
        raise VerificationError("target is not bound to the published source trace")
    if identities["source_trace_sha256"] != source["source"]["trace_sha256"]:
        raise VerificationError("differential source binding is inconsistent")
    if identities["target_trace_sha256"] != target["target"]["trace_sha256"]:
        raise VerificationError("differential target binding is inconsistent")


def _differential_consistency(report: dict[str, Any]) -> None:
    measurement = report["measurement"]
    tolerance = measurement["tolerance"]
    try:
        measured = Decimal(measurement["canonical_artifact_decimal"])
        published = Decimal(measurement["published_decimal"])
        maximum = Decimal(tolerance["maximum_decimal"])
    except InvalidOperation as exc:
        raise VerificationError("measurement decimals are invalid") from exc

    if measured < 0 or published < 0 or maximum < 0:
        raise VerificationError("measurement decimals must be non-negative")
    if abs(measured - published) > Decimal("0.000000000001"):
        raise VerificationError("published and canonical decimals disagree materially")

    computed_within = measured <= maximum
    if tolerance["within_tolerance"] != computed_within:
        raise VerificationError("tolerance result contradicts the measured value")
    if measurement["significant"] == computed_within:
        raise VerificationError("significance contradicts tolerance authority")

    decision = report["decision"]
    if decision["status"] != "supported_within_declared_scope" or not computed_within:
        raise VerificationError("bounded decision contradicts measurement")


def _claim_boundary(report: dict[str, Any]) -> None:
    decision = report["decision"]
    if decision["claim"] != ALLOWED_CLAIM:
        raise VerificationError("claim is wider than the published allowlist")
    if decision["global_equivalence"] != "not_authorized":
        raise VerificationError("global equivalence is not authorized")

    reasons = decision["reason_codes"]
    if (
        not isinstance(reasons, list)
        or set(reasons) != EXPECTED_REASONS
        or len(reasons) != len(EXPECTED_REASONS)
    ):
        raise VerificationError("claim reason codes are incomplete or widened")


def verify_snapshot(snapshot: Path) -> list[str]:
    snapshot = snapshot.resolve()
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise VerificationError("snapshot path must be a real directory")

    repo_root = Path(__file__).resolve().parent.parent
    try:
        snapshot.relative_to(repo_root)
    except ValueError as exc:
        raise VerificationError("snapshot must be inside this repository") from exc

    manifest = load_json(snapshot / "manifest.json")
    _manifest_entries(snapshot, manifest)
    _schema_contract(repo_root)

    source = load_json(snapshot / "source-summary.json")
    target = load_json(snapshot / "target-summary.json")
    report = load_json(snapshot / "differential-report.json")

    _source_shape(source)
    _target_shape(target)
    _differential_shape(report)
    _bindings(source, target, report, manifest)
    _differential_consistency(report)
    _claim_boundary(report)

    return [
        "Manifest integrity",
        "Schema conformance",
        "Source binding",
        "Target binding",
        "Differential consistency",
        "Claim boundary",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "snapshot", type=Path, help="repository-local snapshot directory"
    )
    args = parser.parse_args(argv)

    try:
        checks = verify_snapshot(args.snapshot)
    except VerificationError as exc:
        print(f"Verification ................ FAIL\nReason: {exc}", file=sys.stderr)
        return 1

    for check in checks:
        print(f"{check:.<31} PASS")
    print("\nSnapshot:\nSUPPORTED WITHIN DECLARED SCOPE")
    print("\nGlobal equivalence:\nNOT AUTHORIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
