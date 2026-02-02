a=int(input())
n=list(map(int, input().split()))

v = {}
for x in n:
    v[x] = v.get(x,0) + 1
mx = max(v, key=v.get)
if v[mx] == 1:
    print(min(n))
else:
    print(mx)