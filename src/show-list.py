from urllib import request
import sys
import json

def list_icon(type, id):
  url = './List Icons/'
  if type == 'preset':
    return url + id + '.png'
  elif type == 'collection':
    return url + 'collection.png'
  elif type == 'filter':
    return url + 'filter.png'
  else:
    return ''

def list_url(type, id):
  if type == 'preset':
    return 'anybox://show?id=' + id
  elif type == 'collection':
    return 'anybox://collection/' + id
  elif type == 'filter':
    return 'anybox://filter/' + id
  else:
    return 'anybox://show'

def list_type_name(type):
  if type == 'preset':
    return 'Preset'
  elif type == 'collection':
    return 'Collection'
  elif type == 'filter':
    return "Smart List"
  else:
    return 'Unknown'


def get_items(type):
  req = request.Request('http://127.0.0.1:6391/' + type)
  resp = request.urlopen(req) 
  items = json.loads(resp.read())
  result = []
  for list_item in items:
    id = list_item['id']
    list_type = list_item['type']
    icon = list_icon(list_type, id)
    url = list_url(list_item['type'], id)
    subtitle = list_type_name(list_type) + ' • ' + str(list_item['count']) + ' items'
    item = {
      'title': list_item['name'],
      'subtitle':  subtitle,
      'arg': [url],
      'icon': {
        'path': icon
      },
    }
    result.append(item)
  return result

def get_presets():
  return get_items('presets')

def get_filters():
  return get_items('filters')

def get_collections():
  return get_items('collections')

presets = get_presets()
filters = get_filters()
collections = get_collections()

all =  {
  'items': presets + filters + collections
}
sys.stdout.write(json.dumps(all))

