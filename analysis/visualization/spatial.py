"""Processed fields, compressed merge trees, and native support fragmentation."""
import numpy as np
from matplotlib.colors import ListedColormap
from rgmtm.baselines import space_filling as sfc
import figstyle as fs
from .catalog import evenly_spaced_frames


def support_labels(frame, leaves, shape):
    labels = np.full(np.prod(shape), -1, dtype=int)
    for rank, leaf in enumerate(leaves):
        vertices = frame.leaf_feature_vertices(leaf)
        labels[vertices] = rank
    return labels.reshape(shape)


def support_palette(count):
    import matplotlib.pyplot as plt
    colors = [('#eeeeee')] + [plt.get_cmap('tab10')(i % 10) for i in range(count)]
    return ListedColormap(colors)


def draw_tree(ax, frame, leaves):
    """Draw only extrema and branching nodes; keep original scalar heights."""
    ranks = {leaf: i for i, leaf in enumerate(leaves)}

    def visit(node):
        children = frame.children[node]
        if not children:
            return ranks[node], float(frame.values[node])
        points = [visit(child) for child in children]
        if len(points) == 1:
            return points[0]
        y = float(frame.values[node]); x = float(np.mean([p[0] for p in points]))
        for cx, cy in points:
            ax.plot([cx, cx, x], [cy, y, y], color='#555555', lw=.8)
        ax.scatter([x], [y], marker='D', s=12, color='#555555', zorder=3)
        return x, y

    visit(frame.root)
    palette = support_palette(len(leaves))
    for rank, leaf in enumerate(leaves):
        ax.scatter([rank], [frame.values[leaf]], color=palette(rank + 1), s=20, zorder=4)
    ax.set_xticks(range(len(leaves)), [f'F{i+1}' for i in range(len(leaves))])
    ax.set_xlabel('feature (frame-local ID)')
    ax.grid(axis='y', alpha=.2)


def spatial_topology(dataset, label, unit, export):
    import matplotlib.pyplot as plt
    sc = dataset['sc']; fields = sc['fields']; times = evenly_spaced_frames(len(fields))
    fig, axs = plt.subplots(len(times), 3, figsize=(7, 2.1 * len(times)),
                            layout='constrained', squeeze=False)
    low, high = float(fields.min()), float(fields.max())
    for row, t in enumerate(times):
        frame = sc['frames'][t]; leaves = sc['ids'][t]; shape = fields[t].shape
        a = axs[row, 0]
        im = a.imshow(fields[t], origin='lower', cmap=fs.FIELD_CMAP, vmin=low, vmax=high)
        for i, leaf in enumerate(leaves):
            y, x = np.unravel_index(leaf, shape)
            a.scatter([x], [y], s=20, c=[support_palette(len(leaves))(i+1)], edgecolors='white', linewidths=.5)
            a.annotate(f'F{i+1}', (x, y), xytext=(4, 4), textcoords='offset points', fontsize=6)
        date = sc.get('dates', [str(i) for i in range(len(fields))])[t]
        a.set_title(f'{date} · processed field'); a.set_xlabel('grid column'); a.set_ylabel('grid row')
        support = support_labels(frame, leaves, shape)
        axs[row, 1].imshow(support + 1, origin='lower', cmap=support_palette(len(leaves)),
                           vmin=0, vmax=len(leaves))
        axs[row, 1].set(title='leaf supports (grey = shared domain)', xlabel='grid column', ylabel='grid row')
        draw_tree(axs[row, 2], frame, leaves)
        axs[row, 2].set(title=f'{sc["trees"][t].kind} tree · {len(leaves)} extrema', ylabel=unit)
    fig.colorbar(im, ax=list(axs[:, 0]), shrink=.65, label=unit)
    fig.suptitle(f'{label}: scalar fields, feature supports and topology', fontsize=10)
    export.save(fig, f'{dataset["name"]}_spatial_topology',
        'Fixed first/middle/last frames. Colors identify frame-local features, not temporal tracks. '
        'Trees suppress degree-one nodes and retain scalar heights; grey cells lie outside leaf supports.')


def curve_fragmentation(dataset, label, unit, export):
    import matplotlib.pyplot as plt
    sc = dataset['sc']; t = int(np.argmax([len(ids) for ids in sc['ids']]))
    frame = sc['frames'][t]; leaves = sc['ids'][t]; field = sc['fields'][t]
    labels = support_labels(frame, leaves, field.shape); palette = support_palette(len(leaves))
    fig, axs = plt.subplots(2, 3, figsize=(7, 4.2), layout='constrained')
    for row, curve in enumerate(('Hilbert', 'Morton')):
        order = sfc.sample_order(field.shape, curve); inverse = sfc.inverse_order(field.shape, curve)
        y, x = np.unravel_index(order, field.shape); line = field.ravel()[order]
        a = axs[row, 0]
        a.imshow(labels + 1, origin='lower', cmap=palette, vmin=0, vmax=len(leaves))
        a.plot(x, y, color='#444444', lw=.22, alpha=.55)
        a.scatter(x[0], y[0], marker='>', color='black', s=22, zorder=3)
        a.set(title=f'{curve}: full grid traversal', xlabel='grid column', ylabel='grid row')
        a = axs[row, 1]; rank = np.arange(len(line))
        a.plot(rank, line, color='#777777', lw=.65)
        for i, leaf in enumerate(leaves):
            r = inverse[leaf]
            a.scatter([r], [line[r]], color=palette(i+1), s=16, zorder=3, label=f'F{i+1}')
        a.set(title='unchanged native scalar sequence', xlabel='sample rank', ylabel=unit)
        permuted = labels.ravel()[order]
        axs[row, 2].imshow((permuted + 1)[None, :], origin='lower', aspect='auto',
                           cmap=palette, vmin=0, vmax=len(leaves), extent=(0, len(order), 0, 1))
        runs = []
        for i in range(len(leaves)):
            occupied = np.flatnonzero(permuted == i)
            runs.append(int(1 + np.count_nonzero(np.diff(occupied) > 1)) if len(occupied) else 0)
        axs[row, 2].set(title='support fragmentation', xlabel='sample rank', yticks=[])
        run_labels = [f'F{i+1}={r}' for i, r in enumerate(runs)]
        chunks = [', '.join(run_labels[i:i+4]) for i in range(0, len(run_labels), 4)]
        axs[row, 2].text(.02, -.32, 'Runs: ' + '\n      '.join(chunks),
                         transform=axs[row, 2].transAxes, fontsize=6, va='top')
    date = sc.get('dates', [str(i) for i in range(len(sc['fields']))])[t]
    handles, names = axs[0, 1].get_legend_handles_labels()
    fig.legend(handles, names, loc='outside lower center', ncol=len(leaves), frameon=False)
    fig.suptitle(f'{label}: native ordering and fragmentation · {date}', fontsize=10)
    export.save(fig, f'{dataset["name"]}_curve_fragmentation',
        f'Frame {t}: first maximum-extremum-count frame, chosen for structural illustration. '
        'Both curves visit every processed grid cell; direction and orientation are fixed. '
        'No value interpolation or barrier correction is applied. Fragment counts are for this frame only.')
