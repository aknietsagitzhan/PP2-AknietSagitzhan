a = int(input()) 
if a <= 0:
    print("NO")
else:
    while a > 1 and a % 2 == 0:
        a //= 2

    if a == 1:
        print("YES")
    else: 
        print("NO")