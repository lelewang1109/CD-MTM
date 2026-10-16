"""Historical hashes survive a registered rename; unrelated edits must fail."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from provenance import verify_saved_file


class RenameProvenanceTests(unittest.TestCase):
    def test_exact_rename_and_subsequent_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = b"from cdmtm import layout\n"
            after = b"from rgmtm import layout\n"
            sha = lambda value: hashlib.sha256(value).hexdigest()
            (root / "src").mkdir()
            current = root / "src/new.py"
            current.write_bytes(after)
            (root / "provenance").mkdir()
            manifest = root / "provenance/rgmtm_rename_20261016.json"
            manifest.write_text(json.dumps({"sources": {"src/old.py": {
                "before_sha256": sha(before), "after_sha256": sha(after),
                "after_path": "src/new.py", "reverse_edits": [[5, 10, "cdmtm"]]}}}))
            self.assertEqual(verify_saved_file(root, "src/old.py", sha(before)), "verified pre-rename source")
            current.write_bytes(after + b"changed = True\n")
            with self.assertRaises(ValueError):
                verify_saved_file(root, "src/old.py", sha(before))
            current.write_bytes(after)
            with self.assertRaises(ValueError):
                verify_saved_file(root, "src/old.py", "0" * 64)
            data = json.loads(manifest.read_text())
            data["sources"]["src/old.py"]["reverse_edits"][0][2] = "wrong"
            manifest.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                verify_saved_file(root, "src/old.py", sha(before))


if __name__ == "__main__":
    unittest.main()
