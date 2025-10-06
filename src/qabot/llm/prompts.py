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
