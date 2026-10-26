from docx import Document
from pathlib import Path
import pandas as pd
p=Path(r'C:/Users/user/iCloudDrive/5학기/연구미팅/VD PPT/VD Table 20260928.docx')
d=Document(p)
out=[]
for el in d.element.body:
 if el.tag.endswith('}p'):
  from docx.text.paragraph import Paragraph
  out.append(Paragraph(el,d).text)
 elif el.tag.endswith('}tbl'):
  from docx.table import Table
  out.extend(' | '.join(c.text for c in r.cells) for r in Table(el,d).rows)
Path('table_intensity_extract.txt').write_text('\n'.join(out),encoding='utf8')
f=pd.read_stata('outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta',convert_categoricals=False)
print(f.shape); print(f.dtypes.to_string()); print(f.head(2).to_string())
