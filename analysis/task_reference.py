"""Shared scalar-reference solvers and synthetic scenes for the paper evaluation.

This module contains reusable utilities only. The earlier X/Y comparison driver
is intentionally excluded from the final-paper project.
"""
from pathlib import Path
import sys
from itertools import permutations
from dataclasses import replace
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from experiments import era5 as ep
from experiments.ring.dataset import generate
from cdmtm.error_budget import (Parameters, solve_frame, solve_sequence, constraints,
                                checked_lp, leaf_orders, InfeasibleLayout)
from cdmtm.reference_anchored import render_sequence
from cdmtm.reference_points import reference_points_from_frames

OUT = ROOT / 'results'
plt = ep.plt


# ---------------------------------------------------------------- solving
def solve_scalar_reference(sc, qs, p):
    """solve_sequence with an explicit scalar reference per leaf (same temporal logic)."""
    rows = []
    for t, (c, a, h, ids, q) in enumerate(zip(sc['centers'], sc['areas'], sc['hier'], sc['tracks'], qs)):
        previous = previous_q = mask = None
        if t:
            lookup = {k: i for i, k in enumerate(sc['tracks'][t - 1])}
            mask = np.array([k in lookup for k in ids])
            previous = np.zeros(len(ids)); previous_q = np.zeros(len(ids))
            for i, k in enumerate(ids):
                if mask[i]:
                    j = lookup[k]; previous[i] = rows[-1]['x'][j]; previous_q[i] = rows[-1]['reference'][j]
        row = solve_frame(c, a, h, previous, previous_q, p, mask, reference=np.asarray(q, float))
        row['feature_ids'] = list(ids)
        rows.append(row)
    return rows


def lp_tau(w, q, order, p):
    n = len(w)
    A, b, bounds = constraints(w, order, p)
    L = np.c_[-A, np.zeros(len(A))]
    E = np.c_[np.eye(n), np.zeros((n, n)), -np.ones(n)]
    F = np.c_[-np.eye(n), np.zeros((n, n)), -np.ones(n)]
    r = checked_lp(np.r_[np.zeros(2 * n), 1.], np.vstack([L, E, F]), np.r_[-b, q, -q], bounds + [(0, None)])
    return None if r is None else float(r.fun)


def free_tau(w, q, p, exact_limit=7):
    """Min-max reference deviation over ALL leaf orders (hierarchy dropped)."""
    n = len(w)
    orders = permutations(range(n)) if n <= exact_limit else [tuple(np.argsort(q))]
    vals = [v for o in orders if (v := lp_tau(w, q, o, p)) is not None]
    return (min(vals) if vals else None), n <= exact_limit


# -------------------------------------------------------------- rendering
def render_checked(sc, rows, p, length):
    attempts = []
    while True:
        try:
            maps, ds, errors = render_sequence(sc['frames'], sc['ids'], rows, p.canvas, length,
                                               canvas_origin=p.canvas_origin)
        except ValueError as e:
            if 'increase resolution' not in str(e) or length >= 131072: raise
            attempts.append(dict(length=length, reason='raster')); length *= 2; continue
        bad = [t for t, tr in enumerate(sc['trees']) if ep.signature(maps[:, t], tr.kind) != ep.signature(tr)]
        attempts.append(dict(length=length, topology_failed=bad))
        if not bad: return maps, ds, errors, length, attempts
        if length >= 131072: raise RuntimeError('topology mismatch persists')
        length *= 2


def validate(sc, rows, p):
    """Collaborator's invariants from experiments/public.py::solve_view."""
    for t, (r, a, h) in enumerate(zip(rows, sc['areas'], sc['hier'])):
        o = np.array(r['order'])
        assert tuple(o) in leaf_orders(h), t
        assert np.allclose(r['w'], p.width_scale * a, rtol=0, atol=1e-12), t
        assert np.min(r['z'] - r['w'] / 2) >= p.canvas_origin - 1e-6, t
        assert np.max(r['z'] + r['w'] / 2) <= p.canvas_origin + p.canvas + 1e-6, t
        assert np.all(abs(r['x'] - r['z']) <= p.rho * r['w'] / 2 + 1e-6), t
        assert np.all(np.diff(r['z'][o]) - (r['w'][o[:-1]] + r['w'][o[1:]]) / 2 >= p.gap - 1e-6), t
        assert np.max(abs(r['x'] - r['reference'])) <= r['budget'] + 1e-6, t
        assert r['tau'] - 1e-6 <= np.max(abs(r['x'] - r['reference'])), t


def summarize(sc, rows, p, span_for_norm):
    per = []
    for t, (r, a) in enumerate(zip(rows, sc['areas'])):
        e = r['x'] - r['reference']
        tf, exact = free_tau(p.width_scale * np.asarray(a), r['reference'], p)
        per.append(dict(t=t, leaves=len(a), tau_hier=r['tau'], tau_free=tf, tau_free_exact=exact,
                        max_abs_err=float(np.max(abs(e))), mean_abs_err=float(np.mean(abs(e))),
                        total_width=float(np.sum(r['w']))))
    errs = np.concatenate([abs(r['x'] - r['reference']) for r in rows])
    hc = [d['tau_hier'] - d['tau_free'] for d in per if d['tau_free'] is not None]
    return dict(per_frame=per,
                reference_nmae=float(errs.mean() / span_for_norm),
                reference_p95_norm=float(np.quantile(errs, .95) / span_for_norm),
                tau_max=float(max(d['tau_hier'] for d in per)),
                frames_with_conflict=int(sum(d['tau_hier'] > 1e-6 for d in per)),
                frames_with_hierarchy_cost=int(sum(x > 1e-6 for x in hc)),
                hierarchy_cost_max=float(max(hc)) if hc else None)


# ----------------------------------------------------------------- scenes
def ring_scene():
    fields, coords, meta = generate()
    sc = ep.scene_from_fields(fields, coords, 210 ** 2 / 196, 'split')
    centre = np.array(meta['actual_float32_property_values']['center'])
    ext = reference_points_from_frames(sc['frames'], sc['ids'], kind='extremum')
    qs = [np.linalg.norm(e - centre, axis=1) for e in ext]
    span = 210.
    base = replace(ep.P, canvas=span, width_scale=1 / (2 * span), rho=.5, gap=.5 * span / 120, extra_budget=span / 120)
    rmax = float(np.ceil(np.max(np.linalg.norm(coords - centre, axis=1))))
    p_ref = replace(base, canvas=rmax)
    radius = np.array([meta['actual_float32_property_values']['mu0'] + t * meta['actual_float32_property_values']['muChange']
                       for t in range(len(fields))])
    return dict(name='ring', sc=sc, qs=qs, ext=ext, p_ref=p_ref, p_x=base, span=span, nominal=196,
                label='Radial distance from ring centre', truth=dict(label='analytic ring radius', values=radius),
                meta=dict(centre=centre.tolist(), canvas=rmax))


def gaussian_fields(T=64, n=64, span=120.):
    g = np.linspace(0, span, n); X, Y = np.meshgrid(g, g)
    l1, l2 = np.array([25., 25.]), np.array([85., 85.])
    # l3 starts near l2 (39 units) and ends equidistant from l1 and l2 (51 units each),
    # never crossing l2 or the l1-l2 ridge; d(l3,l1) drops below d(l2,l1)=85 mid-sequence.
    start, end = np.array([115., 60.]), np.array([75., 35.])
    s = 7.
    def blob(c, amp): return amp * np.exp(-((X - c[0]) ** 2 + (Y - c[1]) ** 2) / (2 * s * s))
    # plateau (ridge) joining l1-l2 so they merge high in the split tree; l3 stays isolated
    d = l2 - l1; tt = np.clip(((X - l1[0]) * d[0] + (Y - l1[1]) * d[1]) / (d @ d), 0, 1)
    ridge = .5 * np.exp(-((X - (l1[0] + tt * d[0])) ** 2 + (Y - (l1[1] + tt * d[1])) ** 2) / (2 * 9. ** 2))
    fields, l3 = [], []
    for t in range(T):
        c3 = start + (end - start) * min(1., t / (T * .8)); l3.append(c3)
        fields.append(blob(l1, 1.) + blob(l2, .95) + ridge + blob(c3, 1.05))
    coords = np.c_[X.ravel(), Y.ravel()]
    return np.asarray(fields, np.float64), coords, dict(l1=l1, l2=l2, l3=np.array(l3), span=span)


def gaussian_scene():
    fields, coords, meta = gaussian_fields()
    span = meta['span']
    sc = ep.scene_from_fields(fields, coords, (span / 63) ** 2, 'split')
    ext = reference_points_from_frames(sc['frames'], sc['ids'], kind='extremum')
    # focus = the track whose extremum is nearest l1 in the first frame (fixed identity)
    focus_track = sc['tracks'][0][int(np.argmin(np.linalg.norm(ext[0] - meta['l1'], axis=1)))]
    qs = []
    for e, tr in zip(ext, sc['tracks']):
        f = e[tr.index(focus_track)]
        qs.append(np.linalg.norm(e - f, axis=1))
    diag = float(np.ceil(span * np.sqrt(2)))
    base = replace(ep.P, canvas=span, width_scale=.25 * span / (span * span), rho=.5, gap=.5, extra_budget=1.)
    p_ref = replace(base, canvas=diag)
    d12 = float(np.linalg.norm(meta['l2'] - meta['l1']))
    return dict(name='gaussians', sc=sc, qs=qs, ext=ext, p_ref=p_ref, p_x=base, span=span, nominal=2048,
                label=f'Distance to focus feature (track {focus_track})',
                truth=dict(label='true d(l3,l1)', values=np.linalg.norm(meta['l3'] - meta['l1'], axis=1), d12=d12),
                meta=dict(focus_track=int(focus_track), canvas=diag, d12=d12))
