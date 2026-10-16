"""Verify saved evidence against exact, reversible source renames.

Old numerical runs retain their original source hashes. A registered rename is
accepted only if the current file matches its recorded post-rename hash and its
reverse edits reconstruct the exact old bytes. This is not evidence of a new run.
"""
from pathlib import Path
import hashlib
import json


def evidence_path(root, relative_path):
    """Resolve old experimental-asset paths without publishing manuscripts."""
    root = Path(root)
    relative_path = Path(relative_path)
    if relative_path.parts and relative_path.parts[0] == "paper":
        relocated = root / "results/legacy_publication" / Path(*relative_path.parts[1:])
        if relocated.is_file():
            return relocated
    return root / relative_path


def verify_saved_file(root, relative_path, expected):
    root = Path(root)
    path = evidence_path(root, relative_path)
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected:
        return "unchanged"
    manifest = root / "provenance/rgmtm_rename_20261016.json"
    record = json.loads(manifest.read_text())["sources"].get(str(relative_path))
    if not record or record["before_sha256"] != expected:
        raise ValueError(f"Unregistered evidence/source mismatch: {relative_path}")
    current = (root / record["after_path"]).read_bytes()
    if hashlib.sha256(current).hexdigest() != record["after_sha256"]:
        raise ValueError(f"Source changed after registered rename: {relative_path}")
    restored = current
    for start, end, original in reversed(record["reverse_edits"]):
        restored = restored[:start] + original.encode("utf-8") + restored[end:]
    if hashlib.sha256(restored).hexdigest() != expected:
        raise ValueError(f"Invalid reversible rename record: {relative_path}")
    return "verified pre-rename source"
