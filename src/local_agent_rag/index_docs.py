"""
First part of RAG workflow - it turns documents into chunks, embeds them
and stores in a database.

Workflow:
docs/*.md  →  load  →  split by "## " headings  →  split into ~600-char chunks
           →  embed each chunk (Ollama)  →  save to Chroma (vector_store/)
"""
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embedding_demo import get_embedding # used to send text to Ollama embed model

# We need to set up data for text splitter to work on:
# docs directory, chunks size and overlap
# locate docs relative to the script, not from where it is run
# __file__ is the path to this script
DOCS_DIR = Path(__file__).resolve().parent / "docs"

CHUNK_SIZE = 600 # characters (not tokens)
CHUNK_OVERLAP = 100 # to preserve contexts in adjacent chunks

def load_documents() -> list[tuple[str, str]]:
    # Loads documents from md files to later split them into chunks
    # It returns a list where each item is a tuple with document filename and contents
    # [
    # ("docker.md", "# Docker\n\n## Images and containers\n..."),
    # ("kubernetes.md", "..."),
    # ]
    documents = []

    for path in DOCS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        documents.append((path.name, text))
    print("============Documents==========")
    print(documents)
    print("===============================")
    return documents

def split_into_sections(text: str) -> list[tuple[str, str]]:
    """
    Splits markdown text into (section_name, section_text) pairs using ## headings
    It goes through each line one by one and when encounters a new heading, saves 
    the previous section and starts the next one
    """
    sections = []
    current_section = "" # name of the section we're inside right now
    current_lines = [] # lines collected for that section so far
    in_code_block = False # are we inside a ``` block?

    for line in text.splitlines():
        # headers inside a code block are not real headers
        if line.startswith("```"):
            in_code_block = not in_code_block

        if line.startswith("## ") and not in_code_block:
            # On second encounter it means we now need to save the contents of current section
            if current_lines:
                sections.append((current_section, "\n".join(current_lines)))
            current_section = line[3:].strip() # '## Docker Compose -> Docker Compose'
            # Keep the heading in the text because it helps embeddings
            # and start collecting lines again
            current_lines = [line] 
        else:
            # This part runs for every ordinary text within a section
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
    # Each chunk becomes a dictionary
    # {
    #     "id": "docker.md-3",              # unique: filename + running number
    #     "text": "## Dockerfile basics\n\nEach instruction ...",
    #     "source": "docker.md",            # which file it came from
    #     "section": "Dockerfile basics",   # which heading it was under
    # }


    for filename, text in documents:
        index = 0

        for section, section_text in split_into_sections(text):
            for chunk_text in splitter.split_text(section_text):
                chunks.append(
                    {
                        "id": f"{filename}-{index}",
                        "text": chunk_text,
                        "source": filename,
                        "section": section,
                    }
                )
                index += 1

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
        path=Path(__file__).resolve().parent / "vector_store"
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
    # ids        = ["docker.md-0", "docker.md-1", ...]
    # texts      = ["# Docker", "## Images and containers ...", ...]
    # embeddings = [[0.012, -0.33, ...], [...], ...]   # one Ollama call per chunk
    # metadatas  = [{"source": "docker.md", "section": ""}, ...
    for chunk in chunks:
        ids.append(chunk["id"])
        texts.append(chunk["text"])
        embeddings.append(
            get_embedding(chunk["text"])
        )
        metadatas.append(
            {
                "source": chunk["source"],
                "section": chunk["section"]
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

