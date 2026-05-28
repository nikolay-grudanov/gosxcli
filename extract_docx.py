#!/usr/bin/env python3
"""Extract XML files from DOCX template to workspace."""

import zipfile
import os

TEMPLATE = "/home/gna/workspase/projects/gosxcli/template/Шаблон_оформления_ВКР_2026_новый.docx"
OUT_DIR = "/home/gna/workspase/projects/gosxcli/template"

os.makedirs(OUT_DIR, exist_ok=True)

with zipfile.ZipFile(TEMPLATE, 'r') as z:
    # List all files
    print("Files in DOCX:")
    for name in sorted(z.namelist()):
        info = z.getinfo(name)
        print(f"  {name} ({info.file_size} bytes)")
    
    # Extract key files
    files_to_extract = {
        'word/styles.xml': 'styles.xml',
        'word/numbering.xml': 'numbering.xml',
        'word/settings.xml': 'settings.xml',
        'word/document.xml': 'document.xml',
        'word/_rels/document.xml.rels': 'document.xml.rels',
        '[Content_Types].xml': 'content_types.xml',
    }
    
    for src, dst in files_to_extract.items():
        if src in z.namelist():
            data = z.read(src)
            out_path = os.path.join(OUT_DIR, dst)
            with open(out_path, 'wb') as f:
                f.write(data)
            print(f"Extracted: {src} -> {out_path} ({len(data)} bytes)")
        else:
            print(f"NOT FOUND: {src}")
    
    # Also extract all header/footer files
    for name in z.namelist():
        if 'header' in name.lower() or 'footer' in name.lower():
            basename = os.path.basename(name)
            data = z.read(name)
            out_path = os.path.join(OUT_DIR, basename)
            with open(out_path, 'wb') as f:
                f.write(data)
            print(f"Extracted: {name} -> {out_path} ({len(data)} bytes)")

print("\nDone! Files extracted to:", OUT_DIR)