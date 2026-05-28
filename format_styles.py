#!/usr/bin/env python3
"""Format and extract all styles from DOCX styles.xml."""

from lxml import etree
import re

NSMAP = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

def qn(tag):
    """Convert namespace:tag to {ns}tag."""
    ns, local = tag.split(':')
    return f'{{{NSMAP[ns]}}}{local}'

STYLES_FILE = "/home/gna/workspase/projects/gosxcli/template/styles.xml"
OUTPUT_FILE = "/home/gna/workspase/projects/gosxcli/template/formatted_styles.txt"

with open(STYLES_FILE, 'rb') as f:
    tree = etree.parse(f)
root = tree.getroot()

lines = []

def log(text=""):
    lines.append(text)
    print(text)

# Document defaults
log("=" * 80)
log("DOCUMENT DEFAULTS (w:docDefaults)")
log("=" * 80)
doc_defaults = root.find(qn('w:docDefaults'))
if doc_defaults is not None:
    log(etree.tostring(doc_defaults, pretty_print=True).decode())

# Latent styles
log("\n" + "=" * 80)
log("LATENT STYLES (summary)")
log("=" * 80)
latent = root.find(qn('w:latentStyles'))
if latent is not None:
    log(f"  count: {latent.get(qn('w:count'))}")
    log(f"  defLockedState: {latent.get(qn('w:defLockedState'))}")
    exceptions = latent.findall(qn('w:lsdException'))
    log(f"  exceptions count: {len(exceptions)}")
    for exc in exceptions[:20]:
        log(f"    - {exc.get(qn('w:name'))}: semiHidden={exc.get(qn('w:semiHidden'))}, uiPriority={exc.get(qn('w:uiPriority'))}")
    if len(exceptions) > 20:
        log(f"    ... and {len(exceptions)-20} more")

# ALL styles
log("\n" + "=" * 80)
log("ALL STYLES (COMPLETE)")
log("=" * 80)

styles = root.findall(qn('w:style'))
log(f"\nTotal styles: {len(styles)}\n")

for style in styles:
    style_id = style.get(qn('w:styleId'))
    style_type = style.get(qn('w:type'))
    name_elem = style.find(qn('w:name'))
    style_name = name_elem.get(qn('w:val')) if name_elem is not None else '???'
    based_on = style.find(qn('w:basedOn'))
    based_on_val = based_on.get(qn('w:val')) if based_on is not None else None
    
    log(f"\n{'━' * 70}")
    log(f"STYLE: '{style_name}' (id={style_id}, type={style_type})")
    if based_on_val:
        log(f"  basedOn: {based_on_val}")
    log(f"{'━' * 70}")
    
    # Print the FULL XML of this style, nicely formatted
    style_xml = etree.tostring(style, pretty_print=True).decode()
    log(style_xml)

# Save to file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"\nSaved to {OUTPUT_FILE} ({len(lines)} lines)")