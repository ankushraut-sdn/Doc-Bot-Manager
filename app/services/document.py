import io
import re
from typing import List
from app.config import Config

try:
    import pypdf
except ImportError:
    pypdf = None

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a supported extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """Split clean text into smaller overlapping chunks for embedding."""
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return [c.strip() for c in chunks if c.strip()]

def extract_text_from_pdf(fp: io.BytesIO) -> str:
    """Extract raw text content from a PDF file stream using pypdf."""
    if pypdf is None:
        raise RuntimeError("pypdf not installed. Install 'pypdf' to parse PDFs.")
    reader = pypdf.PdfReader(fp)
    pages = []
    for pg in reader.pages:
        try:
            pages.append(pg.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n\n".join(pages)

def clean_text(raw: str) -> str:
    """Clean and normalize raw extracted text to improve retrieval accuracy."""
    # Fix hyphenation splits at line ends: "intelli-\ngent" -> "intelligent"
    raw = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", raw)

    # Collapse single newlines inside paragraphs to spaces,
    # but keep double newlines as paragraph breaks.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")

    # Temporary marker for paragraph breaks (2+ newlines)
    raw = re.sub(r"\n{2,}", "<<<PARA>>>", raw)

    # Replace remaining (intra-line) newlines with spaces
    raw = raw.replace("\n", " ")

    # Restore paragraph breaks
    raw = raw.replace("<<<PARA>>>", "\n\n")

    # Collapse multiple spaces
    raw = re.sub(r"[ \t]{2,}", " ", raw)

    # Trim stray bullets/spacing artifacts
    raw = re.sub(r"\s*•\s*", " • ", raw)
    raw = re.sub(r"\s*○\s*", " • ", raw)

    return raw.strip()
