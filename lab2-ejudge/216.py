n = int(input())
a = list(map(int, input().split()))
s = set()

for x in a:
    if x not in s:
        print("YES")
        s.add(x)
    else:
        print("NO")
