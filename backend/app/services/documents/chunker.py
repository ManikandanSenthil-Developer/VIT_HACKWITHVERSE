import re
from typing import Any, Dict, List


class DocumentChunker:
    """
    Semantic boundary sliding-window chunker designed for institutional financial documents.
    Preserves section titles, page markers, and financial metrics across boundaries.
    """

    def __init__(self, target_chunk_size: int = 600, overlap: int = 100):
        self.target_size = target_chunk_size
        self.overlap = overlap

    def chunk_document(
        self,
        text: str,
        document_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        # Detect sections like "Item 1. Business", "Item 1A. Risk Factors", "Note 1", "Section"
        section_pattern = re.compile(
            r"(Item\s+[0-9A-Za-z]+[\.:\s][^\n]+|Note\s+[0-9]+[\.:\s][^\n]+|Part\s+[0-9IVX]+[\.:\s][^\n]+)",
            re.IGNORECASE,
        )
        page_pattern = re.compile(r"---\s*\[Page\s*([0-9]+)\]\s*---", re.IGNORECASE)

        # Split into natural paragraphs first
        paragraphs = text.split("\n\n")
        chunks: List[Dict[str, Any]] = []

        current_chunk_text = ""
        current_section = "General Overview"
        current_page = 1
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if this paragraph contains a page indicator
            page_match = page_pattern.search(para)
            if page_match:
                try:
                    current_page = int(page_match.group(1))
                except Exception:
                    pass

            # Check if this paragraph defines a new section
            sec_match = section_pattern.search(para)
            if sec_match:
                current_section = sec_match.group(1).strip()

            # If adding this paragraph exceeds target size and current_chunk is not empty
            if len(current_chunk_text) + len(para) > self.target_size and len(current_chunk_text) > 200:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "text": current_chunk_text.strip(),
                    "section": current_section,
                    "page_number": current_page,
                    "metadata": {
                        **document_metadata,
                        "section": current_section,
                        "page": current_page,
                        "chunk_index": chunk_idx,
                    },
                })
                chunk_idx += 1

                # Carry over overlap from the end of the previous chunk
                overlap_text = current_chunk_text[-self.overlap :] if len(current_chunk_text) >= self.overlap else ""
                current_chunk_text = overlap_text + "\n" + para
            else:
                if current_chunk_text:
                    current_chunk_text += "\n\n" + para
                else:
                    current_chunk_text = para

        # Append remaining text if any
        if current_chunk_text.strip():
            chunks.append({
                "chunk_index": chunk_idx,
                "text": current_chunk_text.strip(),
                "section": current_section,
                "page_number": current_page,
                "metadata": {
                    **document_metadata,
                    "section": current_section,
                    "page": current_page,
                    "chunk_index": chunk_idx,
                },
            })

        return chunks
