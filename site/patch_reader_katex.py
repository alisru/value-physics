import os

path = r'e:\Vector Field Theory\value-physics\site\reader_generator.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

t1 = '  <style>\n{READER_CSS}'
r1 = '''  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous" onload="renderMathInPage()"></script>
  <style>
{READER_CSS}'''

t2 = '</body>\n</html>'
r2 = '''  <script>
function renderMathInPage(targetEl) {
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(targetEl || document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\\\(', right: '\\\\)', display: false},
        {left: '\\\\[', right: '\\\\]', display: true}
      ],
      throwOnError: false
    });
  }
}
window.renderMathInPage = renderMathInPage;
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => renderMathInPage(), 100);
});
  </script>
</body>
</html>'''

if t1 in text and t2 in text:
    text = text.replace(t1, r1, 1).replace(t2, r2, 1)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('SUCCESS: Updated reader_generator.py with KaTeX auto-render!')
else:
    print('Targets not found: t1=', t1 in text, 't2=', t2 in text)
