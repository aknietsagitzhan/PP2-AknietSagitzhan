import re
s = input()
p = input()
n = re.escape(p)
m = re.findall(n, s)
print(len(m))