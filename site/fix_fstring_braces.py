import os

path = r'e:\Vector Field Theory\value-physics\site\build_value_physics_site.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 1591 <= i <= 1604:
        # Double the braces for f-string escaping
        l = line.replace('{', '{{').replace('}', '}}')
        new_lines.append(l)
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: Escaped lines 1592-1605 in build_value_physics_site.py")
