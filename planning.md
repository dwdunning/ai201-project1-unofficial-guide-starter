# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

## Domain

This project focuses on student reviews of Computer Science professors at Sonoma State University. While Rate My Professors provides access to individual reviews, students often need to read dozens of reviews across multiple professor pages to answer questions about teaching style, workload, exam difficulty, grading practices, and feedback quality.

This RAG system makes that information searchable through natural language questions and provides grounded summaries with source attribution. Instead of manually browsing reviews, students can ask questions such as "Which professors are considered beginner-friendly?" or "What do students say about Mark Gondree's exams?" and receive answers synthesized from the underlying reviews.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| #  | Source                  | Description                                                  | URL                                                          |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 1  | Mark Gondree Reviews    | 24 student reviews discussing teaching style, exams,         | https://www.ratemyprofessors.com/professor/2222240           |
|    |                         | workload, grading, and course experiences.                   |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 2  | Lynn Stauffer Reviews   | 33 student reviews discussing teaching effectiveness,        | https://www.ratemyprofessors.com/professor/62597             |
|    |                         | assignments, exams, and overall course satisfaction.         |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 3  | Ali Kooshesh Reviews    | 46 student reviews covering lectures, grading practices,     | https://www.ratemyprofessors.com/professor/62598             |
|    |                         | course difficulty, and student feedback.                     |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 4  | Suzanne Rivoire Reviews | 32 student reviews describing workload, teaching quality,    | https://www.ratemyprofessors.com/professor/1213020           |
|    |                         | exams, and learning outcomes.                                |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 5  | Gurman Gill Reviews     | 23 student reviews discussing assignments, classroom         | https://www.ratemyprofessors.com/professor/2083075           |
|    |                         | experience, and professor accessibility.                     |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 6  | B. Ravikumar Reviews    | 38 student reviews focused on course rigor, grading          | https://www.ratemyprofessors.com/professor/62601             |
|    |                         | standards, lecture quality, and exams.                       |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 7  | Tia Watts Reviews       | 41 student reviews discussing communication style,           | https://www.ratemyprofessors.com/professor/62602             |
|    |                         | workload, assignments, and teaching effectiveness.           |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 8  | Glenn Carter Reviews    | 162 student reviews describing course structure, grading,    | https://www.ratemyprofessors.com/professor/25142             |
|    |                         | exams, engagement, and long-term student experiences.        |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 9  | Shubbhi Taneja Reviews  | 13 student reviews discussing responsiveness, workload,      | https://www.ratemyprofessors.com/professor/2484473           |
|    |                         | teaching style, and learning outcomes.                       |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
| 10 | Anamary Leal Reviews    | 11 student reviews focused on assignments, grading,          | https://www.ratemyprofessors.com/professor/2409598           |
|    |                         | communication, and overall student experience.               |                                                              |
+----+-------------------------+--------------------------------------------------------------+--------------------------------------------------------------+
---

## Chunking Strategy

The documents in this project are Rate My Professors pages, and the main useful content is made up of short student reviews. Because each review usually represents one complete student opinion, I will split the documents so that each individual review becomes one chunk.

Chunk size:

One student review per chunk

Overlap size:

0 overlap

This strategy fits the structure of the documents because the reviews are already short and self-contained. Splitting by a fixed character count could cut a review in the middle of an important thought, which would make the chunk harder to understand during retrieval. Combining multiple reviews into one larger chunk could mix different opinions about exams, workload, grading, and teaching style, which would make semantic search less precise.

Using one review per chunk should make retrieval more targeted. For example, if a user asks about exam difficulty, the system can retrieve specific reviews that mention exams instead of pulling in large sections containing unrelated comments.

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

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

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
