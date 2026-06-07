"""
Milestone 3 — Document Ingestion and Chunking

Loads Rate My Professors JSON files (one per professor), produces one chunk
per student review, and saves the dataset to data/processed/chunks.json for
Milestone 4.

Chunk schema:
  chunk_id          — unique identifier: <professor_legacyId>_<rating_legacyId>
  text              — cleaned student review comment (chunk content)
  professor_name    — full name of the professor
  professor_id      — RMP legacy ID of the professor
  source_file       — JSON filename the review came from
  course            — course number from the review (e.g. "CS340")
  date              — review submission date string
  difficulty_rating — per-review difficulty score (1–5)
  helpful_rating    — per-review helpfulness score (1–5)
  grade             — grade the reviewer received ("A", "B+", etc., or "")
  would_take_again  — 1 (yes), 0 (no), or null
  rating_tags       — tags the reviewer selected
"""

import glob
import html
import json
import os
import re

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents", "rmp")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "processed", "chunks.json")


def clean_text(text: str) -> str:
    """Decode HTML entities, strip edges, collapse internal whitespace."""
    text = html.unescape(text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_course(course: str) -> str:
    """Prepend 'CS' to bare numeric course numbers; leave everything else as-is."""
    if course.isdigit():
        return "CS" + course
    return course


def load_chunks(documents_dir: str) -> tuple[list[dict], int, int, int]:
    """Return (chunks, total_docs, total_chunks, skipped)."""
    json_files = sorted(glob.glob(os.path.join(documents_dir, "*.json")))
    chunks = []
    total_docs = 0
    skipped = 0

    for filepath in json_files:
        source_file = os.path.basename(filepath)
        with open(filepath, encoding="utf-8") as fh:
            data = json.load(fh)

        prof = data["professor"]
        professor_name = f"{prof['firstName']} {prof['lastName']}"
        professor_id = prof["legacyId"]
        total_docs += 1

        for rating in data["ratings"]:
            text = clean_text(rating.get("comment", ""))
            if not text:
                skipped += 1
                continue

            chunk = {
                "chunk_id": f"{professor_id}_{rating['legacyId']}",
                "text": text,
                "professor_name": professor_name,
                "professor_id": professor_id,
                "source_file": source_file,
                "course": normalize_course(rating.get("class", "")),
                "date": rating.get("date", ""),
                "difficulty_rating": rating.get("difficultyRating"),
                "helpful_rating": rating.get("helpfulRating"),
                "grade": rating.get("grade", ""),
                "would_take_again": rating.get("wouldTakeAgain"),
                "rating_tags": rating.get("ratingTags", ""),
            }
            chunks.append(chunk)

    return chunks, total_docs, len(chunks), skipped


def print_sample_chunks(chunks: list[dict], n: int = 5) -> None:
    print(f"\n{'='*70}")
    print(f"SAMPLE CHUNKS (first {n})")
    print("=" * 70)
    for i, chunk in enumerate(chunks[:n], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"  chunk_id:         {chunk['chunk_id']}")
        print(f"  professor_name:   {chunk['professor_name']}")
        print(f"  course:           {chunk['course']}")
        print(f"  date:             {chunk['date']}")
        print(f"  difficulty:       {chunk['difficulty_rating']}")
        print(f"  helpful:          {chunk['helpful_rating']}")
        print(f"  grade:            {chunk['grade']}")
        print(f"  would_take_again: {chunk['would_take_again']}")
        print(f"  rating_tags:      {chunk['rating_tags']}")
        print(f"  source_file:      {chunk['source_file']}")
        print(f"  text:             {chunk['text'][:200]}{'...' if len(chunk['text']) > 200 else ''}")


def main() -> None:
    chunks, total_docs, total_chunks, skipped = load_chunks(DOCUMENTS_DIR)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(chunks, fh, indent=2, ensure_ascii=False)

    print_sample_chunks(chunks)

    print(f"\n{'='*70}")
    print("INGESTION SUMMARY")
    print("=" * 70)
    print(f"  Documents loaded:  {total_docs}")
    print(f"  Chunks created:    {total_chunks}")
    print(f"  Reviews skipped:   {skipped}  (empty comment)")
    print(f"  Output saved to:   {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
