"""Compatibility entry point for a code/results archive; manuscripts stay local."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "experiments/publication2027/package.py"), run_name="__main__")
