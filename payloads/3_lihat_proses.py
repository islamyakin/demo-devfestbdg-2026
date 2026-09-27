import os
for pid in sorted(p for p in os.listdir("/proc") if p.isdigit()):
    try:
        print(pid, open(f"/proc/{pid}/cmdline").read().replace("\0", " "))
    except OSError:
        pass
