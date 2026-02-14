def usual(num):
    for p in (2, 3, 5):
        while num % p == 0:
            num //= p
    return num == 1

n = int(input())
print("Yes" if usual(n) else "No")