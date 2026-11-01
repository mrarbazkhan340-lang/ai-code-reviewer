# tests_manual.py
import sys, json, logging

SHA = "49943b5a94413a530761350f04e896f76e8d620e"      # test_github aur test_chunking ke liye
OWNER, REPO = "pallets", "flask"

def test_llm():
    from reviewer.llm import ask_text
    print(ask_text("Sirf ek word mein jawab do: 2+2?"))

def test_schema_json():
    from reviewer.llm import ask_json
    from reviewer.schemas import Review
    r = ask_json('Is exact JSON ko wapas do: {"findings":[{"file":"a.py","line":3,"type":"bug","severity":"low","message":"test","suggestion":"fix"}]}', Review)
    print(r)

def test_github():
    from reviewer.github_client import get_commit_diff
    d = get_commit_diff(OWNER, REPO, SHA)
    print(d[:600])
    print("LEN:", len(d))

def test_chunking():
    from reviewer.github_client import get_commit_diff
    from reviewer.chunking import make_chunks
    chunks = make_chunks(get_commit_diff(OWNER, REPO, SHA))
    print("chunks:", len(chunks), "sizes:", [len(c) for c in chunks])

FAKE_DIFF = '''diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -48,6 +48,10 @@ def login(user, pwd):
-    if user and pwd:
+    if user:
         pass
+    query = f"SELECT * FROM users WHERE name='{user}' AND pwd='{pwd}'"
+    row = db.execute(query).fetchone()
+    return row["id"]
'''

def test_pipeline_fake():
    logging.basicConfig(level=logging.INFO)
    from reviewer.pipeline import review_diff
    out = review_diff(FAKE_DIFF)
    print(json.dumps([f.model_dump() for f in out], indent=2))

if __name__ == "__main__":
    globals()[sys.argv[1]]()