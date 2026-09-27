import json, urllib.request
req = urllib.request.Request(
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
    headers={"Metadata-Flavor": "Google"})
with urllib.request.urlopen(req, timeout=5) as r:
    tok = json.load(r)["access_token"]
    print("status:", r.status, "| panjang token:", len(tok))
