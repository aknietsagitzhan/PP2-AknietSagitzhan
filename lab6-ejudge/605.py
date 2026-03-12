n = input().lower()
if any(v in "aeiou" for v in n):
    print("Yes")
else: 
    print("No")