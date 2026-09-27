import json, os, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = os.environ.get("MODE", "naive")  
DUMMY = "/app/data/customers.txt"
TIMEOUT = 10


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
        if self.path != "/execute":
            return self.send(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length", 0))
        if n > 64_000:
            return self.send(413, {"error": "code too large"})
        code = self.rfile.read(n).decode()
        self.send(200, {"mode": MODE, **run(code)})


ThreadingHTTPServer(("", int(os.environ.get("PORT", 8080))), H).serve_forever()
