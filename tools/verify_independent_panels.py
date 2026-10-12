"""Prove that all panel entry points draw data without reading finished images.

Block repository PDF/PNG/JPEG inputs, run each panel on its own figure,
record its numeric image arrays and vector marks, and save verification PNGs
under tmp/. Existing paper figures are not modified.
"""
import json
import os
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
PANELS = ROOT / 'analysis/panels'
OUT = ROOT / 'tmp/independent-panel-verification'
sys.path.insert(0, str(PANELS))


def reject_finished_image_input(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    mode, flags = args[1:3]
    writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(
        isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR))
    if path.is_relative_to(ROOT) and path.suffix.lower() in (
            '.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff') and not writing:
        raise AssertionError('Finished-image input is forbidden: ' + str(path))


sys.addaudithook(reject_finished_image_input)
import common

records = []


def verify_save(fig, group, stem):
    common.clean_axes(fig)
    assert len(fig.axes) == 1, (group, stem, len(fig.axes))
    ax = fig.axes[0]
    assert not ax.texts and ax.get_legend() is None and not ax.axison
    assert not ax.get_title() and not ax.get_xlabel() and not ax.get_ylabel()
    arrays = [im.get_array() for im in ax.images]
    # Heatmaps here are scalar matrices, not RGB/RGBA screenshot arrays.
    assert all(a.ndim == 2 and a.dtype.kind in 'fiu' for a in arrays)
    if any(min(a.shape) > 1 for a in arrays):
        assert all(line.get_gid() == 'coastline' for line in ax.lines)
        assert not ax.collections and not ax.patches
    record = {'script': f'analysis/panels/{group}/{stem}.py',
              'axes': len(fig.axes),
              'scalar_matrix_shapes': [list(a.shape) for a in arrays],
              'vector_lines': len(ax.lines), 'vector_patches': len(ax.patches),
              'text_labels': len(ax.texts),
              'finished_image_input': False}
    destination = OUT / group
    destination.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination / (stem + '.png'), dpi=100, bbox_inches='tight')
    common.plt.close(fig)
    records.append(record)


common.save = verify_save
for group in sorted([*PANELS.glob('fig[1-6]'), *PANELS.glob('supp_*')]):
    for script in sorted(group.glob('*.py')):
        if script.stem == 'era5_2014': continue
        print('Verifying', group.name, script.name, flush=True)
        runpy.run_path(str(script), run_name='__main__')
assert len(records) == 51
assert sum('/fig1/' in r['script'] for r in records) == 12
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'report.json').write_text(json.dumps(records, indent=2) + '\n')
print('PASS: 51 independent one-axis figures, including 12 for Figure 1;')
print('all ran with repository finished-image reads forbidden.')
print(OUT / 'report.json')
