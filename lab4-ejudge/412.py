import sys
import json

a = json.loads(sys.stdin.readline())
b = json.loads(sys.stdin.readline())

m = object()
d = []

def to_json(v):
    return json.dumps(v, separators=(',', ':'))

def dfs(path, x, y):
    if isinstance(x, dict) and isinstance(y, dict):
        keys = sorted(set(x.keys()) | set(y.keys()))
        for k in keys:
            nx = x.get(k, m)
            ny = y.get(k, m)
            new_path = f"{path}.{k}" if path else k
            dfs(new_path, nx, ny)
        return

    if x is m:
        d.append(f"{path} : <missing> -> {to_json(y)}")
        return
    if y is m:
        d.append(f"{path} : {to_json(x)} -> <missing>")
        return

    if x != y:
        d.append(f"{path} : {to_json(x)} -> {to_json(y)}")

dfs("", a, b)

if d:
    print("\n".join(sorted(d)))
else:
    print("No differences")