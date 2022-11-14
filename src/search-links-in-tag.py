import urllib.request
import sys
import json
import os
from datetime import datetime

api_key = os.getenv('api_key')
show_full_urls = os.getenv('show_full_urls') == '1'
show_dates = os.getenv('show_dates') == '1'
collection_id = os.getenv('collection')

q = '{query}'

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

def format_url(url):
    if url.startswith('https://'):
        return url.removeprefix('https://')
    elif url.startswith('http://'):
        return url.removeprefix('http://')
    else:
        return url

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

def format_subtitle(link):
    subtitle = ''
    date = ''
    if show_dates:
        date = ' • ' + format_date(link['dateLastOpened'])
    if show_full_urls:
        subtitle = format_url(link['url']) + date
    else:
        subtitle = link['host'] + date
    return subtitle


def download_file(url, folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)
        try:
            urllib.request.urlretrieve(url, folder + '/icon')
        except:
            try:
                urllib.request.urlretrieve(
                    "http://127.0.0.1:6391/images/default-browser-icon.png",
                    folder + '/icon')
            except:
                ()

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

def get_links():
  headers = {'x-api-key': api_key}
  payload = {
      'q': q,
      'limit': 30,
      'collection': collection_id
  }
  data = urllib.parse.urlencode(payload)
  req = urllib.request.Request('http://127.0.0.1:6391/search?' + data, headers=headers)
  try:
    with urllib.request.urlopen(req) as response:
      list = json.loads(response.read())
      result = []
      for link in list:
        icon_url = 'http://127.0.0.1:6391/images/' + link['id'] + '/icon'
        icon_relative_url = './Link Icons/' + link['id']
        download_file(icon_url, icon_relative_url)
        url = link['url']
        title = link['title']
        markdown_url = '[' + title + ']' + '(' + url + ')'
        anybox_url = 'anybox://document/' + link['id']
        item = {
              'title': title,
              'subtitle': format_subtitle(link),
              'arg': [url, link['id']],
              'icon': {
                  'path': icon_relative_url + "/icon"
              },
              'text': {
                  'copy': url,
                  'largetype': title
              },
              'mods': {
                  'alt': {
                      'valid': True,
                      'arg': markdown_url,
                      'subtitle': markdown_url
                  },
                  'cmd': {
                      'valid': True,
                      'arg': anybox_url,
                      'subtitle': anybox_url
                  },
                  'shift': {
                      'valid': True,
                      'arg': url,
                      'subtitle': url
                  },
                  
              },
              'quicklookurl': url
          }
        result.append(item)
    return result
  except urllib.error.HTTPError as e:
    throw_error()
  except urllib.error.URLError as e:
    throw_error()


links = get_links()
result = {
  'items': links
}
sys.stdout.write(json.dumps(result))