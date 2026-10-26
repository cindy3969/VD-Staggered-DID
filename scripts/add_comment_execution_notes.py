from pathlib import Path
from copy import deepcopy
import re
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

BASE = Path("C:/Users/user/iCloudDrive/5학기/연구미팅/VD PPT")
OUT = Path("C:/Users/user/Documents/VD/outputs/comment_execution_notes")
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{"+NS["w"]+"}"

# Statements describe analyses actually displayed in the supplied results document.
COMMENTS = {
3: ("Execution — Tables 4-1 and 4-2. ",
    "We classified firms as Seed/pre-Series, Series A, Series B, or Series C+ and estimated VD-by-stage interactions, followed by average VD effects within each stage. The negative association is strongest at Series C+; the two alternative binary early-stage definitions are not separately reported in these tables."),
4: ("Execution — Table A16. ",
    "We summarized time from founding to first VC, founding to first VD, and first VC to VD in the pre-matching sample. These averages document the financing sequence; the full timing distributions and a revised pseudo-treatment assignment are not reported in this table."),
5: ("Execution — Tables 9–12 and Figures A3–A5. ",
    "We estimated Callaway–Sant’Anna staggered DiD models on annual patent outcomes, using first VD year as treatment timing and comparing never-treated with not-yet-treated controls. Event-study estimates span years −4 to +4 and examine pre-treatment patterns, post-treatment dynamics, and heterogeneity; the panel samples are distinct from the 2,820-firm matched cross-section."),
6: ("Execution — Tables 13 and 14. ",
    "We related post-VD patenting to initial VD amount and VD relative to the preceding equity round using firm and year fixed effects, lagged controls, and moderator interactions. The amount and ratio models cover 1,235 and 982 firms, respectively, and are interpreted as descriptive intensity analyses rather than causal dose-response estimates; the remaining proposed intensity measures and missing-amount comparisons are not shown."),
7: ("Execution — Lender-classification table. ",
    "We classified the 714 matched VD firms with available investor names into specialized providers, venture-lending banks, other institutional lenders, and ambiguous cases. The other 696 firms remain unidentified; names provide a measurement check, not proof that every named investor supplied VD or that unnamed records are invalid."),
8: ("Execution — Table A15 and Figures A1–A2. ",
    "We report before/after matching comparisons, propensity-score overlap, and a Love plot of covariate balance. Table A15 is the current balance table, replacing the A9 cross-reference above; its mean-difference tests should be read alongside standardized differences, while variance ratios and explicit common-support counts are not tabulated here."),
9: ("Execution — Tables A7–A14. ",
    "We added patent-text readability, patents in new versus existing CPC domains, entry into new CPC classes, backward-citation breadth, and self-citations over the three-year post-reference window. New-domain measures use a fixed pre-VD portfolio, and regressions examine heterogeneity by prior patents and stage; these are distinct measures of innovation content, while technological distance, originality, and job-posting outcomes are not reported."),
10: ("Execution — Table A3, Panels A–C. ",
     "We separate equity-raising probability (OLS linear probability models), next-round hazard (Cox), waiting time (Weibull AFT), and next-round log amount conditional on raising. Cumulative financing uses ln(1 + USD), includes no-round zeros, and retains undisclosed amounts as missing; follow-up starts at reference-year end and provisionally ends in December 2023."),
11: ("Execution — Tables A4–A6. ",
     "We placed employee regressions and pooled/annual revenue comparisons in the Appendix. The employee analysis uses 611 observations and revenue coverage is sparse, so these outcomes provide supplementary context rather than central evidence."),
12: ("Interpretation — Table 8. ",
     "We report separate Cox models for M&A, IPO, and defunct outcomes, with baseline and controlled specifications. These associations describe subsequent firm trajectories; they are not interpreted as automatic improvements in performance or as causal evidence equivalent to the innovation analyses."),
13: ("Consolidation — Table 8 and the current Appendix. ",
     "The current report consolidates baseline exit results in Table 8 and no longer presents the previous separate M&A/IPO/defunct interaction tables. Tables A3–A5 now contain financing, employee, and revenue evidence; manuscript cross-references should follow this revised numbering."),
14: ("Execution status — Table A1. ",
     "We report the baseline regional-VD instrument specification, its first-stage regression, and the displayed first-stage diagnostics. Table A1 does not yet report IV estimates for VD × Prior Patent or VD × Early Stage, or their interaction-specific strength tests, so the requested H2/H3 IV diagnostics remain outstanding."),
15: ("Status — Timeline deferred. ",
     "No final research-design timeline is included. Table A16 documents the financing sequence and Figures A3–A5 inform the event-time design; the timeline can be finalized after choosing the role of the matched and staggered DiD analyses."),
}

# Anchors are body indices verified against the original files.
RESULT_NOTES = {
21: ("Execution — Comment 3. ", "Tables 4-1 and 4-2 estimate VD-by-stage interactions and average VD effects for Seed/pre-Series, Series A, Series B, and Series C+. They assess stage heterogeneity without relying on a single binary cutoff; separate estimates for both proposed binary definitions are not shown."),
39: ("Interpretation — Comments 12–13. ", "Table 8 consolidates M&A, IPO, and defunct Cox results. These exit associations provide context for firm trajectories and are not interpreted as automatic performance improvements or causal validation of the patent results."),
58: ("Execution — Comment 5. ", "Tables 9–12 estimate staggered DiD effects on annual patent quantity and citations, comparing never-treated and not-yet-treated controls. Figures A3–A5 assess pre-treatment patterns, dynamics, and heterogeneity; these panel samples differ from the 2,820-firm matched cross-section."),
66: ("Execution — Comment 6. ", "Tables 13–14 interact initial VD amount or VD relative to the preceding equity round with the post-VD indicator, using firm/year fixed effects and lagged controls. These are descriptive intensity analyses; endogenous borrowing amounts prevent a causal dose-response interpretation."),
72: ("Execution status — Comment 14. ", "Table A1 reports the baseline 2SLS model and its first stage. The requested IV models for the prior-patent and early-stage interactions, with interaction-specific first-stage diagnostics, are not yet reported."),
90: ("Execution — Comment 10. ", "Panel A uses OLS linear probability models; Panel B uses Cox hazard, Weibull AFT, and conditional log-amount OLS models. Panel C uses OLS for ln(1 + cumulative equity USD), retaining no-round zeros and excluding undisclosed amounts. Fixed horizons require complete follow-up; survival models retain censoring. Follow-up starts at reference-year end, with coverage provisionally assumed through December 2023."),
104: ("Execution — Comment 11. ", "Tables A4–A6 place employee regressions and pooled/annual revenue comparisons in the Appendix. Their smaller samples make them supplementary evidence rather than primary outcomes."),
146: ("Execution — Comment 9. ", "Tables A7–A14 extend the analysis to readability, new/existing technological domains, CPC entry, citation breadth, and self-citations. Domain measures compare post-VD patents with a fixed pre-VD portfolio, allowing innovation content to be examined separately from patent quantity."),
151: ("Execution — Comment 8. ", "Table A15 and Figures A1–A2 document matching balance and overlap. Mean-difference p-values alone do not establish comparability; standardized differences in the Love plot provide a complementary diagnostic. Variance ratios and explicit common-support counts are not reported in this table."),
155: ("Execution — Comments 4 and 15. ", "Table A16 summarizes mean financing intervals in the pre-matching sample. It documents the lifecycle sequence but does not provide full timing distributions or establish that pseudo-treatment timing is comparable; the final design timeline remains deferred."),
}

def text(el):
    return "".join(el.itertext()) if False else "".join(t.text or "" for t in el.iter(W+"t"))

def paragraph(label, body):
    p=E.Element(W+"p")
    pr=E.SubElement(p,W+"pPr")
    spacing=E.SubElement(pr,W+"spacing")
    spacing.set(W+"before","100"); spacing.set(W+"after","120")
    spacing.set(W+"line","240"); spacing.set(W+"lineRule","auto")
    E.SubElement(pr,W+"widowControl")
    for value, bold in [(label,True),(body,False)]:
        r=E.SubElement(p,W+"r"); rp=E.SubElement(r,W+"rPr")
        f=E.SubElement(rp,W+"rFonts")
        for attr in ("ascii","hAnsi","eastAsia"): f.set(W+attr,"Times New Roman")
        E.SubElement(rp,W+"sz").set(W+"val","21")
        E.SubElement(rp,W+"color").set(W+"val","000000")
        if bold: E.SubElement(rp,W+"b")
        t=E.SubElement(r,W+"t");t.set("{http://www.w3.org/XML/1998/namespace}space","preserve");t.text=value
    return p

def edit(name, comments=False):
    src=BASE/name
    with ZipFile(src) as z:
        original=z.read("word/document.xml")
        root=E.fromstring(original);body=root.find("w:body",NS);children=list(body)
        old_tables=[E.tostring(t) for t in root.findall(".//w:tbl",NS)]
        added=[]
        if comments:
            starts=[(i,int(re.match(r"^(\d+)\.",text(el)).group(1))) for i,el in enumerate(children)
                    if re.match(r"^(?:[3-9]|1[0-5])\.\s",text(el))]
            for pos,(i,n) in enumerate(starts):
                end=starts[pos+1][0] if pos+1<len(starts) else len(children)-1
                anchor=next((children[j] for j in range(end-1,i,-1) if text(children[j]).strip()), children[i])
                # Lender note follows the unnumbered classification table.
                anchor.addnext(paragraph(*COMMENTS[n]));added.append(n)
            # Correct only the reviewer-response mapping, not the quoted request.
            target=children[116]
            for t in list(target.iter(W+"t")): t.text=""
            first=next(target.iter(W+"t"));first.text="Table A15"
        else:
            for i,note in RESULT_NOTES.items(): children[i].addnext(paragraph(*note))
            added=list(RESULT_NOTES)
        assert [E.tostring(t) for t in root.findall(".//w:tbl",NS)]==old_tables
        result=E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
        target=OUT/(src.stem+"_with execution notes.docx")
        with ZipFile(target,"w",ZIP_DEFLATED) as dest:
            for item in z.infolist():
                dest.writestr(item,result if item.filename=="word/document.xml" else z.read(item.filename))
    with ZipFile(target) as z:
        assert z.testzip() is None
    print(target, "added", len(added), "notes; all tables unchanged")

edit("20261020 VD Table.docx",True)
edit("20261020 VD Table_matched 2820.docx")
