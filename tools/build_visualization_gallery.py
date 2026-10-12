"""Repository-root entry point for the shared visualization package."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'analysis'), str(ROOT / 'src'), str(ROOT)]
from visualization.gallery import main

if __name__ == '__main__':
    main()
