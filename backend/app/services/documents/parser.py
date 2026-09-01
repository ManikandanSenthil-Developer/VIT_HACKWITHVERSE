import io
import re
from typing import Tuple
from bs4 import BeautifulSoup
import pypdf


class DocumentParser:
    """Extracts, cleans, and sanitizes textual content from diverse financial filing formats."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Strip non-printable characters, excessive whitespace, and normalize quotes."""
        if not raw_text:
            return ""
        # Normalize newlines
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace non-breaking spaces and special unicode quotes
        text = text.replace("\xa0", " ").replace("“", '"').replace("”", '"').replace("’", "'")
        # Collapse multiple whitespace lines into double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple spaces
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    @classmethod
    def parse_html(cls, html_content: str) -> str:
        """Extract clean text from SEC EDGAR HTML or filing web disclosures."""
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()
        text = soup.get_text(separator="\n")
        return cls.clean_text(text)

    @classmethod
    def parse_pdf(cls, pdf_bytes: bytes) -> Tuple[str, int]:
        """Extract text and page count from financial PDF filing."""
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages):
            page_content = page.extract_text() or ""
            if page_content.strip():
                pages_text.append(f"--- [Page {i + 1}] ---\n{page_content}")
        
        full_text = "\n\n".join(pages_text)
        return cls.clean_text(full_text), len(reader.pages)

    @classmethod
    def auto_parse(cls, content: str, is_html: bool = False) -> str:
        """Auto-detect and clean raw textual or HTML content."""
        if is_html or "<html" in content.lower() or "<div" in content.lower():
            return cls.parse_html(content)
        return cls.clean_text(content)
