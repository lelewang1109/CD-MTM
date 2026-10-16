"""Synchronize paper figures and package independently generated panels."""
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
from dataset_suite import RETIRED_DATASETS
PAPER = ROOT / 'results/legacy_publication/pacificvis2027/figures'
SOURCES = ROOT / 'analysis/panels'
NAMES = ('fig_teaser', 'fig_concept', 'fig_topo_price', 'fig_rq1',
         'fig_frontier_exact', 'fig_witness', 'fig_pipeline', 'dendrogram_demo')
for name in NAMES:
    source = ROOT / 'results' / f'{name}.pdf'
    if source.is_file():
        shutil.copy2(source, PAPER / source.name)
shutil.copy2(SOURCES / 'README.md', PAPER / 'panels/README.md')
archive_path = PAPER / 'standalone_panels.zip'
with ZipFile(archive_path, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(SOURCES.rglob('*')):
        if path.is_file() and path.suffix in ('.py', '.md') and 'archive_oisst' not in str(path) and path.stem not in RETIRED_DATASETS:
            archive.write(path, 'code/' + str(path.relative_to(SOURCES)))
    for path in sorted((PAPER / 'panels').rglob('*')):
        if path.is_file() and path.suffix in ('.pdf', '.png', '.md') and path.stem not in RETIRED_DATASETS:
            archive.write(path, 'figures/' + str(path.relative_to(PAPER / 'panels')))
with ZipFile(archive_path) as archive:
    assert archive.testzip() is None
print(archive_path)
