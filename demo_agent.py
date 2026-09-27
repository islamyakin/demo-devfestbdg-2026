import json, shutil, subprocess, sys, textwrap, urllib.request
from concurrent.futures import ThreadPoolExecutor


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()


def call(mode, prompt, token):
    url = sh("gcloud", "run", "services", "describe", f"code-runner-{mode}",
             "--region", "asia-southeast1", "--format=value(status.url)")
    req = urllib.request.Request(url + "/agent", json.dumps({"prompt": prompt}).encode(),
                                 {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:500]}"}


def render(d, width):
    lines = []
    for title, text in (("KODE GEMINI", d.get("code")), ("STDOUT", d.get("stdout")),
                        ("STDERR", (d.get("stderr") or "")[-800:]), ("ERROR", d.get("error"))):
        if not text:
            continue
        lines += [f"── {title} ".ljust(width, "─")]
        for raw in text.rstrip().splitlines():
            lines += textwrap.wrap(raw, width, replace_whitespace=False, drop_whitespace=False) or [""]
    if "exit" in d:
        lines += [f"exit: {d['exit']}"]
    return lines


prompt = " ".join(sys.argv[1:]) or sys.exit(__doc__)
token = sh("gcloud", "auth", "print-identity-token")
with ThreadPoolExecutor(2) as ex:
    naive, sandbox = ex.map(lambda m: call(m, prompt, token), ("naive", "sandbox"))

w = (shutil.get_terminal_size().columns - 3) // 2
left, right = render(naive, w), render(sandbox, w)
print(f"PROMPT: {prompt}\n")
print("NAIVE (container utama)".ljust(w) + " │ " + "SANDBOX")
print("═" * w + "═╪═" + "═" * w)
for i in range(max(len(left), len(right))):
    l = left[i] if i < len(left) else ""
    r = right[i] if i < len(right) else ""
    print(l.ljust(w) + " │ " + r)
