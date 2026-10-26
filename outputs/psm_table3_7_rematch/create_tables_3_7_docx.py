from pathlib import Path
import csv
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'PSM_no_caliper_Tables3_7_regression_results_revised.docx'

LABELS={
 'VD':'VD (H1)','c.VD#c.patentdummybyfiling':'VD × Prior Patent_VD (H2)',
 'c.VD#c.earlystage':'VD × Early Stage_VD (H3)',
 'patentdummybyfiling':'Prior Patent_VD','earlystage':'Early Stage_VD',
 'ln_MoneyRaised_VD':'Log(Total Funding Amt_VD)',
 'NumofFundingRounds_VD':'Num of Funding Rounds_VD','Foundingyear':'Founding Year',
 '_cons':'Constant','N':'Observations','r2':'R-squared','N_fail':'# of failures'
}
TITLES={
 3:'DV: Log(Granted Patent Applications) (3-year filing window)',
 4:'DV: Log(Normalized citations per patent) (3-year)',
 5:'DV: Log(Follow-on Equity Raised) (3-year)',
 6:'DV: Log(Annual Follow-on Equity Raised)',
 7:'Exit outcomes (Cox proportional-hazard models; log-hazard coefficients)'
}

def clean(s):
 s=(s or '').strip()
 if s.startswith('="') and s.endswith('"'): s=s[2:-1]
 return s.replace('""','"')
def read_csv(n):
 with open(ROOT/f'Table{n}.csv',encoding='utf-8-sig',newline='') as f:
  return [[clean(x) for x in r] for r in csv.reader(f) if r]
def shade(cell,fill):
 p=cell._tc.get_or_add_tcPr(); e=OxmlElement('w:shd'); e.set(qn('w:fill'),fill); p.append(e)
def borders(t):
 p=t._tbl.tblPr; b=OxmlElement('w:tblBorders')
 for x in ('top','left','bottom','right','insideH','insideV'):
  e=OxmlElement('w:'+x); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'D9D9D9'); b.append(e)
 p.append(b)
def setcell(c,text,bold=False,center=False,size=8):
 c.text=''; p=c.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
 p.paragraph_format.space_after=Pt(0); r=p.add_run(text); r.bold=bold; r.font.name='Times New Roman'; r.font.size=Pt(size)
 r._element.rPr.rFonts.set(qn('w:ascii'),'Times New Roman'); r._element.rPr.rFonts.set(qn('w:hAnsi'),'Times New Roman')
 c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
def humanize(rows,n):
 out=[]
 for r in rows:
  label=r[0]
  joined=' '.join(r)
  if label=='p-values in parentheses' or 'p<0.10' in joined or 'p<0.05' in joined or 'p<0.001' in joined: continue
  if label in LABELS: r[0]=LABELS[label]
  if n==6 and not label and len(out)==1: r[1:]=['t+1','t+2','t+3']
  out.append(r)
 return out
def add_table(doc,n):
 rows=humanize(read_csv(n),n)
 cols=max(len(r) for r in rows)
 p=doc.add_paragraph(); p.paragraph_format.keep_with_next=True
 rr=p.add_run(f'Table {n}. {TITLES[n]}'); rr.bold=True; rr.font.name='Times New Roman'; rr.font.size=Pt(10)
 t=doc.add_table(rows=0,cols=cols); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
 for i,r in enumerate(rows):
  cells=t.add_row().cells
  vals=r+['']*(cols-len(r))
  is_p=not vals[0] and any(v.startswith('(') for v in vals[1:])
  for j,v in enumerate(vals):
   setcell(cells[j],v,bold=(i==0 or vals[0] in ('Region FE','Industry FE','Founding year control','Observations','R-squared','# of failures')),center=(j>0),size=7.5 if cols>5 else 8)
   if i==0: shade(cells[j],'D9EAF7')
  if is_p:
   for c in cells:
    for run in c.paragraphs[0].runs: run.font.size=Pt(7)
 if cols==5:
  widths=[2.8,.85,.85,.85,.85]
 elif cols==4:
  widths=[3.2,1.05,1.05,1.05]
 else:
  widths=[1.7]+[.78]*(cols-1)
 for row in t.rows:
  for j,w in enumerate(widths): row.cells[j].width=Inches(w)
 borders(t)
 note=doc.add_paragraph()
 note.add_run('Significance levels: * ')
 note.add_run('p').italic=True
 note.add_run(' < .10, ** ')
 note.add_run('p').italic=True
 note.add_run(' < .05, *** ')
 note.add_run('p').italic=True
 note.add_run(' < .01.')
 note.paragraph_format.space_before=Pt(3); note.paragraph_format.space_after=Pt(0)
 for run in note.runs: run.font.name='Times New Roman'; run.font.size=Pt(8)

doc=Document(); s=doc.sections[0]; s.top_margin=Inches(.55); s.bottom_margin=Inches(.55); s.left_margin=Inches(.6); s.right_margin=Inches(.6)
normal=doc.styles['Normal']; normal.font.name='Times New Roman'; normal.font.size=Pt(9)
title=doc.add_paragraph(); title.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=title.add_run('Regression Tables 3 to 7 for the Caliper Free Matched Sample'); r.bold=True; r.font.name='Times New Roman'; r.font.size=Pt(16)
p=doc.add_paragraph('Matched sample: 1,410 VD-backed firms and 1,410 VC-only firms. Treated firms use the actual VD year; controls use founding year plus five. Outcomes are measured through the third post-reference year. Tables 3–6 use reghdfe with region and industry absorbed and robust standard errors; Foundingyear enters as a linear control, following the supplied specification.')
p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for idx,n in enumerate(range(3,8)):
 if idx: doc.add_page_break()
 add_table(doc,n)
doc.save(OUT)
print(OUT)
