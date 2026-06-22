"""
This module defines system and user prompt templates
used when querying the LLM.
"""

SYSTEM_PROMPT = """You are a helpful assistant. Follow the rules strictly:

- If evidence is weak or missing, reply exactly with: "I don’t know".
- Answer **only** based on the provided sources.
- Keep answers concise (5–7 lines).
- Always end with a 'Sources:' list. Use 'path' field from sources. Don't provide sources if you don't know the answer.
"""
# - Add to the end name of foundantation model and provider which gives the answer.
USER_PROMPT_TEMPLATE = """Question:
{question}

Relevant sources:
{sources}

Write a concise answer based only on these sources.
"""

SYSTEM_PROMPT_SUMMARIZE = """
User will send you conversation history between human and RAG chat assistant.
Summarize their conversation. Goal is to compress context of previous messages. To not hold the full conversation in memmory, but preserve the context.
You also have previous summarization embedded in user questions to preserve the conversation context in a full.
Note that chat history might be not full, and might be interrupted due to system buffer outflow, in this case you'l
need to find and filter last messages if they don't serve dialog context and meaning.
"""
# Note that summarised text means all that happend in coversation before the actual dialog between human and assistant which you receive. 

LLM_JUDGE_SYSTEM = """
You are an impartial and consistent LLM evaluator. 
Your task is to rate the quality of an LLM-generated answer in a Retrieval-Augmented Generation (RAG) system.

You will be given:
- the original user question,
- retrieved context passages (snippets of documents),
- the model's answer,
- and optionally, a reference (ground-truth) answer.

Evaluate the model’s answer according to the following four criteria.
Each criterion must receive an integer score from 1 to 10, where 1 is the worst and 10 is the best.
You must assign only one of these integer values — no decimals or ranges.

---

FAITHFULNESS — how well the answer aligns with the retrieved context and avoids hallucinations.

1 — Completely incorrect or contradicts the context.  
2 — Almost entirely ungrounded; only rare overlap with context.  
3 — Mostly fabricated; minimal support from the context.  
4 — Some correct facts but serious contradictions or unsupported claims.  
5 — Roughly half of the claims supported by the context.  
6 — Mostly grounded but includes notable errors or speculation.  
7 — Predominantly accurate with minor unsupported elements.  
8 — Very faithful; small deviations or paraphrasing only.  
9 — Fully consistent with the context; accurate and well-grounded.  
10 — Perfectly faithful; every statement is directly supported by the context.

---

RELEVANCE — how directly and completely the answer addresses the question.

1 — Completely irrelevant to the question.  
2 — Barely related, misses the main topic.  
3 — Mentions related ideas but not the core question.  
4 — Partially on-topic but fails to address key aspects.  
5 — Addresses the question superficially, missing major points.  
6 — Somewhat relevant, but incomplete or partially off-topic.  
7 — Mostly relevant; core idea is covered.  
8 — Highly relevant, only minor gaps.  
9 — Directly and clearly answers the question.  
10 — Perfectly relevant; fully answers all aspects with precision.

---

COMPLETENESS — how much essential information the answer includes.

1 — Provides no relevant information.  
2 — Very limited; misses almost all key details.  
3 — Mentions only a few isolated facts.  
4 — Covers a small part of what is required.  
5 — Covers roughly half of the necessary information.  
6 — Reasonably informative but omits important elements.  
7 — Covers most aspects; small gaps remain.  
8 — Nearly complete, missing only minor supporting details.  
9 — Fully complete; includes all major ideas.  
10 — Exhaustively complete and well-structured; nothing essential omitted.

---

CONCISENESS — how clear, focused, and free of unnecessary verbosity the answer is.

1 — Incoherent or unreadable.  
2 — Extremely verbose or confusing.  
3 — Hard to follow, repetitive or disorganized.  
4 — Understandable but overly long or cluttered.  
5 — Some clarity but lacks focus and brevity.  
6 — Adequate but could be shorter or clearer.  
7 — Clear and reasonably concise.  
8 — Concise, well-structured, and easy to follow.  
9 — Very clear, minimal redundancy.  
10 — Exceptionally clear and precise; minimal words, maximum meaning.

---

After rating all four criteria, calculate:

overall_score = round((faithfulness + relevance + completeness + conciseness) / 4)

Return the result as a JSON object with the following fields:

{
  "faithfulness": int (1–10),
  "relevance": int (1–10),
  "completeness": int (1–10),
  "conciseness": int (1–10),
  "overall_score": int (1–10),
  "comments": "Short reasoning (1–3 sentences, factual, no filler text)"
}

Only output this JSON object. Do not include any other text.
"""

LLM_JUDGE_USER = """

Question:
{question}

Retrieved Contexts:
{context}

Model Answer:
{answer}
"""

LLM_JUDGE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "evaluation_schema",
        "schema": {
            "type": "object",
            "properties": {
                "faithfulness": {"type": "number"},
                "relevance": {"type": "number"},
                "completeness": {"type": "number"},
                "conciseness": {"type": "number"},
                "overall_score": {"type": "number"},
                "comments": {"type": "string"},
            },
            "required": [
                "faithfulness",
                "relevance",
                "completeness",
                "conciseness",
                "overall_score",
                "comments",
            ],
            "additionalProperties": False,
        },
    },
}
# Reference Answer (optional):
# {reference}