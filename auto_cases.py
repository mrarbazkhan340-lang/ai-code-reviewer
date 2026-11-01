import subprocess, json, re, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else r"..\flask"
SKIP = re.compile(r"typo|typing|type hint|mypy|pyright|docs?\b|docstring|refactor|simplif|move|release|bump|annotation|format|lint", re.I)

def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.stdout

def num(pattern, text):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else 0

def size(sha):
    out = git("show", "--shortstat", "--format=", sha)
    return num(r"(\d+) files? changed", out), num(r"(\d+) insertions?", out) + num(r"(\d+) deletions?", out)

def deleted_hunks(sha):
    out = git("show", "--format=", "-U0", sha, "--", "src/flask")
    path, hunks = None, []
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+", line)
        if m and path and path.endswith(".py"):
            cnt = int(m.group(2)) if m.group(2) is not None else 1
            if cnt > 0:
                hunks.append((path, int(m.group(1)), cnt))
    return hunks

def blame_origin(sha, path, start):
    out = git("blame", "--porcelain", "-L", f"{start},{start}", f"{sha}~1", "--", path)
    lines = out.splitlines()
    if not lines:
        return None
    h = lines[0].split()
    fname = next((l[9:] for l in lines if l.startswith("filename ")), path)
    return h[0], int(h[1]), fname

try:
    done = {c["intro_sha"] for c in json.load(open("eval/cases.json", encoding="utf-8"))}
except Exception:
    done = set()

rows = git("log", "--no-merges", "-i", "-E",
           "--grep=fix|bug|crash|regression|wrong|incorrect|broken|restore|ensure",
           "--format=%H|%s", "-n", "400", "--", "src/flask").splitlines()

cands, seen = [], set()
for row in rows:
    sha, msg = row.split("|", 1)
    if SKIP.search(msg):
        continue
    hunks = deleted_hunks(sha)
    if not hunks or len(hunks) > 2 or hunks[0][2] > 6:
        continue
    path, start, _ = hunks[0]
    b = blame_origin(sha, path, start)
    if not b:
        continue
    intro, orig, fname = b
    if intro in seen or intro in done:
        continue
    files, lines_changed = size(intro)
    imsg = git("log", "-1", "--format=%s", intro).strip()
    if files > 10 or lines_changed > 300 or SKIP.search(imsg):
        continue
    seen.add(intro)
    cands.append({
        "owner": "pallets", "repo": "flask", "intro_sha": intro,
        "file": fname, "bug_line": orig, "fixed_in": sha[:8],
        "fix_message": msg, "intro_message": imsg,
        "intro_size": f"{files} files, {lines_changed} lines",
    })
    print(f"{len(cands):2}. fix {sha[:8]} '{msg[:45]}'\n"
        f"    bug aaya: {intro[:9]} '{imsg[:45]}' | {fname}:{orig} | {files} files, {lines_changed} lines")
    if len(cands) >= 25:
        break

json.dump(cands, open("eval/candidates.json", "w", encoding="utf-8"), indent=2)
print(f"\nSaved {len(cands)} candidates -> eval/candidates.json")