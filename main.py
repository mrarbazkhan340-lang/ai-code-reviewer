import sys, json, logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)

from reviewer.github_client import get_commit_diff
from reviewer.pipeline import review_diff

owner, repo, sha = sys.argv[1:4]
findings = review_diff(get_commit_diff(owner, repo, sha))
print(json.dumps([f.model_dump() for f in findings], indent=2))