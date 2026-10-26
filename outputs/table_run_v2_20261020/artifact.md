# Reference and output contract

Reference: C:/Users/user/Documents/VD/outputs/table_update_20261019/VD Table 20261019.docx.
Retain reference unchanged; preserve every package part except word/document.xml.
Source tables use Times New Roman, black text, white backgrounds, horizontal rules, coefficients with p-values in separate following rows, three decimals, and significance stars.
Reuse the actual source table XML and caption/note paragraphs, not generic table styling.
Output scope: active estimation and summary commands in the current v2 do-file. Omit main Tables 8–10. Do not copy old matching diagnostics or inactive innovation specifications as new results.
Create Table 3-2 stage coefficient and marginal-effect panels by cloning source regression rows. Retain main and appendix numbering; new innovation outcomes use A19–A21.
Use source portrait Letter geometry and 1-inch margins for portrait tables. Correlation tables use the source landscape Letter geometry and 1-inch margins. Page breaks separate tables. Fonts and cell widths follow source components; long DV labels may be shortened with full definition in notes.
Editable slots: table numeric cells, row labels that must reflect actual variables, captions, notes. Body content outside requested active tables is removed. Source styles, numbering, relationships, media, headers and footers are preserve-only package parts.
Rendering gate attempted with packaged render_docx.py: unavailable bundled LibreOffice. Native Word fallback failed with COM server and elevation errors. Therefore rendered reference page count and final visual fidelity remain unverified; do not claim rendered QA.
Numeric gate: coefficients, p-values and stars directly from Stata e(b), e(V), degrees of freedom; model/sample mapping recorded in models.json and cell audit JSON.
