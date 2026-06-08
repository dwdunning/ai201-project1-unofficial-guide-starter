# The Unofficial Guide — Project 1


---

## Domain

This project focuses on student reviews of Computer Science professors at Sonoma State University. While Rate My Professors provides access to individual reviews, students often need to read dozens of reviews across multiple professor pages to answer questions about teaching style, workload, exam difficulty, grading practices, and feedback quality.

This RAG system makes that information searchable through natural language questions and provides grounded summaries with source attribution. Instead of manually browsing reviews, students can ask questions such as "Which professors are considered beginner-friendly?" or "What do students say about Mark Gondree's exams?" and receive answers synthesized from the underlying reviews.
---

## Document Sources

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

**Chunk size:**

* One student review per chunk (typically 1-5 sentences)

**Overlap:**

* 0 overlap

No overlap was used because each review already represents a complete, self-contained opinion. Overlap is often useful when splitting long documents into smaller sections to preserve context across chunk boundaries, but the reviews in this corpus are short enough that additional overlap would only duplicate information and increase storage and retrieval redundancy.

**Why these choices fit your documents:**

The source data consists of Rate My Professors reviews stored as JSON files, with one file per professor and one rating object per student review. Because each review is already a short, self-contained opinion, splitting reviews into smaller chunks would risk separating important context, while combining multiple reviews into larger chunks would mix unrelated opinions about teaching style, workload, grading, exams, and course difficulty.

Before chunking, the ingestion pipeline:

* Decoded HTML entities (for example, `&quot;`)
* Normalized whitespace and line breaks
* Removed empty reviews
* Preserved metadata such as professor name, course number, review date, difficulty rating, helpfulness rating, and source filename

This approach allowed the retrieval system to return highly specific reviews that directly addressed a user's question while preserving enough context for grounded answer generation.

**Final chunk count:**

* 423 chunks across 10 source documents


## Sample Chunks

### Chunk 1

**Source:** `suzanne_rivoire_1213020.json`
**Professor:** Suzanne Rivoire
**Course:** CS215

> Extremely disappointed in Rivoire. I can tell she has the potential to be an excellent professor, but her inability to grade anything by the time she promises is rough. She also makes mistakes in labs, missed many classes she had to assign a project a week before finals started. Unorganized and sloppy, but a nice woman.

---

### Chunk 2

**Source:** `glenn_carter_25142.json`
**Professor:** Glenn Carter
**Course:** CS101

> Best Professor ever! I was about to change my major to Comp. Science. He was always energetic and he is very understanding. The class is hard for some, but I thought it was really easy because I did all the reading and studying.

---

### Chunk 3

**Source:** `glenn_carter_25142.json`
**Professor:** Glenn Carter
**Course:** CS101

> Glenn is an awesome man. He knows he's a computer nerd and he's hilarious. He also knows that computer science is boring and he does his best to make it fun. Like one guy said, go to lecture, and take decent notes, you'll get a good grade.

---

### Chunk 4

**Source:** `gurman_gill_2083075.json`
**Professor:** Gurman Gill
**Course:** CS115

> He is very easy to talk to and truly wants each student to pass his course. Each lecture, he stops and makes sure people understand the material. He likes calling on people and "test" them on the material. It's intimidating but very helpful when you're called on and truly lost. He doesn't move on unless you get a clear understanding.

---

### Chunk 5

**Source:** `b_ravikumar_62601.json`
**Professor:** B. Ravikumar
**Course:** CS315

> Very kind but challenging teacher. Much of his lectures are spent by him discussing difficult and hardly related topics. He is very smart, though, and you will learn lots if you go into his office hours.

---

## Embedding Model

**Model used:**

I used `all-MiniLM-L6-v2` through the `sentence-transformers` library. This model creates 384-dimensional embeddings, runs locally, and is fast enough for a small class project. It also works well for short text chunks, which fits this corpus because each chunk is one student review.

The embeddings are stored in ChromaDB using cosine distance. During embedding, I used normalized embeddings so that cosine similarity would be consistent for both stored chunks and user queries.

**Production tradeoff reflection:**

If this system were deployed for real users and cost was not a constraint, I would compare embedding models based on retrieval accuracy, context length, latency, deployment cost, and support for informal student language. A larger model might better understand vague questions, slang, abbreviations, and course-specific phrasing, but it would likely be slower and more expensive. I would also consider whether the model should run locally or through an API. A local model gives more control and avoids API costs, while an API-hosted model may provide stronger accuracy and easier scaling.

---

## Grounded Generation

**System prompt grounding instruction:**

The generation layer uses a system prompt that explicitly restricts the model to the retrieved reviews:

> You may ONLY use the student reviews provided below as evidence. Do not use any outside knowledge. Do not invent facts. Do not invent sources.
>
> If the provided reviews do not contain enough information to answer the question, respond with exactly:
>
> "I don't have enough information on that."

In addition, retrieved reviews are formatted as numbered context blocks that include metadata such as professor name and course number. This allows the model to reference the correct professor and course while generating its answer.

The system also includes a retrieval-level safety check. Before calling the LLM, the top retrieval distance is compared against a threshold. If the distance exceeds the threshold, the model is not called and the system immediately returns:

> "I don't have enough information on that."

This prevents the model from generating answers when retrieval results are too dissimilar to the user's question.

**How source attribution is surfaced in the response:**

Source attribution is generated programmatically rather than by the LLM. After retrieval, the system extracts metadata from the retrieved chunks and builds a source list using the professor name and source filename. The model never generates citations itself.

For example:

* Mark Gondree Reviews (`mark_gondree_2222240.json`)
* Gurman Gill Reviews (`gurman_gill_2083075.json`)

Because citations come directly from retrieval metadata, the system avoids hallucinated sources and ensures that every cited document corresponds to an actual retrieved review.


---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about CS340 with Mark Gondree? | Students describe CS340 with Gondree as engaging and interesting, especially because security is his specialty. Reviews mention that lectures can be dense, but he makes them easier to get through with humor, helpful explanations, labs, and office hours.| Most of the retrieved chunks were reviews of Mark Gondree. Reviews described him as knowledgeable, helpful, caring, and enthusiastic about computer security. Several reviews specifically mentioned that CS340 was engaging because it aligned with his area of expertise. | Relevant | Partially accurate |
| 2 | What do students say about CS315 with Ali Kooshesh? | Students describe CS315 with Kooshesh as difficult, demanding, and project-heavy. Many reviews say students need to start early, attend class, take notes, ask questions, and put in serious effort to succeed |The retrieved reviews consistently described CS315 as challenging, demanding, and requiring significant effort. Students frequently recommended starting projects early, attending class, taking notes, and using office hours. Many reviews also described Kooshesh as knowledgeable and fair despite the course difficulty. | Relevant | Accurate |
| 3 | What complaints appear in reviews of Tia Watts's CS215 course? | Complaints about CS215 with Watts include confusing or poorly written labs, disorganization, late grading, unclear lectures, and students feeling like they had to teach themselves parts of the material. | The retrieval system found reviews mentioning disorganization, slow grading, confusing labs, and unclear lectures. However, some retrieved chunks discussed complaints about other professors rather than Tia Watts. | Partially Relevant | Partially Accurate |
| 4 | What do students say about Glenn Carter's CS101 course? | Students commonly describe CS101 with Carter as approachable, helpful, and often easy if students attend, study, and complete the online/lab work. Reviews also mention that he is caring, enthusiastic, and supportive. | The system reported that students generally consider CS101 easy with a manageable workload. It highlighted Carter as funny, outgoing, caring, and supportive, noted that students appreciated his online notes, and mentioned some criticism of lecture delivery and exam details. | Relevant | Accurate |
| 5 | What complaints appear in reviews of Anamary Leal's CS115 course? | Complaints about CS115 with Leal include unclear instruction, lectures not matching labs, heavy self-teaching, difficult tests, limited help, and poor communication. |  The system identified complaints including poor teaching, disconnects between lectures and labs, lack of support, unclear explanations, heavy coursework with self-teaching, unresponsiveness, and poor communication with students. | Relevant | Accurate |

The evaluation table reflects the initial semantic-only retrieval tests used during development. Later iterations improved retrieval quality through metadata filtering.

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

What complaints appear in reviews of Tia Watts's CS215 course?

**What the system returned:**

In the initial semantic-only retrieval version, the system retrieved some relevant Tia Watts CS215 reviews, but it also retrieved complaint-focused reviews from other professors, including B. Ravikumar. The results were related to the idea of complaints, but they were not all from the requested professor and course.

**Root cause (tied to a specific pipeline stage):**

The failure occurred in the retrieval stage. The first version of retrieval used semantic similarity only, so the embedding model prioritized complaint-related language such as "confusing," "difficult," "unclear," and "tough grader." Because similar complaint language appeared in reviews for multiple professors, ChromaDB returned some reviews that were semantically similar but did not match the requested metadata constraints.

This was not a chunking failure because the chunks were complete student reviews. It was also not primarily a generation failure because the LLM was answering from the retrieved context. The problem was that the retrieved context included some off-target reviews.

**What you would change to fix it:**

I added metadata filtering by professor name and course number before semantic search. When a query includes a known professor or course, the system now filters the ChromaDB search space before ranking by embedding similarity. For example, the Tia Watts CS215 query is filtered to reviews where `professor_name = "Tia Watts"` and `course = "CS215"`.

This improved precision because semantic search now runs only within the relevant subset of documents. A future improvement would be to make the metadata extraction more robust, such as handling nicknames, misspellings, and alternate course formats.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The planning document provided a clear structure for building the system incrementally. Defining the document sources, chunking strategy, retrieval approach, and evaluation questions before writing code made it easier to implement and test each stage of the pipeline separately. The chunking plan was especially useful because it justified treating each review as a single chunk, which simplified ingestion and produced a corpus of 423 meaningful chunks for retrieval.

**One way your implementation diverged from the spec, and why:**

The original plan described retrieval as a simple top-k semantic search using embeddings and ChromaDB. During testing, I found that semantic similarity alone sometimes retrieved reviews from the wrong professor when multiple professors had similar complaint language. To improve precision, I added metadata filtering by professor name and course number before retrieval. I also added a retrieval-distance threshold that prevents the LLM from answering when the retrieved chunks are not sufficiently relevant. These changes were not part of the original plan, but they improved grounding and reduced hallucinations during generation.


---

## AI Usage

**Instance 1**

* *What I gave the AI:*

  * My `planning.md` chunking strategy, document descriptions, and architecture diagram.
  * Instructions to implement the Milestone 3 ingestion and chunking pipeline using the Rate My Professors JSON files.

* *What it produced:*

  * An `ingest.py` script that loaded the JSON files, extracted reviews, created one chunk per review, and saved the chunks to a JSON file.

* *What I changed or overrode:*

  * The initial version only stripped whitespace from review text. I directed the AI to add a cleaning function that decodes HTML entities, normalizes whitespace, removes empty reviews, and saves the processed chunks to `data/processed/chunks.json` instead of the project root. I also reviewed sample chunks and verified that each chunk was a complete review rather than a fragment.

---

**Instance 2**

* *What I gave the AI:*

  * My retrieval design from `planning.md` and the results of Milestone 4 retrieval testing.
  * Retrieval examples where semantic search returned reviews from the wrong professor when multiple professors had similar complaint language.

* *What it produced:*

  * A ChromaDB retrieval pipeline using `all-MiniLM-L6-v2` embeddings and top-k semantic search.

* *What I changed or overrode:*

  * During testing, I discovered that semantic similarity alone sometimes retrieved reviews from other professors. I instructed the AI to add metadata filtering by professor name and course number before retrieval. I also added a retrieval-distance threshold that prevents the LLM from generating an answer when the retrieved chunks are not sufficiently relevant. These changes improved grounding and reduced incorrect answers for course-specific questions.

## Query Interface

Input:
- Natural language question

Output:
- Generated answer
- Source citations

Example Interaction

Question:
What do students say about Glenn Carter?

Answer:
Students say that Glenn Carter is a great teacher, very funny and outgoing, and really knows what he's talking about. They appreciate that his notes are available online and that he helps students understand the material. Many students have expressed their admiration for him, with some even calling him their "hero". They also mention that the class is simple if you attend lectures and take average notes, and that he's willing to accommodate students who need to take tests on different days. Overall, students have a very positive opinion of Glenn Carter and enjoy his teaching style.

Sources:
Glenn Carter Reviews (glenn_carter_25142.json)

Example Interaction 2

Question:
What do students say about CS351 with Suzanne Rivoire?

Answer:
Students say that Dr. Suzanne Rivoire makes difficult topics easy to understand, is a great lecturer, and is passionate and caring. However, some students have expressed concerns about her grading, stating that she is not great at returning graded work, and that she doesn't grade homework assignments in a timely manner, leaving students unsure of their grade in the course. One student also mentioned that the class was too easy and that Dr. Rivoire could have covered more material. Overall, students seem to appreciate Dr. Rivoire's teaching style, but have some issues with her grading practices.

Sources:
Suzanne Rivoire Reviews (suzanne_rivoire_1213020.json)

## Out-of-Scope Query Example

Question:
What do students say about the food in the Kitchens?

Response:
I don't have enough information on that.

Reason:
Top retrieval distance exceeded the threshold, so the LLM was not called.



## Retrieval Test Results

### Query 1: CS340 with Mark Gondree

Query: What do students say about CS340 with Mark Gondree?
Filters applied: professor=Mark Gondree, course=CS340

Rank	Distance	Source File	Professor	Course
1	0.4316	mark_gondree_2222240.json	Mark Gondree	CS340
2	0.4921	mark_gondree_2222240.json	Mark Gondree	CS340
3	0.7464	mark_gondree_2222240.json	Mark Gondree	CS340
Rank 1:

"Dr. Gondree is a great professor and it's clear that Computer Security is his passion. He is constantly cracking jokes which makes the otherwise DENSE powerpoint lectures more fun to get through. His labs are tricky though, especially from the mid-point on. Work with your fellow classmates on the labs and final project and you'll be good!"

Rank 2:

"This class was super cool, it's a shame it isn't taught every semester. We don't deserve Gondree. This is his wheelhouse. You can tell how much he loves the material and he makes it very easy to understand. The labs were both fun and fascinating. He's so helpful and easy to talk to. No other prof offers as many office hours as he does. Use them!"

Rank 3:

"Had him for a computer security class and also as my department advisor. Only had him during the online pandemic class but was great. He always took questions, listened to feedback and was willing to meet our needs. Some of the material was tough but he was willing to explain and work with you in office hours until you got it. Taking him again."

Why these chunks are relevant: All three results are Mark Gondree reviews tagged with course CS340 — the metadata filter ensures every retrieved chunk is on-target. Rank 1 and 2 specifically describe CS340's content (computer security, dense lectures, tricky labs, group project), directly matching the query. There are only 3 CS340-tagged reviews in the corpus, so the retrieval exhausted the filtered set. Rank 3's higher distance (0.7464) reflects a less query-specific review text, but it is still a valid CS340 review.

### Query 2: CS315 with Ali Kooshesh
Query: What do students say about CS315 with Ali Kooshesh?
Filters applied: professor=Ali Kooshesh, course=CS315

Rank	Distance	Source File	Professor	Course
1	0.3555	ali_kooshesh_62598.json	Ali Kooshesh	CS315
2	0.3651	ali_kooshesh_62598.json	Ali Kooshesh	CS315
3	0.4552	ali_kooshesh_62598.json	Ali Kooshesh	CS315
Rank 1:

"If CS315 at SSU is the Dark Souls of CS classes, then Kooshesh is From Software. He respects his students' intelligence enough to challenge them thoroughly but is still fair enough to offer help. Start on projects early, TAKE NOTES in class, like, hand written, and show up to every class early to prep for a possible pop-quiz. Kooshesh is the GOAT."

Rank 2:

"Dr. Kooshesh is very intelligent and humble, his lectures are very clear. You will be very busy with this class, this class will test your intellectual ability and your commitment to the major. You will learn a ton about CS and your ability to solve problems will be sharpened. Consider yourself lucky to have Dr. Kooshesh."

Rank 3:

"Dr. Kooshesh is very 'old school', which is something I really respect about him. Another way to describe him is 'tough but fair'. His expectations are clear and he emphasizes them throughout the course without fail. It's not an easy class but he is so wonderful when you need help. When he tells you not to procrastinate, listen!"

Why these chunks are relevant: This is the strongest retrieval result in the evaluation set. All top results come from ali_kooshesh_62598.json and are tagged CS315. The top distance score (0.3555) is the lowest across all three queries, indicating high semantic similarity between the question and the retrieved reviews. Rank 1 names CS315 explicitly and captures both the difficulty and the fairness that students describe. Ranks 2 and 3 reinforce the same themes — demanding workload, clear expectations, and strong teaching.

### Query 3: Tia Watts CS215 Complaints
Query: What complaints appear in reviews of Tia Watts's CS215 course?
Filters applied: professor=Tia Watts, course=CS215

Rank	Distance	Source File	Professor	Course
1	0.4823	tia_watts_62602.json	Tia Watts	CS215
2	0.5101	tia_watts_62602.json	Tia Watts	CS215
3	0.5155	tia_watts_62602.json	Tia Watts	CS215
Rank 1:

"I think Tia is great!!! If you are a student that is dumb and lazy she is not the teacher for you. However if you are smart and motivated she will rock you!!"

Rank 2:

"Compared to some of the other CS teachers, she's great...easy to follow, will use every second of the time she has with you (and some). When your in her classes it sucks, but if you do the work you'll have learned a lot when your done."

Rank 3:

"Sadly the worst CS class I've taken this far. She definitely knows her stuff but considering both the code in the lecture and the labs have typos and small errors within in them it is impossible to do anything but learn everything by yourself. As long as you do the labs and know what goes on in code for tests you'll pass but with no help from her."

Why these chunks are relevant: The metadata filter correctly constrains all results to Tia Watts CS215 reviews, so every result is from the right source. The distance scores (0.48–0.52) are higher than the other two queries, which is expected — complaint-framed questions are semantically farther from typical review text than professor+course phrasing. Rank 3 is the most directly relevant to the complaint query: it describes lab typos, the self-teaching burden, and lack of help — matching the expected answer in the evaluation plan. Ranks 1 and 2 are less complaint-specific but still accurately represent the range of student opinion about the course.

Note: The results shown above were collected after metadata filtering was implemented. Earlier versions of the retrieval pipeline used semantic similarity alone and occasionally returned reviews from the wrong professor when multiple professors used similar language.

## Stretch Feature: Metadata Filtering

The retrieval system was extended to support metadata filtering by professor name and course number. When a query references a known professor or course, retrieval is restricted to the matching subset of reviews before semantic ranking is applied. This improved precision for course-specific questions and reduced retrieval of reviews from unrelated professors.