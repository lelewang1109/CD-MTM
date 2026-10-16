"""Verify unchanged numerical evidence, reversible source edits, and RG-MTM figures."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from provenance import verify_saved_file


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    migration = json.loads((ROOT / "provenance/rgmtm_rename_20261016.json").read_text())
    for name, expected in migration["protected_result_sha256"].items():
        assert digest(ROOT / name) == expected, name
    local_caches_checked = 0
    for name, expected in migration.get("local_only_result_sha256", {}).items():
        if (ROOT / name).exists():
            assert digest(ROOT / name) == expected, name
            local_caches_checked += 1
    for name, record in migration["sources"].items():
        verify_saved_file(ROOT, name, record["before_sha256"])
    images = json.loads((ROOT / "results/figures/manifest.json").read_text())
    for group in ("source_sha256", "evidence_sha256"):
        for name, expected in images[group].items():
            assert digest(ROOT / name) == expected, name
    for item in images["figures"]:
        for name, expected in item["files"].items():
            assert name.startswith("rgmtm_")
            assert digest(ROOT / "results/figures" / name) == expected, name
    assert (ROOT / "src/rgmtm/reference_guided.py").is_file()
    assert not (ROOT / "src/cdmtm").exists()
    report = dict(status="passed", protected_numerical_files=len(migration["protected_result_sha256"]),
                  local_caches_checked=local_caches_checked,
                  reversible_source_edits=len(migration["sources"]), figures=len(images["figures"]),
                  formats=["PNG", "SVG"], numerical_rerun=False)
    (ROOT / "results/rgmtm_rename_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
