n = int(input())
a = list(map(int, input().split()))
v = {}
for x in a:
    v[x] = v.get(x, 0) + 1
mx = max(v.values())
output = min(x for x, c in v.items() if c == mx)
print(output)