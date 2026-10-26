import pandas as pd
p=r'C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx'
x=pd.read_excel(p,header=1)
print(x.shape);print(x.columns.tolist());print(x.head(4).to_string());print(x['Funding Type'].value_counts().to_string())
x.to_pickle('deals_intensity_cache.pkl')
