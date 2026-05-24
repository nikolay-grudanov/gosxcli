#!/usr/bin/env python3
"""Analyze document.xml structure from DOCX template."""

import sys
sys.path.insert(0, '/home/gna/.local/lib/python3.14/site-packages')

from lxml import etree

NSMAP = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
}

def qn(tag):
    ns, local = tag.split(':')
    return f'{{{NSMAP[ns]}}}{local}'


DOC_FILE = "/home/gna/workspase/projects/gosxcli/template/document.xml"

with open(DOC_FILE, 'rb') as f:
    tree = etree.parse(f)
root = tree.getroot()
body = root.find(qn('w:body'))

lines = []


def log(text=""):
    lines.append(text)
    print(text)


# ==========================================
# SECTION PROPERTIES
# ==========================================
log("=" * 80)
log("SECTION PROPERTIES")
log("=" * 80)

sect_prs = body.findall(qn('w:sectPr'))
for i, sp in enumerate(sect_prs):
    log(f"\nSection {i}:")
    log(etree.tostring(sp, pretty_print=True).decode())

# Also check for sectPr inside paragraphs (section breaks)
for pi, p in enumerate(body.findall(qn('w:p'))):
    pPr = p.find(qn('w:pPr'))
    if pPr is not None:
        inner_sect = pPr.find(qn('w:sectPr'))
        if inner_sect is not None:
            log(f"\nSection break in paragraph {pi}:")
            log(etree.tostring(inner_sect, pretty_print=True).decode())

# ==========================================
# ALL PARAGRAPHS WITH STYLE AND TEXT
# ==========================================
log("\n" + "=" * 80)
log("ALL PARAGRAPHS")
log("=" * 80)

for pi, p in enumerate(body.findall(qn('w:p'))):
    pPr = p.find(qn('w:pPr'))

    # Get style
    style = ""
    if pPr is not None:
        pStyle = pPr.find(qn('w:pStyle'))
        if pStyle is not None:
            style = pStyle.get(qn('w:val'))

    # Get text
    texts = []
    for r in p.findall(qn('w:r')):
        t = r.find(qn('w:t'))
        if t is not None and t.text:
            texts.append(t.text)
        # Check for field codes
        instr = r.find(qn('w:instrText'))
        if instr is not None and instr.text:
            texts.append(f'[FIELD:{instr.text.strip()}]')
        # Check for images
        drawing = r.find(qn('w:drawing'))
        if drawing is not None:
            texts.append('[IMAGE]')

    text = ''.join(texts)
    if text or style:
        log(f"\nP{pi:03d}: style='{style}' text='{text[:120]}'")

    # For non-Normal paragraphs, show the pPr XML
    if style and style not in ('780',):
        if pPr is not None:
            log(f"  pPr: {etree.tostring(pPr, pretty_print=False).decode()[:500]}")

# ==========================================
# TABLES
# ==========================================
log("\n" + "=" * 80)
log("ALL TABLES")
log("=" * 80)

for ti, tbl in enumerate(body.findall(qn('w:tbl'))):
    log(f"\n{'━' * 60}")
    log(f"TABLE {ti}")

    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is not None:
        log(f"  tblPr: {etree.tostring(tblPr, pretty_print=True).decode()}")

    tblGrid = tbl.find(qn('w:tblGrid'))
    if tblGrid is not None:
        log(f"  tblGrid: {etree.tostring(tblGrid, pretty_print=False).decode()}")

    rows = tbl.findall(qn('w:tr'))
    log(f"  Rows: {len(rows)}")

    for ri, row in enumerate(rows):
        trPr = row.find(qn('w:trPr'))
        if trPr is not None:
            log(f"  Row {ri} trPr: {etree.tostring(trPr, pretty_print=False).decode()}")

        cells = row.findall(qn('w:tc'))
        for ci, cell in enumerate(cells):
            tcPr = cell.find(qn('w:tcPr'))
            cell_texts = []
            for p in cell.findall(qn('w:p')):
                for r in p.findall(qn('w:r')):
                    t = r.find(qn('w:t'))
                    if t is not None and t.text:
                        cell_texts.append(t.text)
                    instr = r.find(qn('w:instrText'))
                    if instr is not None and instr.text:
                        cell_texts.append(f'[FIELD:{instr.text.strip()}]')

            text = ''.join(cell_texts)
            if text.strip() or tcPr is not None:
                log(f"    Cell[{ri},{ci}]: '{text[:100]}'")
                if tcPr is not None:
                    log(f"      tcPr: {etree.tostring(tcPr, pretty_print=False).decode()[:500]}")

# ==========================================
# IMAGES / DRAWINGS
# ==========================================
log("\n" + "=" * 80)
log("IMAGES")
log("=" * 80)

for pi, p in enumerate(body.findall(qn('w:p'))):
    for r in p.findall(qn('w:r')):
        drawings = r.findall(qn('w:drawing'))
        for d in drawings:
            log(f"\nImage in paragraph {pi}:")
            log(etree.tostring(d, pretty_print=True).decode()[:2000])

# ==========================================
# FIELD CODES
# ==========================================
log("\n" + "=" * 80)
log("FIELD CODES")
log("=" * 80)

for pi, p in enumerate(body.findall(qn('w:p'))):
    for r in p.findall(qn('w:r')):
        instr = r.find(qn('w:instrText'))
        if instr is not None and instr.text:
            log(f"  P{pi}: instrText='{instr.text.strip()}'")

# ==========================================
# BOOKMARKS
# ==========================================
log("\n" + "=" * 80)
log("BOOKMARKS")
log("=" * 80)

for bm in body.findall('.//' + qn('w:bookmarkStart')):
    name = bm.get(qn('w:name'))
    bm_id = bm.get(qn('w:id'))
    log(f"  id={bm_id} name='{name}'")

# Save output
OUTPUT = "/home/gna/workspase/projects/gosxcli/template/document_analysis.txt"
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"\nSaved to {OUTPUT}")