"""Chunking utilities for splitting raw markdown documents into sections."""

import json
import re

def sliding_window(seq, size, step):
    """Return overlapping windows from a sequence.

    Args:
        seq: Input sequence (string, list, etc.).
        size: Window size.
        step: Step between consecutive windows.

    Returns:
        A list of dictionaries with keys: `start` and `chunk`.
    """
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    n = len(seq)
    result = []
    for i in range(0, n, step):
        chunk = seq[i:i+size]
        result.append({'start': i, 'chunk': chunk})
        if i + size >= n:
            break

    return result



def split_markdown_by_level(text, level=2):
    """Split markdown content into sections using a target heading level.

    Args:
        text: Markdown content.
        level: Heading level used as section delimiters.

    Returns:
        A list of markdown sections including heading and body.
    """
    # This regex matches markdown headers
    # For level 2, it matches lines starting with "## "
    header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
    pattern = re.compile(header_pattern, re.MULTILINE)

    # Split and keep the headers
    parts = pattern.split(text)
    
    sections = []
    for i in range(1, len(parts), 3):
        # We step by 3 because regex.split() with
        # capturing groups returns:
        # [before_match, group1, group2, after_match, ...]
        # here group1 is "## ", group2 is the header text
        header = parts[i] + parts[i+1]  # "## " + "Title"
        header = header.strip()

        # Get the content after this header
        content = ""
        if i+2 < len(parts):
            content = parts[i+2].strip()

        if content:
            section = f'{header}\n\n{content}'
        else:
            section = header
        sections.append(section)
    
    return sections


def chunk_documents(docs, level=2):
    """Transform raw repository documents into section-level chunks.

    Args:
        docs: List of document dictionaries containing at least `content`.
        level: Markdown heading level used for splitting.

    Returns:
        A list of chunked document dictionaries.
    """
    docs_chunks = []

    for doc in docs:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop("content", "")
        sections = split_markdown_by_level(doc_content, level=level)
        for section in sections:
            section_doc = doc_copy.copy()
            section_doc["section"] = section
            docs_chunks.append(section_doc)

    return docs_chunks


def main():
    """Read raw docs, split them into sections, and save chunked output."""
    with open("data/raw_docs.json", "rt", encoding="utf-8") as f_in:
        docs = json.load(f_in)

    docs_chunks = chunk_documents(docs, level=2)

    with open("data/chunked_docs.json", "w", encoding="utf-8") as f_out:
        json.dump(docs_chunks, f_out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()