def func(lst, k):
    for i in range(k):
        for a in lst:
            yield a

lst = input().split()
k = int(input())
for s in func(lst, k):
    print(s, end=" ")