import re
s = input()
n = re.compile(r"\b\w+\b")
w = n.findall(s)

print(len(w))