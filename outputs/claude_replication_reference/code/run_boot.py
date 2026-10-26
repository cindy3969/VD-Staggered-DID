import json,subprocess,time
subs=['all','noprior','prior','early','late']
jobs=[[s,y,'never',2024,True,49,7] for y in ['ultimately_granted_filings','cite_mean'] for s in subs]
running=[];i=0
while i<len(jobs) or running:
    running=[p for p in running if p.poll() is None]
    while len(running)<2 and i<len(jobs):
        running.append(subprocess.Popen(['python3','dripw.py',json.dumps([jobs[i]]),f'bt_{i}.csv'],stdout=open(f'bt_{i}.log','w'),stderr=subprocess.STDOUT)); i+=1
    time.sleep(5)
