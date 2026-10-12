"""Generate every standalone subplot without rendering composite images."""
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
for group in sorted([*ROOT.glob('fig[1-6]'), *ROOT.glob('supp_*')]):
    for script in sorted(group.glob('*.py')):
        if script.stem == 'era5_2014': continue  # archived sequence, excluded from revised paper
        print(f'Generating {group.name}/{script.stem}', flush=True)
        runpy.run_path(str(script), run_name='__main__')
