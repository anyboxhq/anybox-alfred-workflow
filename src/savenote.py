from urllib import request
import urllib.error
import json
import sys

note = ''
if len(sys.argv) >= 2:
   note = sys.argv[1]

payload = {
	'note': note
}
data = json.dumps(payload).encode("utf-8")
headers = {'Content-Type': 'application/json'}
req = request.Request('http://127.0.0.1:6391/save', headers=headers, data=data, method='POST')

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

try:
    request.urlopen(req)
except urllib.error.HTTPError as e:
    sys.stdout.write(error_feedback)
except urllib.error.URLError as e:
    sys.stdout.write(error_feedback)