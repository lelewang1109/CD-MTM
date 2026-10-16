"""Shared calculations for independently generated paper subplots.

Each entry point in fig1/--fig6/ creates its own Matplotlib figure and draws
its own marks. The combined paper images are never loaded or cropped.
Calculations are reused in memory by build_all.py; individual entry points
also work on their own.
"""
from functools import lru_cache
from pathlib import Path
import sys
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'analysis'), str(ROOT / 'src'), str(ROOT)]
import task_reference as tr, figstyle as fs
import relax_hierarchy as rh, replicate as rp, filling as fl, pointcert as pc
import fig_concept as fc
from fig_witness import witness
from fig_teaser import tracks
from experiments import era5 as ep

plt = tr.plt
OUT = ROOT / 'results/legacy_publication/pacificvis2027/figures/panels'
KAPPA = .2
W0, W1, TZ = 38, 57, 48
ROOT_NC = ROOT / 'data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114_12h_arco.nc'
COAST = ROOT / 'data/geo/ne_110m_coastline.geojson'

@lru_cache(maxsize=1)
def prepare_teaser():
    ds = rp.LOADERS['era5'](); sc = ds['sc']; kind = sc['trees'][0].kind; T = len(sc['ids'])
    lo, hi = np.quantile(sc['fields'], [0, 1])
    base = rh.run(ds, 0., make_figure=False, return_internal=True); I0 = base['_internal']; p = I0['p']; ref = I0['ref']
    L = p.canvas; theta = base['theta']
    R = rh.run(ds, KAPPA, make_figure=False, return_internal=True)
    rowsA = I0['results']['A_full_hierarchy']['_rows']; mapsA = I0['results']['A_full_hierarchy']['_maps']
    rowsR = R['_internal']['results']['R_relaxed']['_rows']
    mapsR, dskR, _ = rh.render(sc, rowsR, p, ds['nominal'])
    optR = mapsR.astype(float).copy(); dstar = []
    for t, (fr, sk) in enumerate(zip(sc['frames'], dskR)):
        optR[:, t], d = fl.optimal_fill(mapsR[:, t], list(sk.ordering), sk.anchors, fr, kind); dstar.append(d)
    # ST-MTM in its own model
    span = ds['native_span']
    px = rh.gm.Parameters(canvas=span, canvas_origin=float(min(ds['lo'][0], 0.)), width_scale=.5 * span / ds['domain_area'],
                          gap=span / 240, extra_budget=span / 120, rho=.5)
    st = ep.run_method(sc, 'ST-MTM', px, canvas=span, length=ds['nominal'], refine_raster=False, strict_checks=False)
    Ust = [np.asarray(r['pixel_x'], float) for r in st['rows']]
    cert_pt = []; st_pt = []
    for t in range(T):
        q = np.asarray(ref['qs'][t])
        cert_pt.append(float(pc.tau_pt(rh.leaf_orders(sc['hier'][t]), q).min()))
        st_pt.append(float(pc.tau_pt([np.argsort(Ust[t], kind='stable')], q)[0]))
    log = base['frame_log']
    H = np.array([d['tau_hier'] - d['tau_free'] for d in log]); F = np.array([d['tau_free'] for d in log])
    errR = np.array([np.max(abs(r['x'] - r['reference'])) for r in rowsR])


    t = np.arange(T)
    ymax = max(np.max(st_pt), np.max(H + F)) / L * 105
    SN = [5, 26, 48, 62, 108]
    return locals()

@lru_cache(maxsize=1)
def prepare_witness():
    ds = rp.LOADERS['era5'](); sc = ds['sc']; kind = sc['trees'][0].kind
    base = rh.run(ds, 0., make_figure=False, return_internal=True); I0 = base['_internal']; p = I0['p']; ref = I0['ref']
    L = p.canvas; theta = base['theta']; lo, hi = np.quantile(sc['fields'], [0, 1])
    R = rh.run(ds, KAPPA, make_figure=False, return_internal=True); IR = R['_internal']
    rowsA = I0['results']['A_full_hierarchy']['_rows']; mapsA = I0['results']['A_full_hierarchy']['_maps']
    rowsR = IR['results']['R_relaxed']['_rows']; mapsR, dskR, _ = rh.render(sc, rowsR, p, ds['nominal'])
    optR = mapsR.astype(float).copy(); dst = []
    for t, (f_, sk) in enumerate(zip(sc['frames'], dskR)):
        optR[:, t], d = fl.optimal_fill(mapsR[:, t], list(sk.ordering), sk.anchors, f_, kind); dst.append(d)
    log = base['frame_log']; H = np.array([d['tau_hier'] - d['tau_free'] for d in log])
    W = {t: witness(sc['frames'][t], sc['ids'][t], np.asarray(ref['qs'][t])) for t in range(W0, W1) if H[t] > theta}
    tz = TZ   # conflict step whose witness triple lies in the domain interior (see analysis/boundary.py)


    ext = [W0 - .5, W1 - .5, p.canvas_origin, p.canvas_origin + L]
    tt = np.arange(W0, W1)
    b, (i, j, k) = W[tz]
    q = np.asarray(ref['qs'][tz])
    u = rowsA[tz]['x']
    return locals()

@lru_cache(maxsize=1)
def prepare_concept():
    g, X, Y, f = fc.field(); vals, merges, idx = fc.merge_values(g, f)
    sAB = [m for m in merges if m[1] | m[2] == frozenset('AB')]
    sAB = sAB[0][0] if sAB else merges[0][0]; sRoot = max(m[0] for m in merges)
    gamma = sRoot - sAB

    q = {k: g[idx[k][1]] for k in fc.P}
    w, gap = 1.0, .2
    tau = (w + gap + q['B'] - q['C']) / 2
    u = dict(A=q['A'], B=q['B'] - tau, C=q['C'] + tau)
    return locals()

@lru_cache(maxsize=1)
def prepare_price():
    g, X, Y, f = fc.field(); vals, merges, idx = fc.merge_values(g, f)
    sAB = [m for m in merges if m[1] | m[2] == frozenset('AB')][0][0]; sR = max(m[0] for m in merges); gam = sR - sAB
    q = {k: g[idx[k][1]] for k in fc.P}; w, gap = 1.0, .2; tau = (w + gap + q['B'] - q['C']) / 2
    uA = dict(A=q['A'], B=q['B'] - tau, C=q['C'] + tau)
    xx = np.linspace(0, 10, 800); top = sR + .12; lo = min(vals.values()) - .12
    cases = [('(a) tree kept: A B C', ['A', 'B', 'C'], uA, {('A', 'B'): sAB, ('B', 'C'): sR}, 0., tau),
             ('(b) A C B, LCA filling', ['A', 'C', 'B'], q, {('A', 'C'): sR, ('C', 'B'): sR}, gam, 0.),
             ('(c) A C B, optimal filling', ['A', 'C', 'B'], q, {('A', 'C'): sAB + gam / 2, ('C', 'B'): sAB + gam / 2}, gam / 2, 0.)]

    return locals()

def canvas(width, height):
    fs.apply()
    fig, ax = plt.subplots(figsize=(width, height))
    return fig, ax

def clean_axes(fig):
    """Export only visual content, without annotation or scalar-map overlays.

    Keep the numeric data and existing drawing routines. Geographic scalar
    maps retain coastlines; other 2-D scalar maps retain only the color field.
    Line/bar/tree panels retain their primary geometry, without text or axes.
    """
    from matplotlib.patches import FancyArrowPatch
    for ax in fig.axes:
        if ax.get_legend() is not None:
            ax.get_legend().remove()
        for artist in list(ax.texts):
            artist.remove()
        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_axis_off()
        scalar_map = any(min(im.get_array().shape[:2]) > 1 for im in ax.images)
        if scalar_map:
            for line in list(ax.lines):
                if line.get_gid() != 'coastline':
                    line.remove()
            for artist in list(ax.collections) + list(ax.patches):
                artist.remove()
        else:
            for artist in list(ax.patches):
                if isinstance(artist, FancyArrowPatch):
                    artist.remove()


def save(fig, group, stem):
    clean_axes(fig)
    folder = OUT / group
    folder.mkdir(parents=True, exist_ok=True)
    # Tight bounds concern this subplot's own canvas, not a composite crop.
    for suffix in ('pdf', 'png'):
        fig.savefig(folder / f'{stem}.{suffix}', dpi=300,
                    bbox_inches='tight', pad_inches=0, facecolor='white')
    plt.close(fig)

def time_marks(ax, sc, times):
    import matplotlib.patheffects as pe
    for k, tt in enumerate(times):
        ax.axvline(tt, color='w', lw=.6, ls=':')
        ax.text(tt, ax.get_ylim()[1], str(k + 1), color='w', fontsize=6,
                ha='center', va='top', fontweight='bold',
                path_effects=[pe.withStroke(linewidth=1.2, foreground='k')])

from matplotlib.patches import Rectangle
T0 = 62
COL = ['#0072b2', '#d55e00', '#009e73', '#cc79a7', '#e69f00', '#56b4e9', '#999999', '#f0e442']

def branch_nodes(fr, k):
    """Skip unary chains: return the next branching node or leaf below k."""
    while len(fr.children[k]) == 1: k = fr.children[k][0]
    return k


def draw_tree(ax, fr, xpos, flat=(), lw=1.2):
    """Elbow dendrogram with y = merge value; internal x = mean of leaf x; flattened nodes dashed red."""
    def rec(k):
        k = branch_nodes(fr, k)
        ch = fr.children[k]
        if not ch: return xpos[k], [xpos[k]]
        xs = []; pts = []
        for c in ch:
            cx, lx = rec(c); c2 = branch_nodes(fr, c); pts.append((cx, float(fr.values[c2]))); xs += lx
        x = float(np.mean(xs)); y = float(fr.values[k]); style = dict(color='#c0392b', ls='--') if k in flat else dict(color='k')
        for cx, cy in pts: ax.plot([cx, cx], [cy, y], color='k', lw=lw)
        ax.plot([min(p[0] for p in pts), max(p[0] for p in pts)], [y, y], lw=lw, **style)
        if k in flat: ax.text(x, y, ' γ', color='#c0392b', fontsize=7, va='bottom')
        return x, xs
    rec(fr.root)


def layout_row(ax, row, q, y, cols, L, origin):
    for i in range(len(q)):
        z, w, u = row['z'][i], row['w'][i], row['x'][i]
        ax.add_patch(Rectangle((z - w / 2, y - .12), w, .24, color=cols[i], alpha=.55, lw=0))
        ax.plot(u, y, 'o', color=cols[i], ms=3.5, mec='k', mew=.4)
        ax.plot([u, q[i]], [y + .12, 1 - .05], color=cols[i], lw=.8)
        ax.plot(q[i], 1, 'v', color=cols[i], ms=4)
    ax.plot([origin, origin + L], [1, 1], color='k', lw=.6); ax.plot([origin, origin + L], [y, y], color='#bbbbbb', lw=.4)
    ax.set_xlim(origin - .02 * L, origin + 1.02 * L); ax.set_ylim(-.35, 1.35); ax.set_yticks([])
    ax.text(origin, 1.12, 'reference q', fontsize=6.5); ax.text(origin, y - .32, '1-D layout', fontsize=6.5)



@lru_cache(maxsize=1)
def prepare_pipeline():
    state = prepare_witness()
    ds, sc, kind, base, I0, p, ref, L, R, IR = [state[k] for k in ['ds','sc','kind','base','I0','p','ref','L','R','IR']]
    t = T0; fr = sc['frames'][t]; ids = sc['ids'][t]; q = np.asarray(ref['qs'][t]); n = len(ids)
    lg0 = base['frame_log'][t]; lgR = R['frame_log'][t]
    rowA = I0['results']['A_full_hierarchy']['_rows'][t]; rowR = IR['results']['R_relaxed']['_rows'][t]
    cols = {i: COL[r] for r, i in enumerate(np.argsort(q))}                           # colour by reference rank
    cl = [cols[i] for i in range(n)]
    flat = [s['node'] for s in lgR['steps']]
    rowsR = IR['results']['R_relaxed']['_rows']
    maps, dsk, npx = rh.render(sc, rowsR, p, ds['nominal'])
    opt = maps.astype(float).copy(); dst = []
    for tt, (f_, sk) in enumerate(zip(sc['frames'], dsk)):
        opt[:, tt], d = fl.optimal_fill(maps[:, tt], list(sk.ordering), sk.anchors, f_, kind); dst.append(d)


    w0, w1 = max(0, t - 18), min(len(rowsR), t + 4)
    tt_ = np.arange(w0, w1)
    return locals()

@lru_cache(maxsize=1)
def prepare_dendrogram():
    from scipy.cluster.hierarchy import optimal_leaf_ordering, leaves_list
    from generality import cells, dendro, linkage, Parameters, th
    X, xy = cells(); n = len(X)
    c = xy - xy.mean(0); a = np.linalg.eigh(c.T @ c)[1][:, -1]; proj = c @ a
    if np.corrcoef(proj, xy[:, 1])[0, 1] < 0: proj = -proj                      # orient north-ish upward
    q = (proj - proj.min()) / np.ptp(proj) * (n - 1) + .5
    Xc = X - X.mean(1, keepdims=True); Xc /= np.maximum(np.linalg.norm(Xc, axis=1, keepdims=True), 1e-12)
    Z = optimal_leaf_ordering(linkage(Xc, 'average'), Xc)
    olo = leaves_list(Z)
    p = Parameters(canvas=float(n), canvas_origin=0., width_scale=1., gap=0., rho=0., extra_budget=0.)
    tau = th.dp_tau(np.ones(n), q, dendro(Z), p, n, tol=.25)
    disp_olo = np.abs(np.arange(n) + .5 - q[olo]); ref = np.argsort(q); disp_ref = np.abs(np.arange(n) + .5 - q[ref])

    return locals()
