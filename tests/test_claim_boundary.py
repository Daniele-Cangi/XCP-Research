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


class ClaimBoundaryTests(unittest.TestCase):
    def test_global_claim_escalation_fails_after_all_public_hashes_are_resealed(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            snapshot = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, snapshot)
            report_path = snapshot / "differential-report.json"
            report = verify.load_json(report_path)
            report["decision"]["claim"] = "global_equivalence_supported"
            report["decision"]["global_equivalence"] = "supported"
            write_json(report_path, report)

            manifest_path = snapshot / "manifest.json"
            manifest = verify.load_json(manifest_path)
            for entry in manifest["files"]:
                if entry["path"] == "differential-report.json":
                    entry["bytes"] = report_path.stat().st_size
                    entry["sha256"] = verify.file_sha256(report_path)
            manifest["manifest_sha256"] = verify.canonical_sha256(manifest, omit="manifest_sha256")
            write_json(manifest_path, manifest)

            with self.assertRaisesRegex(verify.VerificationError, "claim|global equivalence"):
                verify.verify_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
