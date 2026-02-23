import json

def func(source, patch):
    for key, value in patch.items():
        if value is None:
            source.pop(key, None)
        elif key in source and isinstance(source[key], dict) and isinstance(value, dict):
            func(source[key], value)
        else:
            source[key] = value
    return source


source = json.loads(input())
patch = json.loads(input())

result = func(source, patch)

print(json.dumps(result, separators=(',', ':'), sort_keys=True))