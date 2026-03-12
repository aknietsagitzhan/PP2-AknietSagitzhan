n = int(input())
a = list(map(int, input().split()))
if all(x >= 0 for x in a):
    print("Yes")
else:
    print("No")