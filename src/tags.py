from urllib import request
import urllib.error
import sys
import json

error_feedback = {
  'items': [
    {
      'title': 'It looks like Anybox it’s not running or haven’t installed.',
      'subtitle': 'Press ⏎ to open Anybox or press ⌘ + ⏎ to install Anybox in Mac App Store.',
      'arg': ['anybox://show'],
      'mods': {
        'cmd': {
            'valid': True,
            'arg': 'itms-apps://apps.apple.com/app/id1593408455',
            'subtitle': 'Install Anybox on Mac App Store.'
        },
      }
    }
  ]
}

def get_tags():
  req = request.Request('http://127.0.0.1:6391/tags')
  try: 
    resp = request.urlopen(req) 
    items = json.loads(resp.read())
    result = {
      'items': []
    }
    for list_item in items:
      id = list_item['id']
      name = list_item['name']
      item = {
        'title': name,
        'arg': [id],
        'icon': {
          'path': './List Icons/tag.png'
        },
      }
      result['items'].append(item)
    sys.stdout.write(json.dumps(result))
  except urllib.error.HTTPError as e:
    sys.stdout.write(json.dumps(error_feedback))
  except urllib.error.URLError as e:
    sys.stdout.write(json.dumps(error_feedback))

get_tags()
