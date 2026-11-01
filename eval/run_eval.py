import json, sys, time, logging

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from reviewer.github_client import get_commit_diff
from reviewer.pipeline import review_diff

TOL = 5
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"

class ErrorCounter(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.count = 0
    def emit(self, record):
        self.count += 1

counter = ErrorCounter()
logging.getLogger("reviewer").addHandler(counter)

report = []
def out(text=""):
    print(text, flush=True)
    report.append(text)

cases = json.load(open("eval/cases.json", encoding="utf-8"))
results = []

for i, c in enumerate(cases, 1):
    out(f"\n=== Case {i}/{len(cases)}: {c['file']} (bug line {c['bug_line']}) ===")
    out("Bug: " + c["bug_description"])
    if c.get("fix_diff"):
        out("--- Asli fix ka diff (reference) ---")
        out(c["fix_diff"][:1200])
        out("--- end fix diff ---")

    counter.count = 0
    try:
        findings = review_diff(get_commit_diff(c["owner"], c["repo"], c["intro_sha"]))
    except Exception as e:
        out(f"FAILED: {e}")
        results.append({"case": i, "error": str(e)})
        continue

    if counter.count:
        out(f"WARNING: {counter.count} step(s) fail hue, is case ka result bharosemand nahi hai.")

    name = c["file"].split("/")[-1]
    near = [f for f in findings
            if f.file.split("/")[-1] == name and abs(f.line - c["bug_line"]) <= TOL]
    others = [f for f in findings if f not in near]

    out(f"\nBug ke paas ({len(near)}):")
    for f in near:
        out(f"  line {f.line} [{f.type}/{f.severity}] {f.message}")
    out(f"Baaki findings ({len(others)}):")
    for f in others:
        out(f"  {f.file}:{f.line} [{f.type}/{f.severity}] {f.message}")

    results.append({
        "case": i,
        "failed_steps": counter.count,
        "near_bug": [f.model_dump() for f in near],
        "others": [f.model_dump() for f in others],
        "verdict": "JUDGE_MANUALLY",
    })
    time.sleep(3)

json.dump(results, open(f"eval/results_{VERSION}.json", "w", encoding="utf-8"),
        indent=2, ensure_ascii=False)
open(f"eval/report_{VERSION}.txt", "w", encoding="utf-8").write("\n".join(report))
out(f"\nSaved: eval/results_{VERSION}.json aur eval/report_{VERSION}.txt")