import pandas as pd
from pathlib import Path
for name in ['outputs/csdid_replicated_from_rebuilt_patent_list/csdid_rebuilt_patent_panel.dta','outputs/csdid_replicated_from_rebuilt_patent_list/csdid_all_published_applications_panel.dta']:
 f=pd.read_stata(name,convert_categoricals=False);print(name,f.shape);print(f.columns.tolist());print(f.head(1).to_string(index=False))
