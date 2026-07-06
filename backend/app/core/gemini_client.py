from functools import lru_cache

from google import genai
from google.genai import types

from app.core.config import get_settings

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768   # truncated via output_dimensionality, matches schema.sql `vector(768)`
GENERATION_MODEL = "gemini-2.5-flash"

_TASK_TYPE_MAP = {
    "retrieval_document": "RETRIEVAL_DOCUMENT",
    "retrieval_query": "RETRIEVAL_QUERY",
}


@lru_cache
def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    """Embeds `text` into a 768-dim vector using Gemini.
    task_type: "retrieval_document" for courses being indexed,
               "retrieval_query" for the skill-gap search text."""
    client = _get_client()
    result = await client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=_TASK_TYPE_MAP.get(task_type, "RETRIEVAL_DOCUMENT"),
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    return result.embeddings[0].values


async def generate_text(prompt: str) -> str:
    """Calls Gemini's generative model for free-form text (e.g. a short
    explanation of why certain courses were recommended)."""
    client = _get_client()
    response = await client.aio.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )
    return response.text
