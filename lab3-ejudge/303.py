to_digit = {
    "ZER": "0", "ONE": "1", "TWO": "2", "THR": "3", "FOU": "4",
    "FIV": "5", "SIX": "6", "SEV": "7", "EIG": "8", "NIN": "9"
}
to_triplet = {v: k for k, v in to_digit.items()}
def decode(s):
    """Convert triplet string to integer"""
    digits = []
    for i in range(0, len(s), 3):
        digits.append(to_digit[s[i:i+3]])
    return int("".join(digits))

def encode(num):
    """Convert integer to triplet string"""
    if num == 0:
        return "ZER"
    return "".join(to_triplet[d] for d in str(num))

expr = input().strip()

for op in ["+", "-", "*"]:
    if op in expr:
        left, right = expr.split(op)
        operator = op
        break

a = decode(left)
b = decode(right)

if operator == "+":
    result = a + b
elif operator == "-":
    result = a - b
else:
    result = a * b

print(encode(result))