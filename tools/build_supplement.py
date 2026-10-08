"""Build the deterministic anonymous PacificVis source-and-results archive."""
from hashlib import sha256
from pathlib import Path
import json
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/pacificvis2027/supplement.zip"


def include_files():
    paths = [ROOT / "README.md", ROOT / "pyproject.toml",
             ROOT / "paper/proofs.tex", ROOT / "paper/README.md",
             ROOT / "data/README.md", ROOT / "results/README.md",
             ROOT / "analysis/README.md", Path(__file__)]
    for directory in ("src", "experiments", "analysis", "tests"):
        paths.extend((ROOT / directory).rglob("*.py"))
    paths.extend((ROOT / "results").glob("*.json"))
    paper = ROOT / "paper/pacificvis2027"
    paths.extend(paper / name for name in ("README.md", "main.tex", "refs.bib", "vgtc.cls"))
    paths.extend(paper.glob("*.bst"))
    paths.extend((paper / "figures").glob("*.pdf"))
    return sorted(set(paths), key=lambda path: str(path.relative_to(ROOT)))


def write_member(archive, name, data):
    item = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    item.compress_type = ZIP_DEFLATED
    item.external_attr = 0o644 << 16
    archive.writestr(item, data)


def main():
    paths = include_files()
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing supplement inputs: {missing}")
    manifest = {
        "scope": "PacificVis 2027 CD-MTM anonymous source and selected final results",
        "excluded": "Public raw inputs and historical X/Y dual-view experiments",
        "files": {},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w") as archive:
        for path in paths:
            name = str(path.relative_to(ROOT))
            data = path.read_bytes()
            manifest["files"][name] = sha256(data).hexdigest()
            write_member(archive, name, data)
        write_member(archive, "MANIFEST.json", (json.dumps(manifest, indent=2) + "\n").encode())
    print(OUT, len(paths), "files", OUT.stat().st_size, "bytes", "sha256", sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()

