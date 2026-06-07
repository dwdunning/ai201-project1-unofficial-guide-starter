"""
Milestone 4 — Embedding and Retrieval

Loads the processed chunks produced by ingest.py, embeds each review's text
using the all-MiniLM-L6-v2 sentence-transformers model, stores the embeddings
in a persistent ChromaDB vector database, then runs three evaluation queries
to verify that retrieval is working.

Run this script once to build the database. You can safely run it again —
existing records will be updated in place rather than duplicated.

To start completely fresh, delete the data/chroma_db/ directory.
"""

import json
import os

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = os.path.join(os.path.dirname(__file__), "data", "processed", "chunks.json")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma_db")
COLLECTION_NAME = "rmp_reviews"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5
BATCH_SIZE = 100

EVAL_QUERIES = [
    "What do students say about CS340 with Mark Gondree?",
    "What do students say about CS315 with Ali Kooshesh?",
    "What complaints appear in reviews of Tia Watts's CS215 course?",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_chunks(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Metadata sanitization
# ---------------------------------------------------------------------------

def sanitize_metadata(chunk: dict) -> dict:
    """
    ChromaDB metadata values must be str, int, or float — not None.

    would_take_again is None for 270 of 423 reviews (the reviewer did not
    answer the question). We store -1 as a sentinel for 'not reported' so
    the upsert does not raise a ValueError.
    """
    def none_to_neg1(v):
        return v if v is not None else -1

    return {
        "professor_name": chunk["professor_name"],
        "professor_id": chunk["professor_id"],
        "source_file": chunk["source_file"],
        "course": chunk["course"],
        "date": chunk["date"],
        "difficulty_rating": none_to_neg1(chunk["difficulty_rating"]),
        "helpful_rating": none_to_neg1(chunk["helpful_rating"]),
        "grade": chunk["grade"],
        "would_take_again": none_to_neg1(chunk["would_take_again"]),
        "rating_tags": chunk["rating_tags"],
    }


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------

def build_vector_store(
    chunks: list[dict],
    model: SentenceTransformer,
) -> chromadb.Collection:
    """
    Embed all chunks and upsert them into a persistent ChromaDB collection.

    ChromaDB concepts used here:

    PersistentClient(path=...)
        Saves the database to disk so it survives between Python runs.
        Think of it like opening a SQLite file — the data stays there.

    get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
        Opens the named collection if it already exists, or creates a new
        one. The hnsw:space setting tells ChromaDB to measure similarity
        with cosine distance (lower = more similar, 0 = identical).
        We normalize embeddings during encode so that cosine distance is
        the correct metric. This setting is locked in at creation time.

    upsert(ids, documents, embeddings, metadatas)
        Inserts each record if the id is new; updates the existing record
        if the id is already in the collection. This makes the script safe
        to run more than once.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [sanitize_metadata(c) for c in chunks]

    print(f"Embedding {len(texts)} chunks with {MODEL_NAME} ...")
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=BATCH_SIZE,
    )

    for start in range(0, len(chunks), BATCH_SIZE):
        end = start + BATCH_SIZE
        collection.upsert(
            ids=ids[start:end],
            documents=texts[start:end],
            embeddings=embeddings[start:end].tolist(),
            metadatas=metadatas[start:end],
        )

    print(f"Stored {collection.count()} documents in ChromaDB at {CHROMA_DIR}\n")
    return collection


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(
    collection: chromadb.Collection,
    model: SentenceTransformer,
    query: str,
    top_k: int = TOP_K,
) -> dict:
    """
    Embed the query string and return the top_k most similar chunks.

    collection.query returns a dict whose values are lists-of-lists because
    ChromaDB supports sending multiple queries at once. Since we send one
    query at a time, we only use index [0] to get the results for that
    single query.

    Keys in the returned dict:
      ids[0]        — chunk_ids of the top results
      documents[0]  — the original review texts
      metadatas[0]  — the metadata dicts stored alongside each document
      distances[0]  — cosine distances (lower means more similar)
    """
    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )


def print_results(query: str, results: dict) -> None:
    ids = results["ids"][0]
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
    print("=" * 70)
    for rank, (chunk_id, doc, meta, dist) in enumerate(
        zip(ids, docs, metas, distances), start=1
    ):
        print(f"\n  Rank {rank}  |  distance: {dist:.4f}")
        print(f"  Professor:   {meta['professor_name']}")
        print(f"  Course:      {meta['course']}")
        print(f"  Source file: {meta['source_file']}")
        print(f"  Chunk ID:    {chunk_id}")
        print(f"  Text:        {doc[:300]}{'...' if len(doc) > 300 else ''}")

    print(f"\n  --- Distance summary ---")
    print(f"  Top result:  {distances[0]:.4f}")
    print(f"  Avg (top {len(distances)}): {sum(distances) / len(distances):.4f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    chunks = load_chunks(CHUNKS_FILE)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    model = SentenceTransformer(MODEL_NAME)
    print(f"Loaded embedding model: {MODEL_NAME}")

    os.makedirs(CHROMA_DIR, exist_ok=True)
    collection = build_vector_store(chunks, model)

    for query in EVAL_QUERIES:
        results = retrieve(collection, model, query)
        print_results(query, results)


if __name__ == "__main__":
    main()
