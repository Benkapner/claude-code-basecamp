# Credential Management

## Loading Pattern

```python
from pathlib import Path
from dotenv import load_dotenv

# Load from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# No default for secrets (fail if missing)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not set in .env file")
    sys.exit(1)

# Optional values can have defaults
model_name = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
```

## Hard Limits

- **NEVER** use real values as defaults: `os.getenv("KEY", "AIza...")` exposes the key
- **ALWAYS** create `.env.example` with placeholders
- **ALWAYS** add `.env` to `.gitignore`
- **Load early** — `load_dotenv()` at entry points, not deep in utility code
- **Fail fast** — exit immediately if required secrets are missing
