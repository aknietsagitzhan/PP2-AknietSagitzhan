a = int(input())
def valid(a):
    ans = True
    for i in a:
        if i % 2 != 0:
            ans = False
            break
    if ans:
        print("Valid")
    else:
        print("Not valid")
valid(a)