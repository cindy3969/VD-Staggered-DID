from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
p=r'C:/Users/user/iCloudDrive/5학기/연구미팅/VD PPT/VD Table 20260928.docx'
d=Document(p);active=''
for el in d.element.body:
 if el.tag.endswith('}p'):
  t=Paragraph(el,d).text
  if t.startswith('Table'):active=t
 elif el.tag.endswith('}tbl') and active.startswith('Table 3-'):
  print(active)
  for j,r in enumerate(Table(el,d).rows):print(j,repr(r.cells[0].text),len(r.cells))
  active=''
