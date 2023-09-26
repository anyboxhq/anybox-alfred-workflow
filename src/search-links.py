import urllib.request
import sys
import json
import os
from datetime import datetime

api_key = os.getenv('api_key')
show_full_urls = os.getenv('show_full_urls') == '1'
show_dates = os.getenv('show_dates') == '1'
show_tags = os.getenv('show_tags') == '1'
show_folders = os.getenv('show_folders') == '1'
limit = 5

if show_folders and show_tags:
  limit = 3

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

def format_url(url):
    if url.startswith('https://'):
        return remove_prefix(url, 'https://')
    elif url.startswith('http://'):
        return url.remove_prefix(url, 'http://')
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
    if 'comment' in link and link['comment'] != "":
      subtitle = subtitle + ' • ' + link['comment']
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

def get_containers(type):
  payload = {
    'q': q,
    'limit': limit,
  }
  url = ''
  anybox_url_prefix = ""
  icon_path = ''
  sub_title = ''

  if type == 'tag':
    url = 'http://127.0.0.1:6391/tags?'
    anybox_url_prefix = 'anybox://tag/'
    icon_path = './List Icons/tag.png'
    sub_title = 'Tag'
  else:
    url = 'http://127.0.0.1:6391/folders?'
    anybox_url_prefix = 'anybox://folder/'
    icon_path = './List Icons/folder.png'
    sub_title = 'Folder'

  data = urllib.parse.urlencode(payload)
  req = urllib.request.Request(url + data)
  try: 
    resp = urllib.request.urlopen(req) 
    items = json.loads(resp.read())
    result = []
    for list_item in items:
      id = list_item['id']
      name = list_item['name']
      anybox_url = anybox_url_prefix + id
      markdown_url = '[' + name + ']' + '(' + anybox_url + ')'
      item = {
        'title': name,
        'subtitle': sub_title,
        'variables': { 'type': type },
        'arg': [id],
        'icon': {
          'path': icon_path
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
          }
        },
      }
      result.append(item)
    return result
  except urllib.error.HTTPError as e:
    throw_error()
  except urllib.error.URLError as e:
    throw_error()

tags = []
folders = []
if show_tags:
  tags = get_containers('tag')
if show_folders:
  folders = get_containers('folder')

links = get_links()
result = {
  'items': tags + folders + links
}
sys.stdout.write(json.dumps(result))