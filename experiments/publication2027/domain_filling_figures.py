"""Render and independently verify a synthetic full-domain filling illustration.

This supplements the method description; it does not rerun real-data experiments.
Run from RG-MTM: PYTHONPATH=src:analysis python experiments/publication2027/domain_filling_figures.py
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'analysis')]
from rgmtm.baselines.stmtm import AugmentedMergeTreeFrame, TreeArc, DiscreteSkeleton, fill_frame
from attainable import Filling, lca_matrix
from filling import barriers, optimal_fill
import figstyle as fs

OUT = ROOT / 'results/legacy_publication/pacificvis2027-restructured/figures'
DATA = ROOT / 'results/publication2027/figure_data'
LEAVES = [r'$A_1$', r'$A_2$', 'B', 'C', 'D']
COLORS = [fs.BLUE, fs.BLUE_LIGHT, fs.CORAL, fs.GREEN, fs.ORANGE]
XY = {0: (0., 0.), 1: (1., 0.), 2: (2., 0.), 3: (3., 0.), 4: (4., 0.),
      5: (.5, 2.), 6: (1.25, 4.), 7: (3.5, 3.), 8: (2.3, 8.)}


def save(fig, stem, out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    for ext in ('pdf', 'png', 'svg'):
        fig.savefig(out / f'{stem}.{ext}', dpi=300)
    plt.close(fig)


def example():
    children = {8: (6, 7), 6: (5, 2), 5: (0, 1), 7: (3, 4),
                0: (), 1: (), 2: (), 3: (), 4: ()}
    parent = {c: p for p, cs in children.items() for c in cs}
    values = [0., 0., 0., 0., 0., 2., 4., 3., 8.]
    coords = [XY[i] for i in range(9)]
    arcs = {}
    for c, p in parent.items():
        regular = []
        for fraction in (1 / 3, 2 / 3):
            regular.append(len(values))
            values.append((1 - fraction) * values[c] + fraction * values[p])
            coords.append(tuple((1 - fraction) * np.asarray(XY[c]) + fraction * np.asarray(XY[p])))
        arcs[c] = TreeArc(c, c, p, np.asarray(regular, int))
    coords = np.asarray(coords)
    return AugmentedMergeTreeFrame(0, 8, children, arcs, np.asarray(values), coords,
                                   coords.min(0), coords.max(0))


def feasible_gap_witnesses(P, leaf, delta):
    """Independent feasibility: select a gap witnessing each pair's lower bound.

    Every gap has upper bound P_ij+delta for every spanning pair, and leaf lower
    bounds. Exhaustive witness choices avoid calling either cost implementation.
    """
    n = len(leaf)
    pairs = list(itertools.combinations(range(n), 2))
    lo = np.maximum(leaf[:-1], leaf[1:])
    hi = np.array([min(P[i, j] + delta for i, j in pairs if i <= k < j)
                   for k in range(n - 1)])
    if np.any(lo > hi + 1e-10):
        return False
    for choice in itertools.product(*(range(i, j) for i, j in pairs)):
        bound = lo.copy()
        for (i, j), k in zip(pairs, choice):
            bound[k] = max(bound[k], P[i, j] - delta)
        if np.all(bound <= hi + 1e-10):
            return True
    return False


def render_checked(frame):
    anchors = np.array([10, 30, 50, 70, 90])
    profiles = []
    V = lca_matrix(frame, list(range(5)), 'join')
    O = np.asarray(list(itertools.permutations(range(5))))
    batch = Filling(5).delta(O, V)
    scalar = np.array([barriers(list(o), frame, 1.)[1] for o in O])
    np.testing.assert_allclose(batch, scalar, atol=1e-12)
    for order in [(0, 1, 2, 3, 4), (0, 1, 3, 2, 4)]:
        sk = DiscreteSkeleton(order, anchors, anchors - 4, anchors + 4)
        initial = fill_frame(frame, sk, 101)
        corrected, delta = optimal_fill(initial, list(order), anchors, frame, 'join')
        b, _ = barriers(order, frame, 1.)
        P = V[np.ix_(order, order)]
        measured = max(abs(max(corrected[anchors[i]:anchors[j] + 1]) - P[i, j])
                       for i, j in itertools.combinations(range(5), 2))
        np.testing.assert_allclose(measured, delta, atol=1e-12)
        np.testing.assert_allclose(corrected[anchors], frame.values[list(order)], atol=1e-12)
        assert feasible_gap_witnesses(P, frame.values[list(order)], delta)
        if delta > 0:
            assert not feasible_gap_witnesses(P, frame.values[list(order)], delta - 1e-5)
        profiles.append(dict(order=order, anchors=anchors, starts=sk.starts, ends=sk.ends,
                             initial=initial, corrected=corrected, barriers=b,
                             delta=float(delta), measured=float(measured)))
    return profiles


def node_correspondence(frame, profile):
    """Trace named samples through the actual nearest-index resampling.

    r1 is on A1's leaf arc; r2 is on the internal A-to-(A,B) arc.
    This trace describes the tree-consistent example, not a general bijection.
    """
    from rgmtm.baselines.stmtm import _alternating_positions
    r1 = int(frame.arc_for_child(0).regular_vertices[0])
    r2 = int(frame.arc_for_child(5).regular_vertices[0])
    positions = np.asarray(_alternating_positions(int(profile['anchors'][0]),
                           int(profile['starts'][0]), int(profile['ends'][0])))
    indices = np.rint(np.linspace(0, 1, len(positions))).astype(int)
    r1_pixels = sorted(positions[indices == 0].tolist())
    # Between A2 and B there is exactly one internal arc (node 5 -> node 6).
    # The LCA occupies the last gap pixel; the remaining ten pixels sample it.
    gap = np.arange(int(profile['ends'][1]) + 1, int(profile['starts'][2]))
    indices = np.rint(np.linspace(0, 1, len(gap) - 1)).astype(int)
    r2_pixels = gap[:-1][indices == 0].tolist()
    lo, hi = profile['ends'][0] + 1, profile['starts'][1]
    merge_pixel = int((lo + hi - 1) // 2)
    result = dict(r1=dict(source_node=r1, scalar=float(frame.values[r1]), pixels=r1_pixels),
                  r2=dict(source_node=r2, scalar=float(frame.values[r2]), pixels=r2_pixels),
                  S=dict(source_node=5, scalar=2., pixels=[merge_pixel]))
    for name, item in result.items():
        np.testing.assert_allclose(profile['initial'][item['pixels']], item['scalar'], atol=1e-12,
                                   err_msg=f'{name} source-to-pixel mismatch')
    return result


def draw_tree(ax, frame):
    for arc in frame.arcs.values():
        nodes = [arc.child, *arc.regular_vertices, arc.parent]
        xy = frame.coordinates[nodes]
        ax.plot(xy[:, 0], xy[:, 1], color=fs.GRAY, lw=.8, zorder=1)
        regular = frame.coordinates[arc.regular_vertices]
        ax.scatter(regular[:, 0], regular[:, 1], s=7, facecolors='white', edgecolors=fs.GRAY_DARK,
                   linewidths=.5, zorder=2)
    for i in range(5):
        ax.scatter(*XY[i], s=22, color=COLORS[i], marker='D', zorder=3)
        ax.text(XY[i][0], -.6, LEAVES[i], ha='center', fontsize=8)
    for i in (5, 6, 7, 8):
        ax.scatter(*XY[i], s=24, color=fs.GRAY_DARK, marker='s', zorder=3)
        label = 'S: 2' if i == 5 else str(int(frame.values[i]))
        ax.annotate(label, XY[i], xytext=(5, 1), textcoords='offset points', fontsize=7)
    for child, text, offset in [(0, r'$r_1$', (-16, 1)), (5, r'$r_2$', (-18, 3))]:
        node = frame.arc_for_child(child).regular_vertices[0]
        ax.annotate(text, frame.coordinates[node], xytext=offset, textcoords='offset points', fontsize=7)
    ax.plot([-.1, -.1, 1.1, 1.1], [-.8, -1., -1., -.8], color=fs.BLUE, lw=.65)
    ax.text(.5, -1.6, r'$A=\{A_1,A_2\}$', ha='center', color=fs.BLUE, fontsize=7)
    ax.set(xlim=(-.5, 4.6), ylim=(-1.9, 8.6))
    ax.axis('off')


def detail(frame, profiles):
    fig = plt.figure(figsize=(7, 3.3))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 2.05], left=.03, right=.985,
                          bottom=.22, top=.90, wspace=.25, hspace=.52)
    tree = fig.add_subplot(gs[:, 0])
    draw_tree(tree, frame)
    tree.set_title('(a) Augmented input tree T', pad=9)
    for row, d in enumerate(profiles):
        ax = fig.add_subplot(gs[row, 1])
        for leaf, start, end in zip(d['order'], d['starts'], d['ends']):
            ax.axvspan(start, end, color=COLORS[leaf], alpha=.12, lw=0)
        if row:
            ax.plot(20, d['corrected'][20], 's', color=fs.GRAY_DARK, ms=3.2)
            ax.plot(d['initial'], ls='--', color=fs.GRAY, lw=.8, label='Initial LCA filling')
        ax.plot(d['corrected'], color=fs.BLUE if row == 0 else fs.GREEN, lw=1.05)
        for leaf, a in zip(d['order'], d['anchors']):
            ax.plot(a, 0, 'D', color=COLORS[leaf], ms=3.2)
        ax.set(ylim=(-.3, 8.7), xlim=(0, 100), ylabel='scalar value',
               xticks=d['anchors'], xticklabels=[LEAVES[i] for i in d['order']], yticks=[0, 2, 4, 6, 8])
        ax.spines[['top', 'right']].set_visible(False)
        title = '(b) Tree-consistent order: merge error 0' if row == 0 else '(c) Interleaved order: optimal merge error 2.5'
        ax.set_title(title, loc='left', pad=5)
        for k, b in enumerate(d['barriers']):
            lo, hi = d['anchors'][k:k + 2]
            p = lo + int(np.argmax(d['corrected'][lo:hi + 1]))
            ax.annotate(f'{b:g}', (p, b), xytext=(0, 4), textcoords='offset points',
                        ha='center', fontsize=6.5, color=fs.BLUE if row == 0 else fs.GREEN)
        if row:
            ax.text(.03, .90, r'$A_1,A_2$: merge 2 $\rightarrow$ 4.5', transform=ax.transAxes,
                    color=fs.BLUE, fontsize=7, va='top', bbox=dict(fc='white', alpha=.9, ec='none', pad=1))
        else:
            trace = node_correspondence(frame, d)
            for name, offset in [('r1', (-14, 10)), ('r2', (-14, 13))]:
                item = trace[name]
                pixels = item['pixels']
                ax.plot(pixels, d['initial'][pixels], 'o', ms=3, mfc='white', mec=fs.GRAY_DARK, mew=.65)
                label = r'$r_1$' if name == 'r1' else r'$r_2$'
                mid = pixels[len(pixels) // 2]
                ax.annotate(label, (mid, d['initial'][mid]), xytext=offset, textcoords='offset points',
                            fontsize=7, arrowprops=dict(arrowstyle='-', color=fs.GRAY_DARK, lw=.5))
            for k in range(4):
                lo, hi = d['anchors'][k:k + 2]
                pixel = lo + int(np.argmax(d['initial'][lo:hi + 1]))
                ax.plot(pixel, d['initial'][pixel], 's', color=fs.GRAY_DARK, ms=3.2)
            s = trace['S']['pixels'][0]
            ax.annotate('S', (s, 2.), xytext=(8, -9), textcoords='offset points', fontsize=7, color=fs.GRAY_DARK)
    handles = [Line2D([], [], marker='D', ls='none', color=fs.BLUE, ms=4, label='leaf extremum'),
               Line2D([], [], marker='s', ls='none', color=fs.GRAY_DARK, ms=4, label='merge node'),
               Line2D([], [], marker='o', ls='none', markerfacecolor='white', color=fs.GRAY_DARK, ms=3, label='regular sample'),
               Line2D([], [], ls='--', color=fs.GRAY, lw=.8, label='initial LCA profile')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .08), ncol=4, frameon=False)
    fig.text(.5, .015, 'White r1 / r2: resampled leaf / internal arcs. Grey S: LCA barrier. Shading: leaf intervals.',
             ha='center', fontsize=6.5)
    save(fig, 'fig_full_domain_filling')


def overview(out=OUT):
    """Replace the existing method overview without changing figure numbering."""
    fig, axes = plt.subplots(1, 5, figsize=(7, 1.6))
    for ax, title in zip(axes, ['1. Input / reference', '2. Certify position', '3. Relax / layout', '4. Fill selected order', '5. Assemble / disclose']):
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis('off')
        ax.set_title(title, fontsize=7, fontweight='bold', pad=5)
    ax = axes[0]
    pts = {0: (.08, .42), 1: (.27, .42), 2: (.48, .42), 3: (.72, .42), 4: (.92, .42),
           5: (.17, .59), 6: (.35, .72), 7: (.82, .65), 8: (.58, .88)}
    for c, p in {0: 5, 1: 5, 5: 6, 2: 6, 3: 7, 4: 7, 6: 8, 7: 8}.items():
        a, b = np.asarray(pts[c]), np.asarray(pts[p]); ax.plot([a[0], b[0]], [a[1], b[1]], color=fs.GRAY, lw=.6)
        q = (a + b) / 2; ax.plot(*q, 'o', ms=2, mfc='white', mec=fs.GRAY_DARK, mew=.4)
    for i, xy in pts.items():
        ax.plot(*xy, 'D' if i < 5 else 's', ms=3, color=COLORS[i] if i < 5 else fs.GRAY_DARK)
    ax.annotate(r'$r_1$', (.125, .505), xytext=(-7, -7), textcoords='offset points', fontsize=6)
    ax.annotate('S', pts[5], xytext=(-4, 5), textcoords='offset points', fontsize=6)
    ax.text(.5, .27, r'white $r$: regular / grey S: merge', ha='center', fontsize=5.7)
    ax.text(.5, .15, r'Fields / tracks $\rightarrow d\rightarrow q_i$', ha='center', fontsize=6)
    axes[1].barh(.65, .3, left=.08, color=fs.GRAY, height=.15); axes[1].barh(.65, .45, left=.38, color=fs.CORAL, height=.15)
    axes[1].text(.5, .42, r'$\tau^*=\tau_{\rm free}+H$', ha='center', fontsize=8)
    axes[1].text(.5, .15, 'Witnesses explain conflicts', ha='center', fontsize=6)
    for y, order in [(.73, range(5)), (.50, [0, 1, 3, 2, 4])]:
        for x, leaf in zip(np.linspace(.09, .91, 5), order):
            axes[2].plot([x - .065, x + .065], [y, y], color=COLORS[leaf], lw=4, alpha=.3)
            axes[2].plot(x, y, 'D', ms=3, color=COLORS[leaf])
    axes[2].text(.5, .30, r'$T\rightarrow T\prime$, budget $B_t$', ha='center', fontsize=6.5)
    axes[2].text(.5, .15, 'Order + intervals + anchors', ha='center', fontsize=6)
    frame = example()
    profiles = render_checked(frame)
    initial = profiles[0]
    trace = node_correspondence(frame, initial)
    xx = .03 + .94 * np.arange(101) / 100
    yy = .40 + .45 * initial['initial'] / 8
    axes[3].plot(xx, yy, color=fs.BLUE, lw=.9)
    for x in xx[initial['anchors']]:
        axes[3].axvspan(x - .035, x + .035, ymin=.38, ymax=.78, color=fs.BLUE_LIGHT, alpha=.18)
    for name, label, offset in [('r1', r'$r_1$', (0, -4)), ('r2', r'$r_2$', (-1, 6))]:
        p = trace[name]['pixels'][0]
        axes[3].plot(xx[p], yy[p], 'o', ms=2.5, mfc='white', mec=fs.GRAY_DARK, mew=.5)
        axes[3].annotate(label, (xx[p], yy[p]), xytext=offset, textcoords='offset points', fontsize=6)
    for k in range(4):
        lo, hi = initial['anchors'][k:k + 2]
        p = lo + int(np.argmax(initial['initial'][lo:hi + 1]))
        axes[3].plot(xx[p], yy[p], 's', ms=2.8, color=fs.GRAY_DARK)
    p = trace['S']['pixels'][0]
    axes[3].annotate('S', (xx[p], yy[p]), xytext=(3, 4), textcoords='offset points', fontsize=6)
    axes[3].text(.5, .29, 'White samples / grey barriers', ha='center', fontsize=6.3)
    axes[3].text(.5, .15, 'Borders: root-to-leaf paths', ha='center', fontsize=6)
    corrected = profiles[1]
    axes[4].plot(xx, .70 + .15 * corrected['initial'] / 8, ls='--', color=fs.GRAY, lw=.6)
    axes[4].plot(xx, .70 + .15 * corrected['corrected'] / 8, color=fs.GREEN, lw=.9)
    p = trace['S']['pixels'][0]
    axes[4].plot(xx[p], .70 + .15 * 4.5 / 8, 's', color=fs.GRAY_DARK, ms=2.8)
    axes[4].annotate('S: 2 → 4.5', (xx[p], .70 + .15 * 4.5 / 8), xytext=(-2, 4),
                     textcoords='offset points', fontsize=5.8,
                     bbox=dict(fc='white', alpha=.9, ec='none', pad=.5))
    columns = np.repeat(corrected['corrected'][:, None], 4, axis=1)
    axes[4].imshow(columns, extent=[.16, .88, .33, .60], origin='lower', aspect='auto',
                   cmap=fs.FIELD_CMAP, vmin=0, vmax=8, interpolation='nearest')
    for x in [.34, .52, .70]:
        axes[4].plot([x, x], [.33, .60], color='white', alpha=.4, lw=.4)
    axes[4].text(.5, .23, r'$v_t\rightarrow\mathcal{V}$ + error overlays', ha='center', fontsize=5.8)
    axes[4].text(.5, .15, 'Shared scalar colors / time axis', ha='center', fontsize=5.7)
    fig.subplots_adjust(left=.015, right=.985, bottom=.01, top=.81, wspace=.24)
    for a, b in zip(axes[:-1], axes[1:]):
        ap, bp = a.get_position(), b.get_position()
        axes[-1].annotate('', xy=(bp.x0 - .004, .51), xytext=(ap.x1 + .004, .51), xycoords=fig.transFigure,
                          arrowprops=dict(arrowstyle='->', lw=.6))
    save(fig, 'fig_method_visual', out)


def main():
    fs.apply()
    plt.rcParams.update({'svg.fonttype': 'none', 'svg.hashsalt': 'rgmtm-domain-filling-20261014'})
    frame = example()
    profiles = render_checked(frame)
    trace = node_correspondence(frame, profiles[0])
    detail(frame, profiles)
    DATA.mkdir(parents=True, exist_ok=True)
    serial = [{k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in d.items()} for d in profiles]
    sources = [Path(__file__), ROOT / 'analysis/filling.py', ROOT / 'analysis/attainable.py',
               ROOT / 'src/rgmtm/baselines/stmtm.py']
    record = dict(synthetic_only=True, tree='(((A1,A2)_2,B)_4,(C,D)_3)_8', all_orders_checked=120,
                  profiles=serial, values=frame.values.tolist(), node_correspondence=trace,
                  input_samples=len(frame.values), regular_samples=sum(len(a.regular_vertices) for a in frame.arcs.values()),
                  checks=['120-order closed-form agreement', 'rendered all-pair error', 'unchanged extrema',
                          'independent optimal-budget feasibility', 'smaller positive budget infeasible',
                          'named regular samples and merge node match source-to-pixel trace'],
                  source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  figures={name: hashlib.sha256((OUT / f'{name}.pdf').read_bytes()).hexdigest()
                           for name in ['fig_full_domain_filling']})
    (DATA / 'domain_filling_example.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Full-domain figures exported; 120-order and independent feasibility checks passed.')


if __name__ == '__main__':
    main()
