import json, sys, time, logging

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

from reviewer.github_client import get_commit_diff
from reviewer.pipeline import review_diff

TOL = 5
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"

cases = json.load(open("eval/cases.json", encoding="utf-8"))
results = []

for i, c in enumerate(cases, 1):
    print(f"\n=== Case {i}: {c['file']} (bug line {c['bug_line']}) ===")
    print("Bug:", c["bug_description"])
    try:
        findings = review_diff(get_commit_diff(c["owner"], c["repo"], c["intro_sha"]))
    except Exception as e:
        print("FAILED:", e)
        results.append({"case": i, "error": str(e)})
        continue

    name = c["file"].split("/")[-1]
    near = [f for f in findings
            if f.file.split("/")[-1] == name and abs(f.line - c["bug_line"]) <= TOL]
    others = [f for f in findings if f not in near]

    print(f"\nBug ke paas ({len(near)}):")
    for f in near:
        print(f"  line {f.line} [{f.type}/{f.severity}] {f.message}")
    print(f"Baaki findings ({len(others)}):")
    for f in others:
        print(f"  {f.file}:{f.line} [{f.type}/{f.severity}] {f.message}")

    results.append({
        "case": i,
        "near_bug": [f.model_dump() for f in near],
        "others": [f.model_dump() for f in others],
        "verdict": "JUDGE_MANUALLY",
    })
    time.sleep(3)

out = f"eval/results_{VERSION}.json"
json.dump(results, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"\nSaved: {out}")