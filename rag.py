"""
Milestone 5 — Grounded Generation and Query Interface

Imports the retrieval layer from embed.py (Milestone 4), passes the
retrieved reviews to Groq (llama-3.3-70b-versatile) as grounded context,
assembles source citations from retrieval metadata, and exposes a
command-line interface for interactive queries.

Sources are always assembled in Python from ChromaDB metadata — the LLM
is never asked to identify its own sources.

Two layers of grounding protection:
  1. Distance gate: if the top retrieval distance exceeds MAX_DISTANCE,
     the LLM is not called at all and a refusal message is returned.
  2. Prompt gate: the system prompt instructs the LLM to respond with
     "I don't have enough information on that." if the retrieved reviews
     do not contain enough evidence, even when the distance is acceptable.

Usage:
    python rag.py              # runs test queries then starts the CLI
    python rag.py --test-only  # runs test queries and exits
"""

import os
import re
import sys

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from embed import (
    CHROMA_DIR,
    COLLECTION_NAME,
    MODEL_NAME,
    TOP_K,
    retrieve,
)

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# Lazy initialization — shared objects created once, reused by CLI and UI
# ---------------------------------------------------------------------------

_state: dict = {}


def _init() -> None:
    """Initialize the embedding model, ChromaDB collection, and Groq client.
    Safe to call multiple times — only runs on the first call."""
    if _state:
        return
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        sys.exit("Error: GROQ_API_KEY not found. Add it to your .env file.")
    print("Loading embedding model and vector store ...")
    _state["model"] = SentenceTransformer(MODEL_NAME)
    _state["collection"] = (
        chromadb.PersistentClient(path=CHROMA_DIR).get_collection(COLLECTION_NAME)
    )
    _state["groq"] = Groq(api_key=api_key)
    # Load all unique professor names from stored metadata for filter detection.
    all_metadata = _state["collection"].get(include=["metadatas"])["metadatas"]
    _state["professor_names"] = sorted({m["professor_name"] for m in all_metadata})
    print(f"Ready. Collection has {_state['collection'].count()} documents.\n")

# Cosine distance thresholds for the retrieval gate.
#
# MAX_DISTANCE applies when no metadata filter is active. The retrieved chunks
# could be from anywhere in the corpus, so a strict threshold protects against
# off-topic results (e.g. the housing-lottery query scores 0.61 and is blocked).
#
# MAX_DISTANCE_FILTERED applies when a professor or course filter is active.
# The filter already constrains results to the right document(s), so the
# distance gate only needs to block genuinely nonsensical filtered queries.
# Short generic questions like "What do students say about CS340?" score ~0.62
# against relevant reviews — a permissive threshold handles them correctly.
MAX_DISTANCE = 0.55
MAX_DISTANCE_FILTERED = 0.75

SYSTEM_PROMPT = """\
You are a helpful assistant that answers questions about student experiences \
with Computer Science professors at Sonoma State University.

You may ONLY use the student reviews provided below as evidence. \
Do not use any outside knowledge. Do not invent facts. Do not invent sources.

If the provided reviews do not contain enough information to answer the \
question, respond with exactly:
I don't have enough information on that.
"""

NO_INFO = "I don't have enough information on that."

TEST_QUERIES = [
    {
        "query": "What do students say about CS340 with Mark Gondree?",
        "professor_name": "Mark Gondree",
        "course": "CS340",
    },
    {
        "query": "What do students say about CS315 with Ali Kooshesh?",
        "professor_name": "Ali Kooshesh",
        "course": "CS315",
    },
    {
        "query": "What complaints appear in reviews of Tia Watts's CS215 course?",
        "professor_name": "Tia Watts",
        "course": "CS215",
    },
    {
        # Out-of-scope query — corpus contains no housing information.
        # Expected: distance gate triggers and returns the refusal message.
        "query": "What do students say about the Sonoma State housing lottery?",
    },
]


# ---------------------------------------------------------------------------
# Metadata filter detection
# ---------------------------------------------------------------------------

def detect_filters(question: str) -> tuple[str | None, str | None]:
    """
    Scan the question for a known professor name and/or a CS course number.

    Professor matching: checks the full name first, then the last name alone,
    both case-insensitively. Last-name matching handles typical phrasings like
    "What do students say about Kooshesh?" without requiring the full name.

    Course matching: looks for patterns like CS215 or CS340 (3-4 digits after
    'CS', case-insensitive). Returns the match normalized to uppercase so it
    aligns with the stored metadata values.
    """
    q_lower = question.lower()
    professor_name = None

    for name in _state["professor_names"]:
        if name.lower() in q_lower:
            professor_name = name
            break
        last_name = name.split()[-1]
        if last_name.lower() in q_lower:
            professor_name = name
            break

    course = None
    match = re.search(r"\bCS\d{3,4}\b", question, re.IGNORECASE)
    if match:
        course = match.group(0).upper()

    return professor_name, course


# ---------------------------------------------------------------------------
# Context and source formatting
# ---------------------------------------------------------------------------

def format_context(results: dict) -> str:
    """
    Format retrieved review texts as a numbered list for the LLM prompt.
    Each entry includes the professor name and course from retrieval metadata
    so the model never has to refer to a review by number alone.
    """
    reviews = results["documents"][0]
    metadatas = results["metadatas"][0]
    blocks = []
    for i, (text, meta) in enumerate(zip(reviews, metadatas), start=1):
        blocks.append(
            f"Review {i}\n"
            f"Professor: {meta['professor_name']}\n"
            f"Course: {meta['course']}\n\n"
            f"{text}"
        )
    return "\n\n".join(blocks)


def extract_sources(results: dict) -> list[str]:
    """
    Return deduplicated source strings from ChromaDB metadata.
    The LLM does not produce these — they are assembled here in Python.
    Each string is formatted as: 'Professor Name Reviews (filename.json)'
    """
    seen = set()
    sources = []
    for meta in results["metadatas"][0]:
        key = (meta["professor_name"], meta["source_file"])
        if key not in seen:
            seen.add(key)
            sources.append(f"{meta['professor_name']} Reviews ({meta['source_file']})")
    return sources


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate(
    groq_client: Groq,
    query: str,
    results: dict,
    professor_name: str | None = None,
    course: str | None = None,
) -> str:
    """
    Pass the retrieved reviews to the LLM as context and return its answer.

    The user message contains the question followed by the numbered reviews.
    When metadata filters were used, a context header is prepended so the LLM
    knows which professor or course the reviews belong to — the reviews
    themselves often say "this class" without naming the course number.
    The system prompt forbids the model from using outside knowledge and
    instructs it to refuse if the context is insufficient.
    """
    context = format_context(results)

    header_parts = []
    if professor_name:
        header_parts.append(professor_name)
    if course:
        header_parts.append(course)
    header = (
        f"Note: The following reviews are for {' / '.join(header_parts)} "
        f"at Sonoma State University.\n\n"
        if header_parts else ""
    )

    user_message = f"{header}Question: {query}\n\nStudent reviews:\n{context}"

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Retrieval diagnostics
# ---------------------------------------------------------------------------

def debug_retrieval(question: str) -> None:
    """Print raw retrieval results for a question without calling Groq."""
    _init()
    professor_name, course = detect_filters(question)

    active = [f"professor={professor_name}"] if professor_name else []
    if course:
        active.append(f"course={course}")
    filter_str = ", ".join(active) if active else "none (full collection search)"

    results = retrieve(
        _state["collection"], _state["model"], question,
        professor_name=professor_name,
        course=course,
    )

    ids = results["ids"][0]
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    print(f"\n{'='*70}")
    print(f"DEBUG RETRIEVAL: {question}")
    print(f"Filters: {filter_str}")
    print("=" * 70)
    for rank, (chunk_id, doc, meta, dist) in enumerate(
        zip(ids, docs, metas, distances), start=1
    ):
        print(f"\n  Rank {rank}  |  distance: {dist:.4f}")
        print(f"  professor_name: {meta['professor_name']}")
        print(f"  course:         {meta['course']}")
        print(f"  source_file:    {meta['source_file']}")
        print(f"  chunk:          {doc[:200]}{'...' if len(doc) > 200 else ''}")
    print()


# ---------------------------------------------------------------------------
# Full RAG pipeline
# ---------------------------------------------------------------------------

def ask(
    question: str,
    professor_name: str | None = None,
    course: str | None = None,
) -> dict:
    """
    Run the full RAG pipeline and return a result dict.

    Returns:
        {
            "answer":  str,        # generated answer or refusal message
            "sources": list[str],  # deduplicated source strings, empty on refusal
        }
    """
    _init()

    # Auto-detect filters from the question text when none are explicitly given.
    if professor_name is None and course is None:
        professor_name, course = detect_filters(question)

    # Debug: print which filters are active for this query.
    active = [f"professor={professor_name}"] if professor_name else []
    if course:
        active.append(f"course={course}")
    print(f"[filters] {', '.join(active) if active else 'none (full collection search)'}")

    results = retrieve(
        _state["collection"], _state["model"], question,
        professor_name=professor_name,
        course=course,
    )
    top_distance = results["distances"][0][0]

    # Use the permissive threshold when a metadata filter is active.
    # The filter already guarantees topical relevance; the gate only needs
    # to block nonsensical inputs, not short/generic on-topic questions.
    threshold = MAX_DISTANCE_FILTERED if (professor_name or course) else MAX_DISTANCE
    print(f"[distance] top={top_distance:.4f}  threshold={threshold}")

    if top_distance > threshold:
        return {"answer": NO_INFO, "sources": []}

    return {
        "answer": generate(_state["groq"], question, results,
                           professor_name=professor_name, course=course),
        "sources": extract_sources(results),
    }


def answer(
    query: str,
    professor_name: str | None = None,
    course: str | None = None,
) -> None:
    """Call ask() and print the result to the terminal."""
    result = ask(query, professor_name=professor_name, course=course)
    print(f"\nQuestion:\n  {query}")
    print(f"\nAnswer:\n{result['answer']}")
    if result["sources"]:
        print("\nSources:")
        for s in result["sources"]:
            print(f"  * {s}")
    else:
        print("\nSources:\n  * No relevant sources found")
    print("-" * 70)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    _init()

    # --- automated test queries ---
    print("=" * 70)
    print("AUTOMATED TEST QUERIES")
    print("=" * 70)
    for item in TEST_QUERIES:
        answer(
            item["query"],
            professor_name=item.get("professor_name"),
            course=item.get("course"),
        )

    if "--test-only" in sys.argv:
        return

    # --- interactive CLI ---
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE  (type 'quit' or press Ctrl+C to exit)")
    print("=" * 70)
    while True:
        try:
            query = input("\nQuestion:\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not query or query.lower() in {"quit", "exit"}:
            break

        answer(query)


if __name__ == "__main__":
    main()
