from zipfile import ZipFile
from pathlib import Path
from lxml import etree as E
import re,copy,shutil
src=Path(r'C:/Users/user/iCloudDrive/5학기/연구미팅/VD PPT/VD Table 20260928.docx')
out=Path(r'C:/Users/user/Documents/VD/outputs/vd_intensity/VD Table_20261019.docx')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+ns['w']+'}'
def tables(root):
 found={};active=None
 for el in root.find('w:body',ns):
  if el.tag==W+'p':
   text=''.join(el.itertext())
   m=re.match(r'Table 3-([1-8])\.',text)
   if m:active=int(m[1])
  elif el.tag==W+'tbl' and active:
   found[active]=el;active=None
 return found
with ZipFile(src) as z: original=z.read('word/document.xml')
with ZipFile(out) as z: updated=E.fromstring(z.read('word/document.xml'))
root=E.fromstring(original);before=copy.deepcopy(root)
a=tables(root);b=tables(updated);assert len(a)==len(b)==8
count=0
for n in a:
 for row in list(range(1,21))+[24,25,26]:
  for col in range(1,5):
   cell=a[n].findall('w:tr',ns)[row].findall('w:tc',ns)[col]
   other=b[n].findall('w:tr',ns)[row].findall('w:tc',ns)[col]
   text=''.join(other.xpath('.//w:t/text()',namespaces=ns))
   ts=cell.findall('.//w:t',ns)
   if ts:
    ts[0].text=text
    for t in ts[1:]:t.text=''
   elif text:
    p=cell.find('w:p',ns);r=p.find('w:r',ns)
    if r is None:r=E.SubElement(p,W+'r')
    E.SubElement(r,W+'t').text=text
   count+=1
# Every original formatting property must remain structurally identical.
for tag in ['tblPr','tblGrid','trPr','tcPr','pPr','rPr','sectPr']:
 assert [E.tostring(x) for x in before.findall('.//w:'+tag,ns)]==[E.tostring(x) for x in root.findall('.//w:'+tag,ns)],tag
backup=out.with_name('VD Table_20261019_before_format_restore.docx')
shutil.copy2(out,backup)
tmp=out.with_suffix('.tmp.docx')
with ZipFile(src) as zi, ZipFile(tmp,'w') as zo:
 for info in zi.infolist():
  data=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else zi.read(info.filename)
  zo.writestr(info,data)
with ZipFile(src) as zi,ZipFile(tmp) as zo:
 assert all(zi.read(n)==zo.read(n) for n in zi.namelist() if n!='word/document.xml')
tmp.replace(out)
print('Replaced existing file. Original formatting properties identical; every package part except document text XML byte-identical. Cells:',count)
