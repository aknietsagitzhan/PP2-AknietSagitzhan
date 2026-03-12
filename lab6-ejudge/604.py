n = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))
r = 0
for a, b in zip(A, B):
    r += a * b
print(r)