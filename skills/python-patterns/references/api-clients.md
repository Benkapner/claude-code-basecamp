# API Clients and Response Parsing

## Hard Limits

- **ALWAYS** set `timeout=30` on all requests — no request should hang indefinitely
- **Retry only transient failures** — 429, 500, 502, 503, 504, connection errors
- **NEVER retry permanent failures** — 400, 401, 403, 404, 422
- **NEVER log full response bodies** — log method, URL, status code, duration only
- **Validate response structure** before accessing fields

## LLM Response Parsing

LLM outputs often include markdown fences that break JSON parsing. Always clean before parsing:

```python
import json

def clean_llm_response(text):
    for prefix in ("```markdown", "```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text

def parse_llm_json(text):
    text = clean_llm_response(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logging.error(f"LLM returned invalid JSON: {text[:200]}")
        return None
```

## Anti-Patterns

| Anti-Pattern | Do This Instead |
|-------------|-----------------|
| No timeout on requests | Always `timeout=30` |
| Retrying 401/403 | Only retry transient errors |
| `verify=False` | Fix the cert or use proper CA bundle |
| Logging full responses | Log status code + item count only |
| String concatenation for URLs | Use `urllib.parse.urljoin` or params dict |
| Catching all exceptions | Catch specific: `requests.exceptions.*` |
