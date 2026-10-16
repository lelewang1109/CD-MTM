"""Publish only the two explicitly selected paper PDFs; keep writing sources local."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
APPROVED_PDFS = {
    Path("publications/RG-MTM-latest.pdf"),
    Path("publications/RG-MTM-supplement.pdf"),
}


def main():
    names = subprocess.check_output(["git", "ls-files", "--cached", "-z"], cwd=ROOT).split(b"\0")
    forbidden = []
    for raw in names:
        if not raw:
            continue
        path = Path(raw.decode())
        if path in APPROVED_PDFS:
            if (ROOT / path).is_symlink():
                forbidden.append(str(path))
            continue
        manuscript = path.parts[0] in {"paper", "notes"}
        manuscript |= path.parts[0] == "publications" and path.suffix == ".pdf"
        manuscript |= path.suffix in {".bib", ".bst", ".cls", ".sty"}
        manuscript |= path.suffix == ".tex" and "tables" not in path.parts
        manuscript |= path.suffix == ".pdf" and path.stem in {"main", "main_content", "supplement", "review-preview", "proofs"}
        if manuscript:
            forbidden.append(str(path))
    if forbidden:
        raise SystemExit("Unapproved manuscript files must remain local:\n" + "\n".join(forbidden))
    print("Public export check passed: only selected paper PDFs may be published; writing sources remain local.")


if __name__ == "__main__":
    main()
