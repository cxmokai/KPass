#!/Users/cxmokai/.asdf/shims/python
import sys
import os
from time import time
import subprocess
import json

cacheFile = os.getenv('cacheFile')
cacheTimeout = os.getenv('cacheTimeout')
database = os.getenv('database')
keePassKeyFile = os.getenv('keePassKeyFile')
keychain = os.getenv('keychain')
keychainItem = os.getenv('keychainItem')

def get_db_keys():
  path = '/bin:/usr/local/bin/:/usr/bin:/Applications/KeePassXC.app/Contents/MacOS/:/opt/homebrew/bin'
  if os.path.exists(keePassKeyFile):
    shell = '''
      security find-generic-password -a $(id -un) -c 'kpas' -C 'kpas' -s "{keychainItem}" -w "{keychain}" |
      keepassxc-cli search --key-file "{keePassKeyFile}" "{database}" - -q
    '''.format(keychainItem=keychainItem, keychain=keychain, keePassKeyFile=keePassKeyFile, database=database)
  else:
    shell = '''
      security find-generic-password -a $(id -un) -c 'kpas' -C 'kpas' -s "{keychainItem}" -w "{keychain}" |
      keepassxc-cli search "{database}" - -q
    '''.format(keychainItem=keychainItem, keychain=keychain, database=database)
  res = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=dict(os.environ, PATH=path))
  return res.stdout.read().decode("utf-8")  # 如果错误，标准输出为空，错误信息在res.stderr.read()

def get_db_keys_from_cache():
  if os.path.exists(cacheFile):
    last_modified_time = os.path.getmtime(cacheFile)
  else:
    last_modified_time = 0
  now = time()
  if now - last_modified_time > int(cacheTimeout):
    db_keys = get_db_keys()
    with open(cacheFile, 'w') as f:
      f.write(db_keys)
  # Get keys from the cache
  try:
    with open(cacheFile, 'r') as f:
      cached_db_keys = f.read()
  except:
    cached_db_keys = ''
  return cached_db_keys

def get_keys():
  if cacheFile.isspace() or cacheFile == '': # 未设置缓存
    db_keys = get_db_keys()
  else:
    db_keys = get_db_keys_from_cache()
  query = sys.argv[1] if len(sys.argv) > 1 else ''
  if query.isspace() or query == '':
    db_keys_list = list(filter(lambda key: key != '', db_keys.split('\n')))
  else:
    db_keys_list = list(filter(lambda key: query in key.lower(), filter(lambda key: key != '', db_keys.split('\n'))))
  return db_keys_list

def get_item_dict(item):
  return {
    'uid': item,
    'title': item,
    'subtitle': item,
    'arg': item,
    'autocomplete': item,
  }

db_keys_list = get_keys()

if (len(db_keys_list) == 0):
  print(json.dumps({
    'items': [{
      'uid': '无搜索结果',
      'title': '无搜索结果',
      'subtitle': '未匹配关键字',
    }]
  }))
else:
  print(json.dumps(
    { "items": list(map(lambda item: get_item_dict(item), get_keys())) }
  ))

