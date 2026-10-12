"""Input fields and R maps for new real sequences; safe to import."""
import public_scalar as ps
import task_reference as tr
import figstyle as fs
from visualization.rendering import temporal_maps


def main():
    fs.apply()
    fig, axs = tr.plt.subplots(2, 3, figsize=(fs.TEXT_W, 3.25), layout='constrained')
    for row, name in enumerate(('olr', 'pm25')):
        dataset = ps.load(name); scene = dataset['sc']
        low, high = float(scene['fields'].min()), float(scene['fields'].max())
        for column, time in enumerate((0, min(30, len(scene['fields']) - 1))):
            ax = axs[row, column]
            ax.imshow(scene['fields'][time], origin='lower', cmap=fs.FIELD_CMAP, vmin=low, vmax=high)
            ax.set_title(f'{name.upper()}: {scene["dates"][time]}'); ax.set_xticks([]); ax.set_yticks([])
        optimal = temporal_maps(dataset)['R 20%']
        ax = axs[row, 2]
        image = ax.imshow(optimal, origin='lower', aspect='auto', cmap=fs.FIELD_CMAP, vmin=low, vmax=high)
        ax.set(title=r'R, $\kappa=20\%$', xlabel='time step', ylabel='reference position'); ax.set_yticks([])
        fig.colorbar(image, ax=list(axs[row, :]), shrink=.65,
                     label={'olr': 'W m⁻²', 'pm25': 'µg m⁻³'}[name])
    for extension in ('png', 'pdf'):
        fig.savefig(tr.OUT / f'fig_new_datasets.{extension}', dpi=300)
    tr.plt.close(fig)


if __name__ == '__main__':
    main()
