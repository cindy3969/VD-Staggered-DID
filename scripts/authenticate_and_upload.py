"""One-time GitHub device authentication; credentials stay in process memory."""
import base64,json,os,subprocess,sys,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLIENT='0120e057bd645470c1ed'  # Public Git Credential Manager OAuth client ID.
def post(url,data):
    req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={'Accept':'application/json','User-Agent':'VD-archive'})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
d=post('https://github.com/login/device/code',{'client_id':CLIENT,'scope':'repo'})
print(json.dumps({k:d[k] for k in ('user_code','verification_uri','expires_in')}),flush=True)
deadline=time.monotonic()+d['expires_in'];interval=d.get('interval',5)
while time.monotonic()<deadline:
    time.sleep(interval)
    r=post('https://github.com/login/oauth/access_token',{'client_id':CLIENT,'device_code':d['device_code'],'grant_type':'urn:ietf:params:oauth:grant-type:device_code'})
    if 'access_token' in r:break
    if r.get('error')=='slow_down':interval+=5
    elif r.get('error')!='authorization_pending':raise RuntimeError(r.get('error'))
else:raise RuntimeError('Device authorization expired')
env=os.environ.copy();env['VD_GITHUB_TOKEN']=r['access_token']
env['GIT_CONFIG_COUNT']='2';env['GIT_CONFIG_KEY_0']='http.https://github.com/.extraheader'
env['GIT_CONFIG_VALUE_0']='Authorization: Basic '+base64.b64encode(('x-access-token:'+r['access_token']).encode()).decode()
env['GIT_CONFIG_KEY_1']='credential.helper';env['GIT_CONFIG_VALUE_1']=''
git=['git','-c','safe.directory='+ROOT.as_posix()]
print('Authenticated; uploading Git repository.',flush=True)
subprocess.run(git+['push','--progress','-u','origin','main'],cwd=ROOT,env=env,check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/upload_github_assets.py')],cwd=ROOT,env=env,check=True)
print('All uploads completed.',flush=True)
