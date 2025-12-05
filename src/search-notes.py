import urllib.request
import sys
import json
import os
from datetime import datetime

api_key = os.getenv('api_key')
show_dates = os.getenv('show_dates') == '1'
limit = 5

q = ''
if len(sys.argv) >= 2:
    q = sys.argv[1]

def is_today(date):
    today = datetime.today().replace(tzinfo=date.tzinfo)
    if (today - date).days == 0:
        return True
    else:
        return False

def is_yesteryday(date):
    today = datetime.today().replace(tzinfo=date.tzinfo)
    if (today - date).days == 1:
        return True
    else:
        return False

def less_than_a_week(date):
    today = datetime.today().replace(tzinfo=date.tzinfo)
    if (today - date).days <= 7:
        return True
    else:
        return False
    
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

# E.g., 2021-12-09T02:40:12Z
def format_date(original):
    date = datetime.strptime(original, "%Y-%m-%dT%H:%M:%S%z")
    tz = datetime.now().astimezone().tzinfo
    if is_today(date):
        return 'Today at ' + date.astimezone(tz).strftime("%H:%M")
    elif is_yesteryday(date):
        return 'Yesterady at ' + date.astimezone(tz).strftime("%H:%M")
    elif less_than_a_week(date):
        return date.astimezone(tz).strftime("%b %d, %Y at %H:%M")
    return date.astimezone(tz).strftime("%b %d, %Y")

def format_subtitle(note):
    subtitle = ''
    if len(note['description']) == 1:
        subtitle = '1 character'
    else:
        subtitle = f"{len(note['description'])} characters"
    if show_dates:
        subtitle = subtitle + ' • ' + format_date(note['dateLastOpened'])
    if 'comment' in note and note['comment'] != "":
      subtitle = subtitle + ' • ' + note['comment']
    return subtitle

def throw_error():
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
  sys.stdout.write(json.dumps(error_feedback))

def get_notes():
  headers = {'x-api-key': api_key}
  payload = {
      'q': q,
      'limit': 30,
      'type': 'note'
  }
  data = urllib.parse.urlencode(payload)
  req = urllib.request.Request('http://127.0.0.1:6391/search?' + data, headers=headers)
  try:
    with urllib.request.urlopen(req) as response:
      list = json.loads(response.read())
      result = []
      for note in list:
        text = note['description']
        title = note['title']
        anybox_url = 'anybox://document/' + note['id']
        item = {
              'title': title,
              'subtitle': format_subtitle(note),
              'arg': [text, note['id']],
              "variables": {"uuid": note['id'], "text": text},
              'text': {
                  'copy': text,
                  'largetype': text
              },
              'mods': {
                  'cmd': {
                      'valid': True,
                      'arg': anybox_url,
                      'subtitle': anybox_url
                  },
              }
          }
        result.append(item)
    return result
  except urllib.error.HTTPError as e:
    throw_error()
  except urllib.error.URLError as e:
    throw_error()

notes = get_notes()
result = {
  'items': notes
}
sys.stdout.write(json.dumps(result))