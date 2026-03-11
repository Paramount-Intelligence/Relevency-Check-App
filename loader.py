import os
from docx import Document
from config import CONSULTANTS


def _find_kb_dir():
    """Find knowledge_base/ next to this script (Railway) or ../Knowledge Base/ (local dev)."""
    local = os.path.join(os.path.dirname(__file__), "knowledge_base")
    if os.path.isdir(local):
        return local
    parent = os.path.join(os.path.dirname(__file__), "..", "Knowledge Base")
    if os.path.isdir(os.path.normpath(parent)):
        return os.path.normpath(parent)
    return None


def load_par_libraries():
    """Load all 4 consultant .docx files at startup. Returns dict {name: text}."""
    kb_dir = _find_kb_dir()
    if not kb_dir:
        raise RuntimeError(
            "Knowledge base not found. Place the 4 .docx files in a 'knowledge_base/' "
            "folder next to evaluator.py."
        )
    libraries = {}
    for name in CONSULTANTS:
        path = os.path.join(kb_dir, f"{name}.docx")
        if not os.path.exists(path):
            raise RuntimeError(f"Missing PAR library: {path}")
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        if len(text) < 100:
            print(f"  ⚠️  {name}.docx is very short ({len(text)} chars) — may be image-based")
        libraries[name] = text
        print(f"  ✅ Loaded {name}.docx — {len(text.split())} words")
    return libraries
