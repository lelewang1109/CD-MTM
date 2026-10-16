"""Build visual inventories of independently generated subplot PNG files."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'results/legacy_publication/pacificvis2027/figures/panels'


def row(sheet, names, group, top, height):
    width = sheet.width // len(names)
    draw = ImageDraw.Draw(sheet)
    for index, name in enumerate(names):
        source = FOLDER / group / (name + '.png')
        im = Image.open(source).convert('RGB')
        im.thumbnail((width - 20, height - 40))
        x = index * width + (width - im.width) // 2
        sheet.paste(im, (x, top + 28))
        draw.text((index * width + 10, top + 7), name, fill='black')


sheet = Image.new('RGB', (1800, 1180), '#eeeeee')
row(sheet, ['top_stmtm', 'top_tree_kept', 'top_relaxed_position',
            'top_relaxed_topology'], 'fig1', 0, 260)
row(sheet, ['middle_stmtm', 'middle_tree_kept', 'middle_relaxed'],
    'fig1', 270, 500)
row(sheet, ['bottom_snapshot_' + str(i) for i in range(1, 6)],
    'fig1', 780, 400)
sheet.save(FOLDER / 'overview_fig1.png')

for group in sorted(FOLDER.iterdir()):
    if not group.is_dir() or group.name == 'fig1':
        continue
    names = sorted(p.stem for p in group.glob('*.png'))
    count = (len(names) + 2) // 3
    sheet = Image.new('RGB', (1800, count * 520), '#eeeeee')
    for r in range(count):
        row(sheet, names[r * 3:(r + 1) * 3], group.name, r * 520, 520)
    sheet.save(FOLDER / ('overview_' + group.name + '.png'))
print('Wrote subplot inventories:', FOLDER)
