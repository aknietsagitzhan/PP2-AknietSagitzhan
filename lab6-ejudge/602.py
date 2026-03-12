def f(n):
    return n % 2 == 0
a = int(input())
n = list(map(int, input().split()))
r = list(filter(f, n))
print(len(r))