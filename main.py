import functools, json, os, re, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = os.environ.get("MODE", "naive")  
DUMMY = "/app/data/customers.txt"
TIMEOUT = 10
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
SYSTEM = (
    "Kamu menulis kode Python 3 yang langsung dijalankan dengan python3 -c. "
    "Balas HANYA dengan kode, tanpa penjelasan dan tanpa markdown fence. "
    "Pakai standard library saja dan cetak hasilnya ke stdout."
)
FENCE = re.compile(r"^\s*```[\w+-]*\n(.*?)\n?```\s*$", re.S)


@functools.cache
def gemini():
    from google import genai
    return genai.Client()


def strip_fence(text):
    m = FENCE.match(text)
    return (m.group(1) if m else text).strip()


def generate(prompt):
    from google.genai import types
    r = gemini().models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.2),
    )
    code = strip_fence(r.text or "")
    print(json.dumps({"severity": "INFO", "message": "gemini code", "mode": MODE, "model": MODEL,
                      "prompt": prompt, "code": code}), flush=True)
    return code


def run(code):
    if MODE == "sandbox":
        cmd = ["/usr/local/gcp/bin/sandbox", "do", "--write", "--", "/usr/local/bin/python3", "-c", code]
    else:
        cmd = ["python3", "-c", code]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        return {"exit": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        return {"exit": None, "error": f"timeout {TIMEOUT}s"}


class H(BaseHTTPRequestHandler):
    def send(self, status, body):
        data = json.dumps(body, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/state":
            return self.send(404, {"error": "not found"})
        exists = os.path.exists(DUMMY)
        self.send(200, {
            "mode": MODE,
            "dummy_file_exists": exists,
            "dummy_file": open(DUMMY).read() if exists else None,
        })

    def do_POST(self):
        if self.path not in ("/execute", "/agent"):
            return self.send(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length", 0))
        if n > 64_000:
            return self.send(413, {"error": "body too large"})
        body = self.rfile.read(n).decode()
        if self.path == "/execute":
            return self.send(200, {"mode": MODE, **run(body)})
        try:
            prompt = json.loads(body)["prompt"]
        except (ValueError, KeyError, TypeError):
            return self.send(400, {"error": 'body harus {"prompt": "..."}'})
        try:
            code = generate(prompt)
        except Exception as e:
            return self.send(502, {"error": f"gemini: {e}"})
        self.send(200, {"mode": MODE, "model": MODEL, "prompt": prompt, "code": code, **run(code)})


ThreadingHTTPServer(("", int(os.environ.get("PORT", 8080))), H).serve_forever()
