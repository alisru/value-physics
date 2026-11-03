import os, re

path = r'e:\Vector Field Theory\value-physics\site\reader_generator.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# In parse_docx_to_html, right after runs_html.append(esc):
# we want to clean any LaTeX math where runs broke up LaTeX tags, e.g. $|\\text{Good}<em>...</em>\\rangle$
old_block = """            p_text = ''.join(runs_html).strip()
            if not p_text:
                continue"""

new_block = """            p_text = ''.join(runs_html).strip()
            if not p_text:
                continue
            # Strip formatting HTML tags embedded within LaTeX math delimiters so KaTeX parses them cleanly
            def _clean_math_delims(m):
                return re.sub(r'</?(?:strong|em|b|i|span)[^>]*>', '', m.group(0))
            p_text = re.sub(r'(\\$\\$[^\\$]+\\$\\$|\\$[^\\$\\n]+\\$|\\\\\\[.+?\\\\\\]|\\\\\\(.+?\\\\\\))', _clean_math_delims, p_text)"""

text_norm = text.replace('\r\n', '\n')
old_norm = old_block.replace('\r\n', '\n')

if old_norm in text_norm:
    text_norm = text_norm.replace(old_norm, new_block.replace('\r\n', '\n'), 1)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text_norm)
    print("SUCCESS: Added math delimiter tag-cleaning to reader_generator.py")
else:
    print("WARNING: Target block not found in reader_generator.py")
