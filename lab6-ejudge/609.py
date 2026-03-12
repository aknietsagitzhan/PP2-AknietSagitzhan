n = int(input())
keys = input().split()
values = input().split()
d = dict(zip(keys, values))
q = input()
if q in d:
    print(d[q])
else: 
    print("Not found")