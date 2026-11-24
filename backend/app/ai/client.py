import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_groq import ChatGroq
from app.core.config import settings

logger = logging.getLogger("pharma_rca.ai")

T = TypeVar("T", bound=BaseModel)


def is_groq_configured() -> bool:
    """Checks if a valid, non-placeholder Groq API key is present."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return False
    if "placeholder" in api_key.lower() or "your_groq" in api_key.lower():
        return False
    return api_key.startswith("gsk_") and len(api_key) > 10


def get_llm(temperature: float = 0.1) -> Optional[ChatGroq]:
    """Returns configured ChatGroq instance if key is valid, else None."""
    if not is_groq_configured():
        logger.info("Groq API key not configured or using placeholder; using rule-based GMP analyzer fallback.")
        return None

    try:
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_retries=2,
        )
    except Exception as exc:
        logger.warning(f"Failed to initialize ChatGroq: {exc}")
        return None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
def invoke_structured_output_with_retry(llm: ChatGroq, schema: Type[T], prompt: str) -> T:
    """Invokes LLM with structured output and automatic retry for rate limits."""
    structured_llm = llm.with_structured_output(schema)
    return structured_llm.invoke(prompt)
