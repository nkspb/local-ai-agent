from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embedding_demo import get_embedding

# We need to set up data for text splitter to work on:
# docs directory, chunks size and overlap
DOCS_DIR = Path("docs")

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50 # to preserve contexts in adjacent chunks

def load_documents() -> list[tuple[str, str]]:
    # Loads documents from md files to later split them in chunks
    # It returns a list where each item is a tuple with document filename and contents
    documents = []

    for path in DOCS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        documents.append((path.name, text))
    print("============Documents==========")
    print(documents)
    print("===============================")
    return documents

def split_documents(documents: list[tuple[str, str]],) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = []

    for filename, text in documents:
        split_texts = splitter.split_text(text)

        # Enumerate is used to iterate over any itterable and returns index + value
        # Itterable is any object that can return its elements one at a time
        for index, chunk_text in enumerate(split_texts):
            chunks.append(
                {
                    "id": f"{filename}-{index}",
                    "text": chunk_text,
                    "source": filename,
                }
            )

    return chunks

def main() -> None:
    documents = load_documents()
    chunks = split_documents(documents)

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")

    for chunk in chunks:
        print()
        print(chunk)

    # Create Chroma client that stores data to disk
    client = chromadb.PersistentClient(
        path="vector_store"
    )

    # Create a collection where chunks will be stored
    collection = client.get_or_create_collection(
        name="devops_docs"
    )

    # Now we need to prepare data structures that will go
    # to Chroma database
    ids = []
    texts = []
    embeddings = []
    metadatas = []

    # Fill in the collection with chunks:
    for chunk in chunks:
        ids.append(chunk["id"])
        texts.append(chunk["text"])
        embeddings.append(
            get_embedding(chunk["text"])
        )
        metadatas.append(
            {
                "source": chunk["source"],
            }
        )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

if __name__ == "__main__":
    main()

