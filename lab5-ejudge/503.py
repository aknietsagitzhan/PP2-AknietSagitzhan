import re
s = input()
p = input()
cnt = re.findall(p, s)
print(len(cnt))