"""Read the EXISTING Pages production branch instead of assuming 'main'."""
import json
import os
import re
from urllib.request import Request, urlopen

account=os.environ['CLOUDFLARE_ACCOUNT_ID']
if not re.fullmatch(r'[a-fA-F0-9]{32}',account):
    raise ValueError('Invalid Cloudflare account ID')
url=f'https://api.cloudflare.com/client/v4/accounts/{account}/pages/projects/sustella-home'
request=Request(url,headers={'Authorization':'Bearer '+os.environ['CLOUDFLARE_API_TOKEN']})
with urlopen(request,timeout=25) as response:
    payload=json.load(response)
if not payload.get('success'):
    raise RuntimeError('Could not read the existing Cloudflare Pages project')
branch=payload['result']['production_branch']
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*',branch):
    raise ValueError('Invalid Pages production branch')
with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf-8') as output:
    output.write('branch='+branch+'\n')
print('Existing Pages production branch verified.')
