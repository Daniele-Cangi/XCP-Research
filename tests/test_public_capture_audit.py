from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verifier"))
import audit  # noqa: E402


class PublicCaptureAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for name in audit.PUBLIC_CAPTURES:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_exact_public_captures_are_accepted(self) -> None:
        _, findings = audit.audit(self.root)
        self.assertEqual(findings, [])

    def test_changed_capture_is_rejected(self) -> None:
        image = self.root / "assets/showcase/03-minilens.webp"
        altered = bytearray(image.read_bytes())
        altered[-1] ^= 1
        image.write_bytes(altered)
        _, findings = audit.audit(self.root)
        self.assertTrue(any("public capture differs from pinned bytes" in item for item in findings))

    def test_unregistered_binary_is_rejected(self) -> None:
        extra = self.root / "assets/showcase/extra.webp"
        extra.write_bytes(b"RIFF\x00\x00\x00\x00WEBP")
        _, findings = audit.audit(self.root)
        self.assertIn("assets/showcase/extra.webp: non-text file type is forbidden", findings)

    def test_missing_registered_capture_is_rejected(self) -> None:
        (self.root / "assets/showcase/02-core-siege.webp").unlink()
        _, findings = audit.audit(self.root)
        self.assertIn("assets/showcase/02-core-siege.webp: registered public capture is missing", findings)
