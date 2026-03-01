import re
s = input()
pattern = re.compile(r"^\d+$")
if pattern.search(s):
    print("Match")
else:
    print("No match")