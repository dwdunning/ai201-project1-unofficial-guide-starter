# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain


This project focuses on student reviews of Computer Science professors at Sonoma State University. While Rate My Professors provides access to individual reviews, students often need to read dozens of reviews across multiple professor pages to answer questions about teaching style, workload, exam difficulty, grading practices, and feedback quality.

This RAG system makes that information searchable through natural language questions and provides grounded summaries with source attribution. Instead of manually browsing reviews, students can ask questions such as "Which professors are considered beginner-friendly?" or "What do students say about Mark Gondree's exams?" and receive answers synthesized from the underlying reviews.

---

## Documents

| #  | Source                  | Description                                                                                                   | File                                         |
| -- | ----------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 1  | Mark Gondree Reviews    | 24 student reviews covering teaching style, exams, workload, grading, and course experiences.                 | `documents/rmp/mark_gondree_2222240.json`    |
| 2  | Lynn Stauffer Reviews   | 33 student reviews covering teaching effectiveness, assignments, exams, and overall course satisfaction.      | `documents/rmp/lynn_stauffer_62597.json`     |
| 3  | Ali Kooshesh Reviews    | 46 student reviews covering lectures, grading practices, course difficulty, and student feedback.             | `documents/rmp/ali_kooshesh_62598.json`      |
| 4  | Suzanne Rivoire Reviews | 32 student reviews covering workload, teaching quality, exams, and learning outcomes.                         | `documents/rmp/suzanne_rivoire_1213020.json` |
| 5  | Gurman Gill Reviews     | 23 student reviews covering assignments, classroom experience, and professor accessibility.                   | `documents/rmp/gurman_gill_2083075.json`     |
| 6  | B. Ravikumar Reviews    | 38 student reviews covering course rigor, grading standards, lecture quality, and exams.                      | `documents/rmp/b_ravikumar_62601.json`       |
| 7  | Tia Watts Reviews       | 41 student reviews covering communication style, workload, assignments, and teaching effectiveness.           | `documents/rmp/tia_watts_62602.json`         |
| 8  | Glenn Carter Reviews    | 162 student reviews covering course structure, grading, exams, engagement, and long-term student experiences. | `documents/rmp/glenn_carter_25142.json`      |
| 9  | Shubbhi Taneja Reviews  | 13 student reviews covering responsiveness, workload, teaching style, and learning outcomes.                  | `documents/rmp/shubbhi_taneja_2484473.json`  |
| 10 | Anamary Leal Reviews    | 11 student reviews covering assignments, grading, communication, and overall student experience.              | `documents/rmp/anamary_leal_2409598.json`    |

---

## Chunking Strategy

The raw data was scraped from Rate My Professors and stored as JSON files, with one file per professor and one object per student rating. Because each rating contains a complete student review, each review will be treated as a single chunk.

**Chunk size:**

* One student review per chunk (typically 1-5 sentences)

**Overlap size:**

* 0 overlap

This strategy fits the structure of the documents because the reviews are already short and self-contained. Splitting reviews by a fixed character or token count could separate important context and make individual chunks harder to understand. Combining multiple reviews into a larger chunk could mix unrelated opinions about exams, workload, grading, and teaching style, reducing retrieval precision.

Using one review per chunk should make retrieval more targeted. For example, if a user asks about exam difficulty, the system can retrieve specific reviews discussing exams instead of returning a larger chunk that contains unrelated comments. Each chunk will also retain metadata such as professor name, course number, review date, difficulty rating, and source file to improve retrieval quality and source attribution.

---

## Retrieval Approach

**Embedding model:**
I will use `all-MiniLM-L6-v2` through the `sentence-transformers` library. This model runs locally, does not require paid API credits, and is recommended for this project.

**Top-k:**
I will retrieve the top 5 most relevant chunks for each user query.

**Production tradeoff reflection:**
If I were deploying this system for real users and cost was not a constraint, I would compare different embedding models based on accuracy, context length, latency, and cost. A larger embedding model might capture more subtle meaning in student reviews, but it could be slower or more expensive. I would also consider whether the model handles informal student language well, since reviews may include slang, abbreviations, and inconsistent wording.

---


## Evaluation Plan

| # | Question | Expected Answer |
|---|----------|-----------------|
| 1 | What do students say about CS340 with Mark Gondree? | Students describe CS340 with Gondree as engaging and interesting, especially because security is his specialty. Reviews mention that lectures can be dense, but he makes them easier to get through with humor, helpful explanations, labs, and office hours. |
| 2 | What do students say about CS315 with Ali Kooshesh? | Students describe CS315 with Kooshesh as difficult, demanding, and project-heavy. Many reviews say students need to start early, attend class, take notes, ask questions, and put in serious effort to succeed. |
| 3 | What complaints appear in reviews of Tia Watts's CS215 course? | Complaints about CS215 with Watts include confusing or poorly written labs, disorganization, late grading, unclear lectures, and students feeling like they had to teach themselves parts of the material. |
| 4 | What do students say about Glenn Carter's CS101 course? | Students commonly describe CS101 with Carter as approachable, helpful, and often easy if students attend, study, and complete the online/lab work. Reviews also mention that he is caring, enthusiastic, and supportive. |
| 5 | What complaints appear in reviews of Anamary Leal's CS115 course? | Complaints about CS115 with Leal include unclear instruction, lectures not matching labs, heavy self-teaching, difficult tests, limited help, and poor communication. |

---

## Anticipated Challenges

1. **Conflicting student opinions**

   Professor reviews are subjective, and different students often have very different experiences with the same professor. One review may describe a professor as caring and helpful, while another describes the same professor as disorganized or difficult. This could make it difficult for the retrieval and generation system to produce balanced summaries without overemphasizing a small number of reviews.

2. **Retrieval of irrelevant or incomplete reviews**

   Some reviews are extremely short (for example, "Great professor" or "Terrible teacher") and contain very little context. Semantic search may retrieve these reviews even when longer reviews provide better evidence. This could reduce answer quality and make it harder for the system to generate detailed, grounded responses.

3. **Cross-professor comparison questions**

   Questions such as "Which professor is most supportive?" require information from multiple source documents. The retrieval system may focus too heavily on one professor's reviews and miss relevant evidence from others, leading to incomplete or biased answers.

4. **Source attribution and traceability**

   The system must clearly identify which reviews and documents support each answer. If metadata is not stored correctly during ingestion and retrieval, responses may not be able to provide accurate citations, reducing trustworthiness and making evaluation more difficult.


---

## Architecture

```text
┌─────────────────────┐
│ Document Ingestion  │
│ JSON Review Files   │
│ (Rate My Professors)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Chunking            │
│ One Review          │
│ Per Chunk           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Embedding           │
│ all-MiniLM-L6-v2    │
│ sentence-transformers│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Vector Store        │
│ ChromaDB            │
│ + Metadata          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Retrieval           │
│ Top-5 Semantic      │
│ Search Results      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Generation          │
│ Groq                │
│ llama-3.3-70b       │
└─────────────────────┘
```


---

## AI Tool Plan

For the initial data scraping from ratemyprofessors, 

I asked Claude

"Investigate the Rate My Professors pages for these professors:

Mark Gondree https://www.ratemyprofessors.com/professor/2222240
Lynn Stauffer https://www.ratemyprofessors.com/professor/62597 
Ali Kooshesh https://www.ratemyprofessors.com/professor/62598 
Suzanne Rivoire https://www.ratemyprofessors.com/professor/1213020 
Gurman Gill https://www.ratemyprofessors.com/professor/2083075 
B. Ravikumar https://www.ratemyprofessors.com/professor/62601 
Tia Watts https://www.ratemyprofessors.com/professor/62602 
Glenn Carter https://www.ratemyprofessors.com/professor/25142 
Shubbhi Taneja https://www.ratemyprofessors.com/professor/2484473 
Anamary Leal https://www.ratemyprofessors.com/professor/2409598

Determine whether reviews can be extracted programmatically.

Check:
1. Whether reviews are embedded in the HTML.
2. Whether the site uses a GraphQL or REST API.
3. Whether there is a public endpoint returning review data.
4. Produce a Python script that downloads all reviews into JSON files if possible.

Do not write the final scraper until you've analyzed the page structure and API calls."
After we were able to make a working scraper and save all 423 reviews of the 10 professors as json files, I asked Claude to 

"Before writing any code, read:

1. `planning.md`
2. The JSON files in `documents/rmp/`
3. The existing repository structure

Your task is to implement only the ingestion and chunking pipeline described in `planning.md`.

Requirements:

* Follow the chunking strategy in `planning.md`.
* Use one review per chunk.
* Preserve metadata needed for source attribution.
* Create a processed chunk dataset suitable for the embedding stage.
* Print sample chunks for inspection.
* Report total documents loaded, chunks created, and skipped reviews.

Before writing code:

1. Summarize your understanding of my chunking strategy.
2. Explain which files you plan to create or modify.
3. Point out any inconsistencies between the JSON structure and the plan.

Only after that analysis should you implement the ingestion/chunking pipeline.
"

After confirming that Claude understood my instructions I had it write ingest.py
After running it I had to add functions to clean the text and normalize course numbers.

I asked it to copy 5 random chunks to a new file to spot check.
 
for embedding I asked "Before writing code, read:

1. `planning.md`
2. `ingest.py`
3. `data/processed/chunks.json`
4. The existing repository structure

I am now working on Milestone 4: Embeddings and Retrieval.

Your task is to implement only the embedding, vector store, and retrieval testing layer. Do not build generation, Groq, Gradio, or the final UI yet.

Project context:

* Milestone 3 produced `data/processed/chunks.json`.
* Each chunk has `text` plus metadata like `chunk_id`, `professor_name`, `course`, `source_file`, `date`, `difficulty_rating`, `helpful_rating`, and `rating_tags`.
* The planned embedding model is `all-MiniLM-L6-v2` using `sentence-transformers`.
* The planned vector store is ChromaDB.
* Retrieval should use top-k = 5.

Architecture for this milestone:
Document Ingestion → Chunking → Embedding with `all-MiniLM-L6-v2` → ChromaDB Vector Store → Top-5 Retrieval

Requirements:

1. Load chunks from `data/processed/chunks.json`.
2. Embed each chunk's `text` using `SentenceTransformer("all-MiniLM-L6-v2")`.
3. Store embeddings in ChromaDB with:

   * document text
   * unique chunk id
   * metadata needed for source attribution
4. Create or update a persistent ChromaDB database, preferably under `data/chroma_db/`.
5. Implement a retrieval function that accepts a query string and returns the top 5 most relevant chunks.
6. Print each result with:

   * rank
   * distance score
   * professor name
   * course
   * source file
   * chunk id
   * review text
7. Add a simple test script or CLI that runs at least these three evaluation queries:

   * What do students say about CS340 with Mark Gondree?
   * What do students say about CS315 with Ali Kooshesh?
   * What complaints appear in reviews of Tia Watts's CS215 course?
8. Keep the code simple and readable. I need to understand and explain it.
9. If you use a ChromaDB API pattern that may be unfamiliar, explain what it does.

Before writing code:

1. Summarize your understanding of Milestone 4.
2. Explain which files you plan to create or modify.
3. Confirm that the code will not include LLM generation yet.
4. Point out any assumptions or risks, especially around ChromaDB persistence or metadata types.

Only after that analysis should you implement the embedding and retrieval code."

Then I had to tweak it to use `normalize_embeddings=True` in both model.encode calls:
1. When embedding all chunk texts.
2. When embedding the query.

Then I asked for it to include distances in the evaluation queries

To try and resolve some of the retrieval errors, I asked Claude

"Milestone 4 retrieval passes the checkpoint, but I want one small improvement before moving to generation.

Please add optional metadata filtering to the retrieve() function.

Requirements:
- Keep the existing semantic-only retrieval behavior as the default.
- Add optional parameters: professor_name=None and course=None.
- If provided, pass a ChromaDB where filter using those metadata fields.
- Update the three evaluation test calls:
  1. Mark Gondree + CS340
  2. Ali Kooshesh + CS315
  3. Tia Watts + CS215
- Print whether a metadata filter was used.
- Do not add generation, Groq, or UI.

Important:
This should be a small extension, not a rewrite."



**Milestone 3 — Ingestion and chunking:**

Loads Rate My Professors JSON files (one per professor), produces one chunk per student review, and saves the dataset to data/processed/chunks.json for Milestone 4.

Chunk schema:

chunk_id — unique identifier:
<professor_legacyId>_<rating_legacyId>
text — cleaned student review comment (chunk content)
professor_name — full name of the professor
professor_id — RMP legacy ID of the professor
source_file — JSON filename the review came from
course — course number from the review (e.g. "CS340")
date — review submission date string
difficulty_rating — per-review difficulty score (1–5)
helpful_rating — per-review helpfulness score (1–5)
grade — grade the reviewer received ("A", "B+", etc., or "")
would_take_again — 1 (yes), 0 (no), or null
rating_tags — tags the reviewer selected """

5 random chunks retrieved for review 

[
  {
    "chunk_id": "1213020_31866126",
    "text": "Extremely disappointed in Rivoire. I can tell she has the potential to be an excellent professor, but her inability to grade anything by the time she promises is rough. She also makes mistakes in labs, missed many classes she had to assign a project a week before finals started. Unorganized and sloppy, but a nice woman.",
    "professor_name": "Suzanne Rivoire",
    "professor_id": 1213020,
    "source_file": "suzanne_rivoire_1213020.json",
    "course": "CS215",
    "date": "2019-05-14 04:58:52 +0000 UTC",
    "difficulty_rating": 3,
    "helpful_rating": 2,
    "grade": "B",
    "would_take_again": 0,
    "rating_tags": "Skip class? You won't pass."
  },
  {
    "chunk_id": "25142_22757520",
    "text": "Best Professor ever! I was about to change my major to Comp. Science. He was always energetic and he is very understanding. The class is hard for some, but I thought it was really easy because I did all the reading and studying.",
    "professor_name": "Glenn Carter",
    "professor_id": 25142,
    "source_file": "glenn_carter_25142.json",
    "course": "CS101",
    "date": "2014-01-15 17:42:59 +0000 UTC",
    "difficulty_rating": 1,
    "helpful_rating": 5,
    "grade": "",
    "would_take_again": null,
    "rating_tags": ""
  },
  {
    "chunk_id": "25142_2098316",
    "text": "Glenn is an awesome man. He knows he's a computer nerd and he's hilarious. He also knows that computer science is boring and he does his best to make it fun. Like one guy said, go to lecture, and take decent notes, you'll get a good grade",
    "professor_name": "Glenn Carter",
    "professor_id": 25142,
    "source_file": "glenn_carter_25142.json",
    "course": "CS101",
    "date": "2004-05-06 02:39:25 +0000 UTC",
    "difficulty_rating": 2,
    "helpful_rating": 5,
    "grade": "",
    "would_take_again": null,
    "rating_tags": ""
  },
  {
    "chunk_id": "2083075_27261356",
    "text": "He is very easy to talk to and truly wants each student to pass his course. Each lecture, he stops and makes sure people understand the material. He likes calling on people and \"test\" them on the material. It's intimidating but very helpful when you're called on and truly lost. He doesn't move on unless you get a clear understanding.",
    "professor_name": "Gurman Gill",
    "professor_id": 2083075,
    "source_file": "gurman_gill_2083075.json",
    "course": "CS115",
    "date": "2016-11-28 02:30:56 +0000 UTC",
    "difficulty_rating": 3,
    "helpful_rating": 5,
    "grade": "A-",
    "would_take_again": 1,
    "rating_tags": "Gives good feedback--Respected--ACCESSIBLE OUTSIDE CLASS"
  },
  {
    "chunk_id": "62601_21570860",
    "text": "Very kind but challenging teacher. Much of his lectures are spent by him discussing difficult and hardly related topics. He is very smart, though, and you will learn lots if you go into his office hours.",
    "professor_name": "B. Ravikumar",
    "professor_id": 62601,
    "source_file": "b_ravikumar_62601.json",
    "course": "CS315",
    "date": "2013-04-20 17:50:59 +0000 UTC",
    "difficulty_rating": 5,
    "helpful_rating": 5,
    "grade": "",
    "would_take_again": null,
    "rating_tags": ""
  }
]



**Milestone 4 — Embedding and retrieval:**
## Retrieval Test Results

### Query 1

**Query:** What do students say about CS340 with Mark Gondree?

**Result:**
Most of the retrieved chunks were reviews of Mark Gondree. Reviews described him as knowledgeable, helpful, caring, and enthusiastic about computer security. Several reviews specifically mentioned that CS340 was engaging because it aligned with his area of expertise.

**Retrieval Quality:** Partially Accurate

**Analysis:**
The retrieval system correctly identified Mark Gondree as the target professor, but some highly ranked results discussed Gondree's other courses rather than CS340 specifically. This suggests the embedding model prioritized the professor identity more strongly than the course number.

---

### Query 2

**Query:** What do students say about CS315 with Ali Kooshesh?

**Result:**
The retrieved reviews consistently described CS315 as challenging, demanding, and requiring significant effort. Students frequently recommended starting projects early, attending class, taking notes, and using office hours. Many reviews also described Kooshesh as knowledgeable and fair despite the course difficulty.

**Retrieval Quality:** Accurate

**Analysis:**
This was the strongest retrieval result. The top results were specifically about CS315 and Ali Kooshesh, and all retrieved chunks came from Kooshesh reviews. The query produced the lowest distance scores of the evaluation set (top result distance: 0.3555, average top-5 distance: 0.4108).

---

### Query 3

**Query:** What complaints appear in reviews of Tia Watts's CS215 course?

**Result:**
The retrieval system found reviews mentioning disorganization, slow grading, confusing labs, and unclear lectures. However, some retrieved chunks discussed complaints about other professors rather than Tia Watts.

**Retrieval Quality:** Partially Accurate

**Analysis:**
The query retrieved complaint-oriented reviews, but semantic similarity sometimes outweighed professor identity. Because multiple professors received similar complaints, some non-Tia-Watts reviews appeared among the top results. This query had the highest distance scores in the evaluation set (top result distance: 0.4443, average top-5 distance: 0.4658).

---

### Retrieval Summary

Retrieval was initially implemented using semantic similarity search only.
While this generally returned relevant reviews, some queries that asked
about a specific professor and course occasionally retrieved reviews from
other professors with similar language.

To improve precision, metadata filtering was added using professor name
and course number. This allowed semantic search to operate within a
smaller relevant subset of documents and significantly improved the
accuracy of course-specific queries.




**Milestone 5 — Generation and interface:**
