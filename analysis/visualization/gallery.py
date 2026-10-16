"""Build the scientific figure gallery with PNG, PDF and editable SVG exports."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'analysis'), str(ROOT / 'src')]
import figstyle as fs
from dataset_suite import PAPER_DATASETS, REAL_DATASETS, LABELS
from .catalog import METHODS, motion_row
from .rendering import temporal_maps, fingerprint
from .spatial import spatial_topology, curve_fragmentation
from .metrics import motion_errors, topology_motion, neighbourhoods, motion_sensitivity

UNITS = dict(olr='W m⁻²', pm25='µg m⁻³', era5='hPa', wildfire='log(1+FRP)', ring='scalar value', gaussians='scalar value')


class Exporter:
    def __init__(self, directory):
        self.directory = Path(directory); self.directory.mkdir(parents=True, exist_ok=True)
        self.items = []
        self.book = PdfPages(self.directory / 'visualization-gallery.pdf')

    def save(self, figure, stem, caption):
        files = {}
        for extension in ('png', 'pdf', 'svg'):
            path = self.directory / f'{stem}.{extension}'
            figure.savefig(path, dpi=300)
            files[path.name] = sha256(path.read_bytes()).hexdigest()
        self.items.append(dict(stem=stem, caption=caption, files=files))
        self.book.savefig(figure)
        plt.close(figure)
        print('Generated', stem, flush=True)


def temporal_comparison(dataset, records, export):
    name = dataset['name']; matrices = temporal_maps(dataset)
    fig, axs = plt.subplots(3, 2, figsize=(7, 5.4), layout='constrained')
    low, high = float(dataset['sc']['fields'].min()), float(dataset['sc']['fields'].max())
    for ax, method in zip(axs.flat, METHODS):
        data = matrices[method.key]
        im = ax.imshow(data, origin='lower', aspect='auto', cmap=fs.FIELD_CMAP,
                       vmin=low, vmax=high, extent=(-.5, data.shape[1]-.5, 0, 1))
        row = motion_row(records[name], method.key)
        error = f'{100*row["error"]:.1f}%' if row.get('clear') else 'undefined'
        ax.set(title=f'{method.label} · error {error} · {data.shape[0]} rows',
               xlabel='time step', ylabel='linearized coordinate (normalized)', yticks=[0, .5, 1])
    fig.colorbar(im, ax=list(axs.flat), shrink=.75, label=UNITS[name])
    fig.suptitle(f'{LABELS[name]}: six-method temporal comparison · common scalar color scale', fontsize=10)
    export.save(fig, f'{name}_temporal_methods',
        'Common processed fields, scalar range and time axis. Vertical axes are normalized separately; '
        'native Hilbert/Morton sample ranks do not represent geographical coordinates. '
        'R uses optimal barrier filling. Actual row counts are disclosed; no scalar-value rescaling is used.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--datasets', nargs='+', choices=PAPER_DATASETS, default=['olr', 'pm25'])
    parser.add_argument('--metrics-only', action='store_true', help='Draw saved-record charts without raw inputs')
    parser.add_argument('--out', type=Path, default=ROOT / 'results/visualizations')
    args = parser.parse_args(argv); fs.apply()
    matplotlib.rcParams.update({'svg.fonttype': 'none', 'svg.hashsalt': 'rgmtm-gallery'})
    path = ROOT / 'results/eval_projection.json'; records = json.loads(path.read_text())
    for name in PAPER_DATASETS:
        for method in METHODS:
            if method.key not in records[name]['hidden']:
                raise ValueError(f'Missing completed evidence for {name}: {method.key}')
    export = Exporter(args.out); dataset_hashes = {}
    if not args.metrics_only:
        import replicate as rp
        for name in dict.fromkeys(args.datasets):
            print('Loading', name, flush=True); dataset = rp.LOADERS[name]()
            dataset_hashes[name] = fingerprint(dataset)
            spatial_topology(dataset, LABELS[name], UNITS[name], export)
            temporal_comparison(dataset, records, export)
            curve_fragmentation(dataset, LABELS[name], UNITS[name], export)
    motion_errors(records, PAPER_DATASETS, LABELS, export)
    topology_motion(records, REAL_DATASETS, LABELS, export)
    neighbourhoods(records, PAPER_DATASETS, LABELS, export)
    motion_sensitivity(records, PAPER_DATASETS, LABELS, export)
    export.book.close()
    manifest = dict(datasets=list(args.datasets), methods=[m.key for m in METHODS],
        metrics_only=args.metrics_only, evidence_sha256=sha256(path.read_bytes()).hexdigest(),
        dataset_fingerprints=dataset_hashes, figures=export.items,
        booklet_sha256=sha256((args.out / 'visualization-gallery.pdf').read_bytes()).hexdigest(),
        source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                       for p in sorted((ROOT / 'analysis/visualization').glob('*.py'))})
    (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Dataset and method visualization gallery', '',
        'Generated from processed scalar arrays and saved experiment JSON, never from existing screenshots.', '',
        'Six methods: TMTM, ST-MTM, RG-MTM-P, RG-MTM-R (κ=20%), Hilbert, Morton. Main PM2.5: January 1–30, 2000, '
        'selected after seasonal exploration; seven clear events do not establish general superiority.', '',
        '[Combined figure booklet](visualization-gallery.pdf)', '',
        'Reproduce: `PYTHONPATH=src:analysis python3 -m visualization.gallery`', '',
        'Raw-data-free quantitative subset: add `--metrics-only`. PDF and SVG accompany each PNG; '
        'SVG keeps editable axes, labels and vector marks. Scalar images remain embedded rasters.', '']
    for item in export.items:
        stem = item['stem']; lines += [f'## {stem}', '', item['caption'], '',
            f'[PDF]({stem}.pdf) · [SVG]({stem}.svg)', '', f'![{stem}]({stem}.png)', '']
    (args.out / 'README.md').write_text('\n'.join(lines))
    print('Gallery:', args.out, '·', len(export.items), 'figures', flush=True)


if __name__ == '__main__':
    main()
