import re
s = input()
d = input()
parts = re.split(d, s)
print(",".join(parts))