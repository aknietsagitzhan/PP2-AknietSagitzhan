p = int(input())
a = list(map(int, input().split()))
mx = a[0]
mn = a[0]
for i in a:
    if i > mx:
        mx = i
    if i < mn:
        mn = i

for i in a:
    if i == mx:
        print(mn, end=" ")
    else: 
        print(i, end=" ")