import re
s = input()
d = re.findall(r"\d", s)
if d:
    print(" ".join(d))
else:
    print()