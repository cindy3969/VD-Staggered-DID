"""Inventory files and route files over 50 MiB to GitHub release assets."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'github_archive'
OUT.mkdir(exist_ok=True)
excluded={'.git','node_modules','.artifact_work/plot_packages','.artifact_work/textstat_deps'}
files=[];skipped=[]
for base,dirs,names in os.walk(ROOT):
    for name in dirs[:]:
        p=Path(base)/name; rel=p.relative_to(ROOT).as_posix()
        if rel in excluded or name=='node_modules' or p.is_symlink() or p.is_junction():
            dirs.remove(name);skipped.append(rel)
    for name in names:
        p=Path(base)/name;rel=p.relative_to(ROOT).as_posix()
        if rel.startswith('github_archive/') or rel in {'.gitignore','README.md'}: continue
        size=p.stat().st_size
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
        files.append({'path':rel,'size':size,'sha256':h.hexdigest(),'storage':'release' if size>50*1024*1024 else 'git'})
large=[f for f in files if f['storage']=='release']
for i,f in enumerate(large):
    f['assets']=[{'name':f'vd-{i:03d}-{j:03d}.bin','offset':off,'size':min(1024**3,f['size']-off)} for j,off in enumerate(range(0,f['size'],1024**3))]
(OUT/'manifest.json').write_text(json.dumps({'snapshot_date':'2026-10-26','release_tag':'vd-archive-2026-10-26','excluded_dependencies':skipped,'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'.gitignore').write_text('/node_modules/\n**/node_modules/\n/.artifact_work/plot_packages/\n/.artifact_work/textstat_deps/\n/github_archive/upload_status.json\n'+''.join('/'+f['path']+'\n' for f in large),encoding='utf-8')
print(json.dumps({'files':len(files),'bytes':sum(f['size'] for f in files),'release_files':len(large),'git_bytes':sum(f['size'] for f in files if f['storage']=='git'),'excluded':skipped}))
