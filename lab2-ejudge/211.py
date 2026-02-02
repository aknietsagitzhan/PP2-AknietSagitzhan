n, l, r = map(int, input().split())
a = list(map(int, input().split()))
a[l-1:r] = a[l-1:r][::-1]
print(*a)