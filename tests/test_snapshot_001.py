from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verifier"))
import verify  # noqa: E402


SOURCE = ROOT / "snapshots" / "001-g2-motion-validation"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def refresh_manifest(snapshot: Path, changed: str) -> None:
    manifest_path = snapshot / "manifest.json"
    manifest = verify.load_json(manifest_path)
    for entry in manifest["files"]:
        if entry["path"] == changed:
            path = snapshot / changed
            entry["bytes"] = path.stat().st_size
            entry["sha256"] = verify.file_sha256(path)
    manifest["manifest_sha256"] = verify.canonical_sha256(manifest, omit="manifest_sha256")
    write_json(manifest_path, manifest)


class Snapshot001Tests(unittest.TestCase):
    def test_snapshot_verifies(self) -> None:
        checks = verify.verify_snapshot(SOURCE)
        self.assertIn("Claim boundary", checks)

    def test_source_target_identity_mismatch_fails_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            snapshot = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, snapshot)
            target_path = snapshot / "target-summary.json"
            target = verify.load_json(target_path)
            target["source_trace_sha256"] = "0" * 64
            write_json(target_path, target)
            refresh_manifest(snapshot, "target-summary.json")
            with self.assertRaisesRegex(verify.VerificationError, "source trace"):
                verify.verify_snapshot(snapshot)

    def test_differential_contradiction_fails_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            snapshot = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, snapshot)
            report_path = snapshot / "differential-report.json"
            report = verify.load_json(report_path)
            report["measurement"]["tolerance"]["within_tolerance"] = False
            write_json(report_path, report)
            refresh_manifest(snapshot, "differential-report.json")
            with self.assertRaisesRegex(verify.VerificationError, "tolerance"):
                verify.verify_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
