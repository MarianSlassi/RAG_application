"""
This module defines system and user prompt templates
used when querying the LLM.
"""

SYSTEM_PROMPT = """You are a helpful assistant. Follow the rules strictly:

- Answer **only** based on the provided sources.
- Keep answers concise (5–7 lines).
- Always end with a 'Sources:' list. Where sources are {document_titles}
- If evidence is weak or missing, reply exactly with: "I don’t know".
"""

USER_PROMPT_TEMPLATE = """Question:
{question}

Relevant sources:
{sources}

Write a concise answer based only on these sources.
"""