import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

candidates = [
    "gemini-flash-latest",        # alias, hamesha current flash par point karta hai
    "gemini-flash-lite-latest",   # alias, sasta/halka version
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]

for name in candidates:
    try:
        r = client.models.generate_content(model=name, contents="Sirf ek word mein jawab do: 2+2?")
        print("OK  ", name, "->", r.text.strip()[:30])
    except Exception as e:
        print("FAIL", name, "->", str(e)[:120].replace("\n", " "))