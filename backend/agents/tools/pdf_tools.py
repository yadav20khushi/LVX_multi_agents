from typing import List, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import re

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

class ParsedDoc(BaseModel):
    file: str
    pages: int
    text: str

class ParsePdfResult(BaseModel):
    pages_total: int
    docs: List[ParsedDoc]
    merged_text: str
    founder_hint: Dict[str, str]

def _extract_text_from_pdf(path: str) -> ParsedDoc:
    if PdfReader is None:
        raise RuntimeError("pypdf not installed. pip install pypdf")
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    text = "\n".join(texts)
    return ParsedDoc(file=Path(path).name, pages=len(reader.pages), text=text)

def _guess_founder_info(text: str) -> Dict[str, str]:
    # lightweight heuristics; A1 will refine with LLM
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    # Look for simple patterns like "Founder: Name" or "CEO: Name"
    name_match = re.search(r"(Founder|Co-?founder|CEO)\s*[:\-]\s*([A-Z][A-Za-z.\s'-]{2,60})", text, re.IGNORECASE)
    company_match = re.search(r"(Company|Startup)\s*[:\-]\s*([A-Z0-9][A-Za-z0-9 .'\-&]{2,80})", text, re.IGNORECASE)
    return {
        "name": (name_match.group(2).strip() if name_match else ""),
        "email": (email_match.group(0) if email_match else ""),
        "company": (company_match.group(2).strip() if company_match else "")
    }

# ADK tool signature
def parse_pdf_tool(files: List[str]) -> Dict[str, Any]:
    """
    Args:
      files: list of absolute or relative PDF paths.
    Returns:
      dict compatible with ParsePdfResult model.
    """
    docs = []
    for f in files:
        if not Path(f).exists():
            raise FileNotFoundError(f"PDF not found: {f}")
        docs.append(_extract_text_from_pdf(f))
    merged_text = "\n\n---\n\n".join(d.text for d in docs)
    pages_total = sum(d.pages for d in docs)
    founder_hint = _guess_founder_info(merged_text)
    return ParsePdfResult(
        pages_total=pages_total,
        docs=docs,
        merged_text=merged_text,
        founder_hint=founder_hint
    ).model_dump()
