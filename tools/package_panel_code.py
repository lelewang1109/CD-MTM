"""Package editable panel source and numeric inputs, with no rendered images."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / 'analysis'))
from dataset_suite import PAPER_DATASETS, RETIRED_DATASETS
OUT = ROOT / 'results/legacy_publication/pacificvis2027/figures/standalone_panel_code.zip'
paths = []
for folder in ('analysis', 'src', 'experiments'):
    paths.extend(p for p in (ROOT / folder).rglob('*.py')
                 if 'archive_oisst' not in str(p) and p.stem not in RETIRED_DATASETS)
paths.extend([ROOT / 'pyproject.toml', ROOT / 'analysis/panels/README.md',
              ROOT / 'data/README.md', ROOT / 'tools/verify_independent_panels.py',
              Path(__file__)])
for name in [f'{stage}_{dataset}' for stage in ('replicate', 'attainable') for dataset in PAPER_DATASETS]:
    paths.append(ROOT / 'results' / (name + '.json'))
paths.append(ROOT / 'results/eval_projection.json')
paths.extend(ROOT / name for name in ('results/final_performance.json', 'results/final_performance.csv', 'results/native_merge_errors.json', 'tools/update_paper_evidence.py'))
paths.append(ROOT / 'analysis/visualization/README.md')
paths.append(ROOT / 'data/geo/ne_110m_coastline.geojson')
with ZipFile(OUT, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(set(paths)):
        archive.write(path, str(path.relative_to(ROOT)))
with ZipFile(OUT) as archive:
    assert archive.testzip() is None
    assert not any(Path(name).suffix.lower() in ('.png', '.pdf', '.jpg', '.jpeg')
                   for name in archive.namelist())
    assert len([name for name in archive.namelist()
                if name.startswith('analysis/panels/fig1/') and name.endswith('.py')]) == 12
print('Source-only package (includes numeric JSON, no rendered images):', OUT)
