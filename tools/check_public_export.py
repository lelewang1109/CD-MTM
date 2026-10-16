"""Reject manuscript PDFs/sources and writing notes from the Git publication set."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = subprocess.check_output(["git", "ls-files", "--cached", "-z"], cwd=ROOT).split(b"\0")
    forbidden = []
    for raw in names:
        if not raw:
            continue
        path = Path(raw.decode())
        manuscript = path.parts[0] in {"paper", "notes"}
        manuscript |= path.suffix in {".bib", ".bst", ".cls", ".sty"}
        manuscript |= path.suffix == ".tex" and "tables" not in path.parts
        manuscript |= path.suffix == ".pdf" and path.stem in {"main", "main_content", "supplement", "review-preview", "proofs"}
        if manuscript:
            forbidden.append(str(path))
    if forbidden:
        raise SystemExit("Manuscript files must remain local:\n" + "\n".join(forbidden))
    print("Public export check passed: no manuscript PDFs, LaTeX sources, or writing notes tracked.")


if __name__ == "__main__":
    main()
