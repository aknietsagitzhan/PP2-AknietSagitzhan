def func():
    for i in range(0, n + 1, 2):
        yield i
n = int(input())

a = True
for num in func():
    if not a:
        print(",", end="")
    print(num, end="")
    a = False