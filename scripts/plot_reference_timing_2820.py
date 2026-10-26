from pathlib import Path
import sys, json
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'.artifact_work/plot_packages'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from collections import Counter
OUT = ROOT/'outputs/reference_timing_audit_2820'
rows = json.loads((OUT/'firm_timing.json').read_text())
groups = {g:[r for r in rows if r['VD']==g] for g in [0,1]}
font_manager.findfont('Times New Roman', fallback_to_default=False)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
fig, axes = plt.subplots(1,3,figsize=(15,4.8))
colors = {1:'#24608C',0:'#D58A3A'}
for ax, col, title, xlabel in zip(axes,['VDyear','reference_age','reference_since_first_vc'],['A. Calendar year','B. Years since founding','C. Years since first VC'],['Reference year (First VD year)','Reference year (First VD year) − founding year','Reference year (First VD year) − first VC year']):
    lo=min(r[col] for r in rows); hi=max(r[col] for r in rows)
    xs=list(range(int(lo),int(hi)+1))
    if col=='reference_age':
        counts=Counter(r[col] for r in groups[1])
        ax.bar(xs,[100*counts[x]/1410 for x in xs],width=.75,color=colors[1],label='Treated')
        ax.axvline(5,color=colors[0],linestyle='--',linewidth=2,label='Controls: all at year 5')
        ax.set_ylim(0,16)
    else:
        for g, shift, label in [(1,-.21,'Treated'),(0,.21,'Controls')]:
            counts=Counter(r[col] for r in groups[g])
            ax.bar([x+shift for x in xs],[100*counts[x]/1410 for x in xs],width=.4,color=colors[g],label=label)
        if col=='reference_since_first_vc': ax.axvline(-.5,color='#999999',linewidth=.8,linestyle=':')
    ax.set_title(title,loc='center',fontweight='bold',pad=12)
    ax.set_xlabel(xlabel,labelpad=10)
    ax.set_ylabel('Number of firms within group (%)')
    ax.set_xticks(xs[::2] if len(xs)>15 else xs)
    if col=='VDyear': ax.tick_params(axis='x',rotation=60)
    ax.set_axisbelow(True); ax.grid(axis='y',alpha=.2)
    ax.legend(frameon=False,fontsize=8,loc='upper right')
fig.suptitle('Actual VD year and pseudo-treatment-year',fontsize=16,fontweight='bold',y=.99)
fig.text(.045,.035,'Notes: 1,410 firms per group. Controls are indexed at founding year + 5. All intervals are calendar-year differences.\nFirst VC year is inferred from founding year + stored time to first VC; negative values in Panel C indicate reference years before first VC.',fontsize=9,color='#444444')
fig.tight_layout(rect=[0,.14,1,.94])
for ext in ['png','pdf','svg']: fig.savefig(OUT/f'reference_timing_distribution.{ext}',dpi=250,bbox_inches='tight')
print(OUT/'reference_timing_distribution.png')

