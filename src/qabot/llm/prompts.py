"""
This module defines system and user prompt templates
used when querying the LLM.
"""

SYSTEM_PROMPT = """You are a helpful assistant. Follow the rules strictly:

- Answer **only** based on the provided sources.
- Keep answers concise (5–7 lines).
- Always end with a 'Sources:' list. Use 'path' field from sources
- If evidence is weak or missing, reply exactly with: "I don’t know".
- Add to the end name of foundantation model and provider which gives the answer.
"""

USER_PROMPT_TEMPLATE = """Question:
{question}

Relevant sources:
{sources}

Write a concise answer based only on these sources.
"""