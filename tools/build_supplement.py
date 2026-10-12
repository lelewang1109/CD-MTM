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
             ROOT / "analysis/README.md",
             ROOT / "notes/january-pm25-and-sfc-baselines.md",
             ROOT / "notes/experiment-documentation-history.md",
             ROOT / "notes/method-performance-audit.md",
             ROOT / "notes/result-presentation-cleanup.json",
             ROOT / "results/final_performance.csv", Path(__file__)]
    for directory in ("src", "experiments", "analysis", "tests", "tools"):
        paths.extend(p for p in (ROOT / directory).rglob("*.py") if "archive_oisst" not in str(p))
    paths.extend(p for p in (ROOT / "results").glob("*.json") if not any(n in p.name for n in ("era5_2014", "oisst")))
    paths.extend((ROOT / "results/archive/pm25_janfeb").glob("*.json"))
    paths.extend(p for p in (ROOT / "results/revised_suite").glob("*.json") if "oisst" not in p.name)
    paths.extend(p for p in (ROOT / "results/revised_suite").glob("*.log") if "oisst" not in p.name)
    paper = ROOT / "paper/pacificvis2027"
    paths.extend(paper / name for name in ("README.md", "main.tex", "refs.bib", "vgtc.cls"))
    paths.extend(paper.glob("*.bst"))
    paths.append(paper / "experiments_revised.tex")
    paths.append(paper / "seasonal_controls.tex")
    paths.append(paper / "performance_diagnostics.tex")
    paths.append(paper / "spatial_motion_controls.tex")
    paths.extend((paper / "figures").glob("*.pdf"))
    paths.extend(p for p in (paper / "figures/panels").rglob("*.pdf") if not any(n in p.name for n in ("era5_2014", "oisst")))
    paths.extend(p for p in (paper / "figures/panels").rglob("*.png") if not any(n in p.name for n in ("era5_2014", "oisst")))
    paths.extend((ROOT / "analysis/panels").rglob("*.md"))
    paths.extend((ROOT / "analysis/visualization").glob("*.md"))
    paths.extend(p for p in (ROOT / "results/visualizations").glob("*")
                 if p.suffix in (".pdf", ".png", ".svg", ".json", ".md"))
    paths.append(ROOT / "tools/package_panels.py")
    paths.append(ROOT / "tools/preview_panels.py")
    paths.append(ROOT / "tools/fetch_coastline.py")
    paths.append(ROOT / "tools/refresh_pdf_figures.py")
    paths.append(ROOT / "tools/verify_independent_panels.py")
    paths.append(ROOT / "tools/package_panel_code.py")
    paths.append(ROOT / "data/geo/ne_110m_coastline.geojson")
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
