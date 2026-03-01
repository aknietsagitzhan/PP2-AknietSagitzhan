import re
s = input()
match = re.search(r"Name:\s*(.+),\s*Age:\s*(\d+)", s)
if match:
    name = match.group(1)
    age = match.group(2)
    print(name, age)