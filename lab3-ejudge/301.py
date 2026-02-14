a = input().strip()
ans = True
for i in a:
    i = int(i)
    if i % 2 != 0:
        ans = False
        break
if ans:
    print("Valid")
else:
    print("Not valid")