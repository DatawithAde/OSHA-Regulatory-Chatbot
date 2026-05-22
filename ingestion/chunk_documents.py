from langchain_core.documents import Document
from typing import List
from .parse_cfr import CFRSection

class RegulatoryChunker:
    def __init__(self, chunk_size=800, chunk_overlap=100, min_chunk_size=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def make_header(self, section, chunk_idx, total_chunks):
        header = f"[29 CFR § {section.section_number} - {section.section_title}]"
        if section.subpart_title:
            header += f"\n[Subpart {section.subpart}: {section.subpart_title}]"
        if total_chunks > 1:
            header += f"\n[Part {chunk_idx+1} of {total_chunks}]"
        return header

    def chunk_section(self, section):
        if not section.text or len(section.text) < self.min_chunk_size:
            return []

        if len(section.text) <= self.chunk_size:
            header = self.make_header(section, 0, 1)
            return [Document(
                page_content=f"{header}\n\n{section.text}",
                metadata={**section.full_metadata, "chunk_index": 0, "total_chunks": 1}
            )]

        paragraphs = [p.strip() for p in section.text.split('\n\n') if p.strip()]
        chunks = self.group_paragraphs(paragraphs)
        documents = []

        for i, chunk_text in enumerate(chunks):
            header = self.make_header(section, i, len(chunks))
            documents.append(Document(
                page_content=f"{header}\n\n{chunk_text}",
                metadata={**section.full_metadata, "chunk_index": i, "total_chunks": len(chunks)}
            ))

        return documents

    def group_paragraphs(self, paragraphs):
        chunks = []
        current_group = []
        current_len = 0

        for para in paragraphs:
            if current_len + len(para) > self.chunk_size and current_group:
                chunks.append('\n\n'.join(current_group))
                current_group = [current_group[-1], para]
                current_len = sum(len(p) for p in current_group)
            else:
                current_group.append(para)
                current_len += len(para)

        if current_group:
            chunks.append('\n\n'.join(current_group))

        return chunks

    def chunk_all_sections(self, sections):
        all_docs = []
        for section in sections:
            all_docs.extend(self.chunk_section(section))
        print(f"Created {len(all_docs)} chunks from {len(sections)} sections")
        return all_docs

def build_documents(sections):
    chunker = RegulatoryChunker(chunk_size=800, chunk_overlap=100)
    return chunker.chunk_all_sections(sections)