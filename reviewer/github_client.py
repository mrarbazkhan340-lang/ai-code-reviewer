import os, requests
from dotenv import load_dotenv
load_dotenv()

HEADERS = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.v3.diff",   # raw diff maangta hai
}

def get_commit_diff(owner: str, repo: str, sha: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text