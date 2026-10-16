"""Update embedded figure Forms in an existing review PDF without reflowing text.

Use only when the manuscript text and each figure's physical dimensions are
unchanged. Every replacement is checked against the existing Form bounding
box, and all page text is compared before the updated file is published.
"""
from pathlib import Path
import shutil
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, NumberObject

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'results/legacy_publication/pacificvis2027'
SOURCE = PAPER / 'review-preview.pdf'
TEMP = ROOT / 'tmp/pdfs/review-with-updated-figures.pdf'
FIGURES = ((0, '/Fm0', 'fig_teaser'), (2, '/Fm1', 'fig_concept'),
           (4, '/Fm2', 'fig_topo_price'), (6, '/Fm3', 'fig_rq1'),
           (7, '/Fm4', 'fig_frontier_exact'), (8, '/Fm5', 'fig_witness'))

reader = PdfReader(SOURCE)
original_text = [p.extract_text() for p in reader.pages]
writer = PdfWriter()
writer.clone_document_from_reader(reader)
for page_index, resource_name, stem in FIGURES:
    resources = writer.pages[page_index]['/Resources']['/XObject']
    existing = resources[resource_name].get_object()
    incoming = PdfReader(PAPER / 'figures' / (stem + '.pdf')).pages[0]
    old_box = [float(v) for v in existing['/BBox']]
    new_box = [float(v) for v in incoming.mediabox]
    assert all(abs(a - b) < 1e-5 for a, b in zip(old_box, new_box)), (stem, old_box, new_box)
    form = DecodedStreamObject()
    form.set_data(incoming.get_contents().get_data())
    form.update({NameObject('/Type'): NameObject('/XObject'),
                 NameObject('/Subtype'): NameObject('/Form'),
                 NameObject('/FormType'): NumberObject(1),
                 NameObject('/BBox'): incoming.mediabox.clone(writer),
                 NameObject('/Resources'): incoming['/Resources'].clone(writer)})
    if '/Group' in incoming:
        form[NameObject('/Group')] = incoming['/Group'].clone(writer)
    resources[NameObject(resource_name)] = writer._add_object(form)
TEMP.parent.mkdir(parents=True, exist_ok=True)
with TEMP.open('wb') as stream:
    writer.write(stream)
checked = PdfReader(TEMP)
assert len(checked.pages) == len(reader.pages) == 11
assert [p.extract_text() for p in checked.pages] == original_text
assert [list(p.mediabox) for p in checked.pages] == [list(p.mediabox) for p in reader.pages]
shutil.copy2(TEMP, SOURCE)
print('Updated six figure Forms; all 11 page texts and page dimensions match:', SOURCE)
