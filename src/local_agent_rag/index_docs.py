from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embedding_demo import get_embedding

# We need to set up data for text splitter to work on:
# docs directory, chunks size and overlap
DOCS_DIR = Path("docs")

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

def load_documents() -> list[tuple[str, str]]:
    documents = []

    for path in DOCS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        documents.append((path.name, text))

    return documents