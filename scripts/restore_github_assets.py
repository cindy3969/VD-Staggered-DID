"""Restore large originals after cloning. Existing files are verified, never overwritten."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'github_archive/manifest.json').read_text(encoding='utf-8'))
url='https://github.com/cindy3969/VD-Staggered-DID/releases/download/'+m['release_tag']+'/'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
for row in m['files']:
    if row['storage']!='release':continue
    dest=ROOT/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        if digest(dest)!=row['sha256']:raise RuntimeError('Existing file differs: '+row['path'])
        print('Verified',row['path']);continue
    temp=dest.with_name(dest.name+'.restore-partial')
    with temp.open('xb') as out:
        for part in row['assets']:
            with urllib.request.urlopen(url+part['name'],timeout=300) as response:
                for block in iter(lambda:response.read(4*1024*1024),b''):out.write(block)
    if temp.stat().st_size!=row['size'] or digest(temp)!=row['sha256']:raise RuntimeError('Verification failed: '+row['path'])
    temp.rename(dest);print('Restored',row['path'])
