import re
s = input()
dates = re.findall(r"\d{2}/\d{2}/\d{4}", s)
print(len(dates))