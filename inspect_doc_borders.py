from zipfile import ZipFile
from lxml import etree as E
ps=[r'C:/Users/user/iCloudDrive/5학기/연구미팅/VD PPT/VD Table 20260928.docx',r'C:/Users/user/Documents/VD/outputs/vd_intensity/VD Table_20261019.docx']
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for p in ps:
 with ZipFile(p) as z:
  e=E.fromstring(z.read('word/document.xml'));print(p)
  for tag in ['tblBorders','tcBorders','pBdr','u','strike']:
   a=e.findall('.//w:'+tag,ns);print(tag,len(a),[E.tostring(v).decode().split('>')[0][-160:] for v in a[:2]])
with ZipFile(ps[0]) as a,ZipFile(ps[1]) as b:
 print('changed parts',[n for n in a.namelist() if n not in b.namelist() or a.read(n)!=b.read(n)])
