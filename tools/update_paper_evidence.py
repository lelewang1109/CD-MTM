"""Compatibility entry point for the modular publication evidence builder.

The previous implementation rewrote manuscript prose by locating subsection
names. Its historical source is notes/archive/update_paper_evidence_legacy.txt.
Tables and snapshots now have their own builder; prose remains independently editable.
"""
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[1]

def proxy(d,method,mode='proxy'):
    """Return one declared motion row; reject missing or duplicate evidence."""
    rows=[x for x in d[mode] if x['method']==method and x['k']==2 and x['eps']==.02]
    if len(rows)!=1:
        raise ValueError(f'Expected one completed motion row: {d.get("dataset")} / {method} / {mode}')
    return rows[0]

def main():
    runpy.run_path(str(ROOT/'experiments/publication2027/build.py'),run_name='__main__')

if __name__=='__main__':main()
