from urllib import request
import sys
import json
import os

def get_items():
  req = request.Request('http://127.0.0.1:6391/anydock-profiles')
  resp = request.urlopen(req) 
  items = json.loads(resp.read())
  result = {
    'items': []
  }
  for list_item in items:
    id = list_item['id']
    item = {
      'title': list_item['name'],
      'arg': [id],
      'icon': {
        'path': './List Icons/anydock.png'
      },
    }
    result['items'].append(item)
  return json.dumps(result)

sys.stdout.write(get_items())

