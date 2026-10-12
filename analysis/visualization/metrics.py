"""Charts drawn strictly from saved evaluation records; no experiment reruns."""
import numpy as np
import matplotlib.pyplot as plt
from .catalog import METHODS, motion_row, motion_rate


def motion_errors(records, datasets, labels, export):
    fig, axs = plt.subplots(2, 3, figsize=(7, 4.5), layout='constrained')
    for ax, name in zip(axs.flat, datasets):
        record = records[name]; cases = motion_row(record, 'R 20%').get('clear', 0)
        for i, method in enumerate(METHODS):
            row = motion_row(record, method.key)
            if row.get('clear'):
                ax.bar(i, row['reversal'] * 100, color=method.color, width=.7)
                ax.bar(i, row['miss'] * 100, bottom=row['reversal'] * 100,
                       color=method.color, alpha=.35, hatch='///', width=.7)
                ax.text(i, row['error'] * 100 + 2, f'{row["error"]*100:.1f}', ha='center', fontsize=5.5)
        ax.set(title=f'{labels[name]} · n={cases}', ylim=(0, 108), ylabel='total motion error (%)')
        ax.set_xticks(range(len(METHODS)), [m.label for m in METHODS], rotation=35, ha='right')
        ax.grid(axis='y', alpha=.2)
        if not cases:
            ax.text(.5, .5, 'No clear events\nrate undefined', transform=ax.transAxes, ha='center', va='center')
    fig.suptitle('Motion readings · k=2, ε=2% · solid: reversal; hatched: miss', fontsize=9)
    export.save(fig, 'motion_error_comparison',
        'Total error = reversal + miss, using the declared two-step, 2% setting. '
        'Counts are clear 2-D events, not independent samples. No significance claim is encoded by bar height; '
        'PM2.5 January was selected after seasonal exploration. Gaussian has no clear events.')


def topology_motion(records, datasets, labels, export):
    methods = [m for m in METHODS if m.key in ('R 20%', 'Hilbert', 'Morton')]
    fig, axs = plt.subplots(2, 2, figsize=(7, 4.3), layout='constrained')
    for ax, name in zip(axs.flat, datasets):
        for method in methods:
            rate = motion_rate(records[name], method.key)
            cost = records[name]['dstar'][method.key]
            if rate is not None:
                ax.scatter(cost['max_share'] * 100, rate * 100, color=method.color, s=36, label=method.label)
                offset = (4, 8) if method.key == 'Hilbert' else (4, -10) if method.key == 'Morton' else (4, 3)
                ax.annotate(method.label, (cost['max_share'] * 100, rate * 100), xytext=offset,
                            textcoords='offset points', fontsize=6)
        ax.set(title=labels[name], xlim=(-3, 110), ylim=(-3, 100),
               xlabel='maximum merge-level error (% of scalar range)', ylabel='total motion error (%)')
        ax.grid(alpha=.2)
    fig.suptitle('Measured position–topology trade-offs · lower on both axes is preferable', fontsize=9)
    export.save(fig, 'topology_motion_tradeoff',
        'R uses optimal barrier filling; Hilbert/Morton use their unchanged native scalar sequences. '
        'Costs are achieved maxima over frames, not κ bounds. Points show one fixed operating setting, '
        'not a Pareto frontier or a statistical superiority claim.')


def neighbourhoods(records, datasets, labels, export):
    fig, axs = plt.subplots(2, 3, figsize=(7, 4.2), layout='constrained')
    for ax, name in zip(axs.flat, datasets):
        for method in METHODS:
            row = records[name]['hidden'][method.key]
            if row['stress'] is None or row['nn_preservation'] is None:
                continue
            ax.scatter(row['stress'], row['nn_preservation'] * 100, color=method.color, s=25,
                       label=method.label)
        ax.set(title=labels[name], xlim=(-.03, 1.2), ylim=(-3, 103),
               xlabel='Kruskal stress-1 (lower is better)', ylabel='NN preservation (%)')
        ax.grid(alpha=.2)
    handles, names = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, names, loc='outside lower center', ncol=6, frameon=False)
    fig.suptitle('2-D neighbourhood preservation · each method keeps its own anchor geometry', fontsize=9)
    export.save(fig, 'neighbourhood_preservation',
        'Frame-mean stress and nearest-neighbour preservation from the saved hidden-cost evaluation. '
        'These metrics measure spatial relationships, not human performance. Frames with fewer than '
        'three extrema are excluded by the shared evaluation protocol.')


def motion_sensitivity(records, datasets, labels, export):
    fig, axs = plt.subplots(2, 3, figsize=(7, 4.5), layout='constrained'); steps = (1, 2, 4, 8)
    for ax, name in zip(axs.flat, datasets):
        for method in METHODS:
            rates = [motion_rate(records[name], method.key, k=k) for k in steps]
            ax.plot(steps, [np.nan if x is None else 100*x for x in rates],
                    color=method.color, marker='o', ms=3, label=method.label)
        cases = [motion_row(records[name], 'R 20%', k=k).get('clear', 0) for k in steps]
        ax.set(title=f'{labels[name]} · n={"/".join(map(str,cases))}', xticks=steps,
               ylim=(-3, 103), xlabel='window length (time steps)', ylabel='total motion error (%)')
        ax.grid(alpha=.2)
    handles, names = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, names, loc='outside lower center', ncol=6, frameon=False)
    fig.suptitle('Window sensitivity · ε=2% · counts follow k=1/2/4/8', fontsize=9)
    export.save(fig, 'motion_window_sensitivity',
        'Each k uses its own set of clear events; lines connect operating settings, not physical trajectories. '
        'Step duration differs across datasets. Undefined rates are omitted, including Gaussian k=1/2.')
