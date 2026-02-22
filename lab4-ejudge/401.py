def func():
    for i in range(1, n +1):
        yield i * i
n = int(input())
for sq in func():
    print(sq)