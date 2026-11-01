import json, subprocess

REPO = r"..\flask"
PICK = [1, 3, 5, 7, 8, 12]

cands = json.load(open("eval/candidates.json", encoding="utf-8"))
cases = json.load(open("eval/cases.json", encoding="utf-8"))
have = {c["intro_sha"][:9] for c in cases}

def fix_diff(sha):
    r = subprocess.run(
        ["git", "-C", REPO, "show", "--format=", "-U2", sha, "--", "src/flask"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout[:2500]

for n in PICK:
    c = cands[n - 1]
    if c["intro_sha"][:9] in have:
        print("skip (already there):", n)
        continue
    cases.append({
        "owner": c["owner"], "repo": c["repo"], "intro_sha": c["intro_sha"],
        "file": c["file"], "bug_line": c["bug_line"],
        "case_type": "auto", "difficulty": "unknown",
        "bug_description": f"Fix commit {c['fixed_in']}: {c['fix_message']}",
        "fixed_in": c["fixed_in"],
        "fix_diff": fix_diff(c["fixed_in"]),
        "reviewer_result_v1": "not run yet",
    })
    print("added:", n, c["fix_message"][:50])

json.dump(cases, open("eval/cases.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("Total cases:", len(cases))