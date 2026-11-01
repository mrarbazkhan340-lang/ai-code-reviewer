import re

MAX_CHARS = 12000   # ~3000 tokens, safe limit

def split_by_file(diff: str) -> list[str]:
    parts = re.split(r"(?=^diff --git )", diff, flags=re.M)
    return [p for p in parts if p.strip()]

def split_big_file(file_diff: str) -> list[str]:
    if len(file_diff) <= MAX_CHARS:
        return [file_diff]
    header, *hunks = re.split(r"(?=^@@ )", file_diff, flags=re.M)
    chunks, cur = [], header
    for h in hunks:
        if len(cur) + len(h) > MAX_CHARS and cur != header:
            chunks.append(cur)
            cur = header          # har chunk mein file ka header rakho
        cur += h
    chunks.append(cur)
    return chunks

def make_chunks(diff: str) -> list[str]:
    out = []
    for f in split_by_file(diff):
        out.extend(split_big_file(f))
    return out