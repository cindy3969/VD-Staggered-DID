from docx import Document
from pathlib import Path
import pandas as pd
p=Path(r'C:/Users/user/iCloudDrive/5학기/연구미팅/VD PPT/20260822 Table.docx')
d=Document(p)
for el in d.element.body:
 if el.tag.endswith('}p'):
  from docx.text.paragraph import Paragraph
  print(Paragraph(el,d).text)
 elif el.tag.endswith('}tbl'):
  from docx.table import Table
  for r in Table(el,d).rows: print(' | '.join(c.text for c in r.cells))
for p in Path('outputs').rglob('*.dta'):
 if any(s in p.name for s in ['csdid_rebuilt_patent_panel','csdid_all_published_applications_panel','firm_year_corrected','full7316_controls']):
  f=pd.read_stata(p,convert_categoricals=False);print('\nFILE',p,f.shape,list(f.columns))
