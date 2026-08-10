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


class ManifestTamperTests(unittest.TestCase):
    def test_evidence_byte_change_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            snapshot = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, snapshot)
            path = snapshot / "source-summary.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(verify.VerificationError, "byte length mismatch"):
                verify.verify_snapshot(snapshot)

    def test_referenced_hash_change_fails_even_with_manifest_resealed(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            snapshot = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, snapshot)
            manifest_path = snapshot / "manifest.json"
            manifest = verify.load_json(manifest_path)
            manifest["files"][0]["sha256"] = "f" * 64
            manifest["manifest_sha256"] = verify.canonical_sha256(manifest, omit="manifest_sha256")
            write_json(manifest_path, manifest)
            with self.assertRaisesRegex(verify.VerificationError, "SHA-256 mismatch"):
                verify.verify_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
