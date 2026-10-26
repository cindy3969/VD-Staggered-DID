from pathlib import Path
import re
import pandas as pd

root=Path(r"C:\Users\user\Documents\VD\outputs\csdid_replicated_from_rebuilt_patent_list")
txt=(root/"replicate_table1_and_figures.log").read_text(encoding="utf-8",errors="replace")
old={
"all":(-.226,.024,-.190,.016,88547,7273),
"noprior":(-.050,.326,-.034,.325,83757,6892),
"prior":(-.817,.010,-.650,.011,75739,6255),
"early":(-.138,.072,-.070,.237,83285,6860),
"late":(-.528,.033,-.531,.013,76211,6287),
}
rows=[]
for label in old:
    m=re.search(rf"=== BEGIN_SPEC {label} OBS_RAW=([0-9]+) ===(.*?)(?:=== END_SPEC {label} ===)",txt,re.S)
    if not m: continue
    block=m.group(2)
    firm=re.search(r"FIRMS_RAW=([0-9]+)",block)
    atts=re.findall(r"^\s*ATT\s*\|\s*([-+.0-9eE]+)\s+([-+.0-9eE]+)\s+[-+.0-9eE]+\s+([0-9.]+)",block,re.M)
    post=re.search(r"^\s*Post_avg\s*\|\s*([-+.0-9eE]+)\s+([-+.0-9eE]+)\s+[-+.0-9eE]+\s+([0-9.]+)",block,re.M)
    oa,op,oe,oe_p,oo,of=old[label]
    a,se,p=map(float,atts[-1] if atts else (float('nan'),)*3)
    ev,evse,evp=map(float,post.groups()) if post else (float('nan'),)*3
    rows.append(dict(spec=label,new_simple_att=a,new_simple_p=p,new_event_att=ev,new_event_p=evp,
                     old_simple_att=oa,old_simple_p=op,old_event_att=oe,old_event_p=oe_p,
                     new_observations=int(m.group(1)),new_firms=int(firm.group(1)),old_observations=oo,old_firms=of,
                     simple_att_difference=a-oa,event_att_difference=ev-oe))
pd.DataFrame(rows).to_csv(root/"Table1_replication_comparison.csv",index=False,encoding="utf-8-sig")
print(pd.DataFrame(rows).to_string(index=False))
