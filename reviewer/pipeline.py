import logging
from .llm import ask_text, ask_json
from .schemas import Review, Finding
from .chunking import make_chunks

log = logging.getLogger("reviewer")

RULES = """Line numbers sirf diff ke '@@ -a,b +c,d @@' header se nikalo (new file ki line).
Sirf wahi problems batao jo is diff mein dikh rahi hain. Agar pakka nahi ho toh mat batao.
Zyada findings se bachna: har finding sach honi chahiye. Kuch nahi mila toh empty list do."""

FORMAT = '''Sirf is exact JSON format mein jawab do. Har finding mein ye saari 6 keys zaroori hain:
{"findings":[{"file":"auth.py","line":50,"type":"security","severity":"high","message":"...","suggestion":"..."}]}
type sirf in mein se ek: security, error_handling, missing_test, bug, other.
severity sirf in mein se ek: low, medium, high.'''

def step1_understand(chunk: str) -> str:
    return ask_text(f"Is code diff mein kya badla aur kyun, 3-4 lines mein batao:\n\n{chunk}")

def step2_security(chunk: str, summary: str) -> list[Finding]:
    p = f"""Tum security reviewer ho. Summary: {summary}
Dhundo: SQL injection, hardcoded secrets, unsafe input, auth bypass.
{RULES}
{FORMAT}

DIFF:
{chunk}"""
    return ask_json(p, Review).findings

def step3_errors_tests(chunk: str, summary: str) -> list[Finding]:
    p = f"""Tum reviewer ho. Summary: {summary}
Dhundo: missing exception handling, unchecked None/edge cases, naye logic ka test missing.
type "error_handling" ya "missing_test" ya "bug" rakho.
{RULES}
{FORMAT}

DIFF:
{chunk}"""
    return ask_json(p, Review).findings

def step4_final(findings: list[Finding]) -> list[Finding]:
    seen, out = set(), []
    for f in sorted(findings, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.severity]):
        key = (f.file, f.line, f.type)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out

def review_diff(diff: str) -> list[Finding]:
    all_findings = []
    for i, chunk in enumerate(make_chunks(diff)):
        try:
            summary = step1_understand(chunk)
        except Exception as e:
            log.error("chunk %d step1 failed: %s", i, e)
            summary = ""
        for step in (step2_security, step3_errors_tests):
            try:
                all_findings += step(chunk, summary)
            except Exception as e:      # ek step fail ho toh baaki chalte rahein
                log.error("chunk %d %s failed: %s", i, step.__name__, e)
    return step4_final(all_findings)