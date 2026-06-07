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
| 1 | What do students commonly say about Glenn Carter's teaching style? | Glenn Carter is frequently described as caring, enthusiastic, helpful, and passionate about teaching. Students often mention that he makes introductory computer science approachable and enjoyable. |
| 2 | What concerns do students raise about Tia Watts? | Reviews are mixed. Positive reviews praise her knowledge and willingness to help, while negative reviews commonly mention disorganization, slow grading, unclear labs, and arriving late to class. |
| 3 | What do students say about Ali Kooshesh's courses? | Students consistently describe his courses as challenging and demanding, but also describe him as knowledgeable, fair, and helpful when students seek assistance. |
| 4 | Which professor receives the strongest praise for being caring and supportive of students? | Mark Gondree and Gurman Gill are frequently described as caring, supportive, accessible, and invested in student success. |
| 5 | What complaints do students make about Anamary Leal's classes? | Reviews frequently mention unclear instruction, self-teaching requirements, poor communication, grading concerns, and difficulty connecting lectures to labs or assignments. |

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

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
