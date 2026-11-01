import os
from google import genai
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

def _is_transient(e) -> bool:
    return getattr(e, "code", None) in (429, 500, 502, 503, 504)

def _should_retry(e) -> bool:
    # temporary API error ya LLM ka galat JSON -> retry. 404/401 jaise errors -> nahi
    return isinstance(e, ValidationError) or _is_transient(e)

_retry = retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(min=2, max=30),
    retry=retry_if_exception(_should_retry),
    reraise=True,
)

@_retry
def _call(model, prompt, config=None):
    return client.models.generate_content(model=model, contents=prompt, config=config)

def _generate(prompt, config=None):
    try:
        return _call(MODEL, prompt, config)
    except Exception as e:
        if _is_transient(e):                      # primary busy ho toh fallback model
            return _call(FALLBACK_MODEL, prompt, config)
        raise

def ask_text(prompt: str) -> str:
    return _generate(prompt).text

@_retry
def ask_json(prompt: str, schema):
    resp = _generate(prompt, {"response_mime_type": "application/json"})
    return schema.model_validate_json(resp.text)