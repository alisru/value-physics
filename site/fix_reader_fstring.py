import os

path = r'e:\Vector Field Theory\value-physics\site\reader_generator.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 960 <= i <= 980:
        # Double single braces for f-string escaping
        l = line
        # If line contains single { not already double
        if '{' in l and '{{' not in l:
            l = l.replace('{', '{{')
        if '}' in l and '}}' not in l:
            l = l.replace('}', '}}')
        new_lines.append(l)
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: Escaped f-string braces in reader_generator.py")
