"""Native Hilbert/Morton maps versus optimally filled R; safe to import."""
import task_reference as tr
import figstyle as fs
import replicate as rp
from visualization.rendering import temporal_maps


def main():
    fs.apply()
    fig, axs = tr.plt.subplots(2, 3, figsize=(fs.TEXT_W, 3.5), layout='constrained')
    for row, name in enumerate(('ring', 'pm25')):
        dataset = rp.LOADERS[name](); scene = dataset['sc']; matrices = temporal_maps(dataset)
        low, high = float(scene['fields'].min()), float(scene['fields'].max())
        for column, method in enumerate(('Hilbert', 'Morton', 'R 20%')):
            image = axs[row, column].imshow(matrices[method], origin='lower', aspect='auto',
                       cmap=fs.FIELD_CMAP, vmin=low, vmax=high)
            label = 'R (κ=20%)' if method == 'R 20%' else method
            axs[row, column].set(title=f'{name}: {label}', xlabel='time step',
                       ylabel='linearized space (normalized)' if column < 2 else '')
            axs[row, column].set_yticks([])
        fig.colorbar(image, ax=list(axs[row, :]), shrink=.65,
                     label='µg m⁻³' if name == 'pm25' else 'scalar value')
    for extension in ('pdf', 'png'):
        fig.savefig(tr.OUT / f'fig_sfc_comparison.{extension}', dpi=300)
    tr.plt.close(fig)


if __name__ == '__main__':
    main()
