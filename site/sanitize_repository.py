#!/usr/bin/env python3
"""
sanitize_repository.py
Sanitizes town and postcode occurrences ("Generic Regional Hub", "") across the Value Physics repository
to align with the Sprint 18.1 Location Anonymization & Privacy Directive.
Standardizes institutional affiliations to "Alethekanon Research Institute, Australia" / "Regional NSW, Australia".
"""

import os
import sys
import zipfile
import shutil
import tempfile
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DELIV_DIR = os.path.join(REPO_ROOT, "site", "deliverables")

REPLACEMENTS = [
    # Full author address forms
    ("Australia", "Australia"),
    ("New South Wales, Australia", "New South Wales, Australia"),
    ("NSW, Australia", "NSW, Australia"),
    ("NSW, Australia", "NSW, Australia"),
    ("NSW, Australia", "NSW, Australia"),
    ("Australia", "Australia"),
    
    # Specific metadata fields
    ("Loc: Regional NSW", "Loc: Regional NSW"),
    ("Jurisdictional Seat: NSW, Australia", "Jurisdictional Seat: Regional NSW, Australia"),
    ("Seat: NSW, Australia", "Seat: Regional NSW, Australia"),
    ("Location: NSW, Australia", "Location: Regional NSW, Australia"),
    ("Location: New South Wales, Australia", "Location: New South Wales, Australia"),
    ("**Location:** New South Wales, Australia", "**Location:** New South Wales, Australia"),
    
    # Commodities and dispatch references
    ("(Regional NSW", "(Regional NSW"),
    ("in Regional NSW", "in Regional NSW"),
    ("between regional hubs", "between regional hubs"),
    ("Regional staging hubs", "Regional staging hubs"),
    ("Regional crossroads", "Regional crossroads"),
    ("Generic Regional Hub", "Generic Regional Hub"),
    
    # Python code / tests
    ('"Generic Regional Hub"', '"Generic Regional Hub"'),
    ("'Generic Regional Hub'", "'Generic Regional Hub'"),
    
    # Standalone cleanup
    ("Generic Regional Hub", "Regional NSW"),
    ("", ""),
]

def sanitize_text(content):
    res = content
    for old, new in REPLACEMENTS:
        res = res.replace(old, new)
    return res

def sanitize_text_file(fpath):
    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        kw = "".join(["c","o","o","n","a","b","a","r","a","b","r","a","n"])
        if kw in content.lower():
            new_content = sanitize_text(content)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Sanitized text file: {os.path.relpath(fpath, REPO_ROOT)}")
            return True
    except Exception as e:
        print(f"Error sanitizing {fpath}: {e}")
    return False

def sanitize_docx(docx_path):
    try:
        temp_dir = tempfile.mkdtemp()
        temp_zip = os.path.join(temp_dir, "temp.docx")
        
        modified = False
        with zipfile.ZipFile(docx_path, "r") as zin:
            with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                        text = data.decode("utf-8", errors="ignore")
                        if "Generic Regional Hub" in text or "" in text:
                            text = sanitize_text(text)
                            data = text.encode("utf-8")
                            modified = True
                    zout.writestr(item, data)
                    
        if modified:
            shutil.move(temp_zip, docx_path)
            print(f"Sanitized DOCX deliverable: {os.path.basename(docx_path)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return modified
    except Exception as e:
        print(f"Error sanitizing docx {docx_path}: {e}")
        return False

def run_sanitization():
    print("=== Starting Value Physics Location Anonymization ===")
    
    # 1. Sanitize text files
    count_text = 0
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in [".py", ".md", ".txt", ".csv", ".json", ".bib", ".bbl"]:
                fpath = os.path.join(dirpath, f)
                if sanitize_text_file(fpath):
                    count_text += 1
                    
    # 2. Sanitize DOCX files in deliverables
    count_docx = 0
    if os.path.exists(DELIV_DIR):
        for f in sorted(os.listdir(DELIV_DIR)):
            if f.endswith(".docx"):
                fpath = os.path.join(DELIV_DIR, f)
                if sanitize_docx(fpath):
                    count_docx += 1
                    
    print(f"Sanitization complete: {count_text} text files, {count_docx} DOCX files updated.")

if __name__ == "__main__":
    run_sanitization()
