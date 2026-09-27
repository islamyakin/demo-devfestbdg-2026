import urllib.request
print("status example.com:", urllib.request.urlopen("https://example.com", timeout=5).status)
