"""Package editable manuscript and reproducible code/evidence without raw data."""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];PAPER=ROOT/'paper/pacificvis2027-restructured';OUT=ROOT/'output/pdf'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 for src,name in [('main.pdf','CD-MTM-PacificVis2027.pdf'),('supplement.pdf','CD-MTM-PacificVis2027-supplement.pdf')]:
  shutil.copy2(PAPER/'build'/src,OUT/name)
 source_files=[p for p in PAPER.rglob('*') if p.is_file() and 'build' not in p.parts and p.suffix in ['.tex','.bib','.cls','.bst','.pdf','.png','.svg','.md']]
 source_zip=PAPER/'latex_sources.zip'
 with zipfile.ZipFile(source_zip,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(source_files):z.write(p,p.relative_to(PAPER))
 shutil.copy2(source_zip,OUT/'CD-MTM-PacificVis2027-LaTeX.zip')
 manifest=json.loads((ROOT/'results/publication2027/manifest.json').read_text())
 files=set()
 for folder in ['src','analysis','experiments','tests','tools']:
  files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.md','.json','.xml'] and '__pycache__' not in p.parts)
 for rec in manifest['records']:files.add(ROOT/rec['source'])
 for rec in manifest['figures']:files.add(ROOT/rec['source'])
 for folder in ['results/publication2027','paper/pacificvis2027-restructured']:
  files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and 'build' not in p.parts and p.suffix!='.zip')
 for name in ['README.md','pyproject.toml','data/README.md','notes/research-restructure-20261013.md','notes/layout-optimization-20261014.md','notes/archive/update_paper_evidence_legacy.txt']:
  files.add(ROOT/name)
 files.update(p for p in (ROOT/'data/geo').glob('*') if p.is_file())
 bundle=OUT/'CD-MTM-PacificVis2027-code-results.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(files):z.write(p,Path('CD-MTM')/p.relative_to(ROOT))
 artifacts={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.iterdir() if p.name.startswith('CD-MTM-PacificVis2027')}
 (OUT/'delivery_manifest.json').write_text(json.dumps(artifacts,indent=2)+'\n')
 print('Packaged PDFs, standalone LaTeX, and reproducible code/results bundle.')
if __name__=='__main__':main()
