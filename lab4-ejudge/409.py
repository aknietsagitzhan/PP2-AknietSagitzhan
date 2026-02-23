def func(n):
    for i in range(n + 1):
        yield 2 ** i

n = int(input())
for a in func(n):
    print(a, end=" ")