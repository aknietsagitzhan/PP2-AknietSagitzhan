def usual(num):
    for i in (2, 3, 5):
        while num % i == 0:
            num //= i
    return num == 1

n = int(input())
print("Yes" if usual(n) else "No")