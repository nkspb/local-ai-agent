from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embedding_demo import get_embedding

# We need to set up data for text splitter to work on:
# docs directory, chunks size and overlap
DOCS_DIR = Path("docs")

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100 # to preserve contexts in adjacent chunks

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

def split_into_sections(text: str) -> list[tuple[str, str]]:
    # Splits markdown text into (section_name, section_text) pairs using ## headings
    sections = []
    current_section = ""
    current_lines = []
    in_code_block = False

    for line in text.splitlines():
        # headers inside a code block are not real headers
        if line.startswith("```"):
            in_code_block = not in_code_block

        if line.startswith("## ") and not in_code_block:
            # Save the section we were building before starting a new one
            if current_lines:
                sections.append((current_section, "\n".join(current_lines)))
            current_section = line[3:].strip() # '## Docker Compose -> Docker Compose'
            current_lines = [line] # Keep the heading in the text because it helps embeddings
        else:
            current_lines.append(line)

    # The last section has no heading after it, so save it here
    if current_lines:
        sections.append((current_section, "\n".join(current_lines)))

    return sections





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
        name="devops_docs_600"
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

