def sqrt(n):
    total = 0
    for i in n:
        total += i*i
    return total
a = int(input())
n = list(map(int, input().split()))
r = sqrt(n)
print(r)