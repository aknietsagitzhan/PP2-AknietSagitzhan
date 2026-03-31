import re
s = input()

if re.search(r'^[A-Za-z].*\d$', s):
    print("Yes")
else:
    print("No")