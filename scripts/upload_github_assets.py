"""Upload the manifest's large files without staging extra copies on disk."""
import hashlib,http.client,json,subprocess,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO='cindy3969/VD-Staggered-DID'
manifest=json.loads((ROOT/'github_archive/manifest.json').read_text(encoding='utf-8'))
cred=subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,check=True)
token=dict(line.split('=',1) for line in cred.stdout.splitlines() if '=' in line)['password']
headers={'Authorization':'Bearer '+token,'User-Agent':'VD-archive','Accept':'application/vnd.github+json'}
def api(path,data=None):
    req=urllib.request.Request('https://api.github.com/repos/'+REPO+path,headers=headers,data=None if data is None else json.dumps(data).encode())
    with urllib.request.urlopen(req,timeout=120) as r:return json.load(r)
try: release=api('/releases/tags/'+manifest['release_tag'])
except urllib.error.HTTPError as e:
    if e.code!=404:raise
    release=api('/releases',{'tag_name':manifest['release_tag'],'name':'VD complete data archive — 2026-10-26','body':'Large original files are stored as numbered assets. See github_archive/manifest.json for original paths, SHA-256 hashes and part order. Run scripts/restore_github_assets.py after cloning to restore the original folder layout.','draft':False,'prerelease':False})
existing={a['name']:a for a in api('/releases/'+str(release['id'])+'/assets?per_page=100')}
done=[]
for f in manifest['files']:
    for part in f.get('assets',[]):
        name=part['name']
        if name in existing:
            assert existing[name]['size']==part['size'],name
            done.append(name);continue
        for attempt in range(4):
            try:
                conn=http.client.HTTPSConnection('uploads.github.com',timeout=300)
                conn.putrequest('POST',f'/repos/{REPO}/releases/{release["id"]}/assets?name={name}')
                for k,v in headers.items():conn.putheader(k,v)
                conn.putheader('Content-Type','application/octet-stream');conn.putheader('Content-Length',str(part['size']));conn.endheaders()
                with (ROOT/f['path']).open('rb') as src:
                    src.seek(part['offset']);remaining=part['size']
                    while remaining:
                        block=src.read(min(4*1024*1024,remaining))
                        if not block:raise RuntimeError('File changed during upload')
                        conn.send(block);remaining-=len(block)
                response=conn.getresponse();body=response.read();conn.close()
                if response.status!=201:raise RuntimeError(f'Upload {name}: HTTP {response.status}: {body[:300]!r}')
                result=json.loads(body);assert result['size']==part['size']
                print(json.dumps({'uploaded':name,'bytes':part['size'],'file':f['path']}),flush=True)
                done.append(name);break
            except Exception:
                if attempt==3:raise
                time.sleep(3)
        (ROOT/'github_archive/upload_status.json').write_text(json.dumps({'release':release['html_url'],'assets':done}),encoding='utf-8')
print(json.dumps({'complete':True,'assets':len(done),'release':release['html_url']}),flush=True)
