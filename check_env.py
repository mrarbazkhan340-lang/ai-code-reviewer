import os
from dotenv import load_dotenv
load_dotenv()
for k in ("GITHUB_TOKEN", "GEMINI_API_KEY"):
    v = os.getenv(k)
    print(k, "OK" if v else "MISSING", f"(len={len(v)})" if v else "")