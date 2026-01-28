a = int(input())
numbers = input().split()
total = 0
for i in range(a):
    total += int(numbers[i])
print(total)