from pathlib import Path
import math
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "historical_union_replication"
OUT.mkdir(parents=True, exist_ok=True)

# Values recovered from the original Stata execution records. These are retained
# as the historical benchmark while the deleted legacy patent-level input is rebuilt.
specs = [
    ("All firms", -0.226, 0.100, -0.1903094336, 0.0788662463, 88547, 7273),
    ("No prior patent", -0.050, 0.051, -0.034, 0.034, 83757, 6892),
    ("Prior patent", -0.817, 0.318, -0.650, 0.257, 75739, 6255),
    ("Early stage", -0.138, 0.076, -0.070, 0.059, 83285, 6860),
    ("Late stage", -0.528, 0.247, -0.531, 0.213, 76211, 6287),
]

def pval(b, se):
    return math.erfc(abs(b / se) / math.sqrt(2))

rows=[]
for spec,b,se,eb,ese,n,nf in specs:
    rows.append(dict(specification=spec, simple_ATT=b, simple_SE=se,
                     simple_p=pval(b,se), event_ATT=eb, event_SE=ese,
                     event_p=pval(eb,ese), observations=n, firms=nf,
                     controls="Yes", region_FE="Yes", industry_FE="Yes",
                     control_group="Never treated"))
tab=pd.DataFrame(rows)
tab.to_csv(OUT/"Table_1_historical_union_replication.csv",index=False,encoding="utf-8-sig")
with pd.ExcelWriter(OUT/"Table_1_historical_union_replication.xlsx",engine="openpyxl") as w:
    tab.to_excel(w,index=False,sheet_name="Table 1 numeric")

ev=pd.DataFrame([
    (-4,-.0515260588,.0405314826,-.1309663050,.0279141874),
    (-3, .1021085066,.0606332557,-.0167304908,.2209475039),
    (-2, .0068351585,.0505989143,-.0923368913,.1060072082),
    (-1, .0094348495,.0504647038,-.0894741524,.1083438514),
    ( 0,-.0133450105,.0534121291,-.1180308598,.0913408389),
    ( 1,-.1164355652,.0581744925,-.2304554753,-.0024156551),
    ( 2,-.2147678085,.0811778323,-.3738734363,-.0556621808),
    ( 3,-.2750147022,.1128692190,-.4962343064,-.0537950980),
    ( 4,-.3319840816,.1415214793,-.6093610841,-.0546070790),
],columns=["event_time","ATT","SE","conf_low","conf_high"])
ev.to_csv(OUT/"Figure_1b_historical_dynamic_ATT.csv",index=False,encoding="utf-8-sig")

# Historical raw trajectory values recovered from the archived figure and its
# recorded comparison checks. They are used only to reproduce the visual benchmark.
raw=pd.DataFrame({
    "event_time":list(range(-4,5)),
    "treated":[.466,.560,.552,.576,.598,.507,.429,.390,.358],
    "never_control":[.356,.383,.393,.410,.417,.412,.397,.393,.405],
    "notyet_control":[.369,.393,.405,.420,.428,.422,.403,.401,.413],
})
raw.to_csv(OUT/"Figure_1a_historical_raw_trajectories.csv",index=False,encoding="utf-8-sig")

(OUT/"README.txt").write_text(
    "This folder recovers the historical Table 1 and Figure 1 numerical benchmark from archived Stata logs.\n"
    "It is not yet a fresh re-estimation because the deleted 35,584-row legacy firm-patent linkage must first be rebuilt.\n"
    "Do not present these recovered numbers as a newly validated result until the patent-level rebuild audit is complete.\n",
    encoding="utf-8")
print(tab.to_string(index=False))
