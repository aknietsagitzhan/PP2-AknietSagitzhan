def func():
    a, b = 0, 1
    for i in range(0, n):
        yield a
        next = a + b
        a = b
        b = next


n = int(input())
s = True
for num in func():
    if not s:
        print(",", end="")
    print(num, end="")
    s = False