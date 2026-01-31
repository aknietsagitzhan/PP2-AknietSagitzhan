a = int(input())
n = list(map(int, input().split()))
mx = n[0]
indx = 0
for i in (n):
    if n[i] > mx:
        mx = n[i]
        indx = i
print(indx)