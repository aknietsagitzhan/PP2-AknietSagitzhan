a = int(input())
numbers = list(map(int , input().split()))
total = 0
for i in numbers:
    if i > 0:
        total += 1
print(total)