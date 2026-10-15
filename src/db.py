import os
import json
import btree
from hardware import sdcard

# ---- Configuration ----

SD_MOUNT = '/sd'
DATA_DIR = SD_MOUNT + '/app_data/lift'
DB_PATH = DATA_DIR + '/lift.db'

# Key layout (values are JSON):
#   ex:<name>    -> {description, weight, reps, sets} (the last three are bools)
#   plan:<name>  -> [exercise names in order]
#   meta:current -> current plan name
#   meta:order   -> [plan names in display order]
#   log:<YYYY-MM-DD>:<exercise> -> {done, sets: [[weight, reps], ...]} (values are strings)
_f = None
_db = None

# ---- Connection ----

def _mount_sd():
  try:
    os.listdir(SD_MOUNT)
    return
  except OSError:
    pass
  # Note: SDCard umounts /sd first and prints EINVAL when nothing is mounted yet.
  sdcard.SDCard(slot=3, width=1, sck=40, miso=39, mosi=14, cs=12, freq=20000000)

def _ensure_dir(path):
  cur = ''
  for part in path.split('/')[1:]:
    cur += '/' + part
    try:
      os.mkdir(cur)
    except OSError:
      pass

def open_db():
  global _f, _db
  _mount_sd()
  _ensure_dir(DATA_DIR)
  try:
    _f = open(DB_PATH, 'r+b')
  except OSError:
    _f = open(DB_PATH, 'w+b')
  _db = btree.open(_f)

def close_db():
  if _db:
    _db.close()
    _f.close()

# ---- Low-level key/value helpers ----

def _keys(prefix):
  p = prefix.encode()
  return [k[len(p):].decode() for k in _db.keys(p, p + b'\xff')]

def _put(key, value):
  _db[key.encode()] = json.dumps(value).encode()
  _db.flush()

def _get(key, default=None):
  try:
    return json.loads(_db[key.encode()])
  except KeyError:
    return default

def _del(key):
  try:
    del _db[key.encode()]
    _db.flush()
  except KeyError:
    pass

# ---- Exercises ----

def exercises():
  return _keys('ex:')

def add_exercise(name, description='', weight=False, reps=False, sets=False):
  if _get('ex:' + name) is None:
    _put('ex:' + name, {'description': description, 'weight': weight, 'reps': reps, 'sets': sets})
    return True
  return False

def exercise_info(name):
  """Exercise settings; anything missing (older records) is off, i.e. a plain done checkbox."""
  info = _get('ex:' + name, {})
  if not isinstance(info, dict):
    info = {}
  return {
    'description': info.get('description', ''),
    'weight': bool(info.get('weight')),
    'reps': bool(info.get('reps')),
    'sets': bool(info.get('sets')),
  }

def exercise_description(name):
  return exercise_info(name)['description']

def delete_exercise(name):
  _del('ex:' + name)
  for plan in plans():
    items = plan_items(plan)
    if name in items:
      items.remove(name)
      _put('plan:' + plan, items)

# ---- Plans ----

def plans():
  """Plan names in display order. Plans missing from meta:order go last, alphabetically."""
  names = _keys('plan:')
  order = _get('meta:order', [])
  return [n for n in order if n in names] + [n for n in names if n not in order]

def plan_items(name):
  return _get('plan:' + name, [])

def add_plan(name, position=None):
  """Creates an empty plan at a 0-based display position (default: last)."""
  if _get('plan:' + name) is not None:
    return False
  order = plans()
  if position is None or position > len(order):
    position = len(order)
  order.insert(max(0, position), name)
  _put('plan:' + name, [])
  _put('meta:order', order)
  if current_plan() is None:
    set_current_plan(name)
  return True

def delete_plan(name):
  was_current = current_plan() == name
  _del('plan:' + name)
  _put('meta:order', plans())
  if was_current:
    rest = plans()
    set_current_plan(rest[0] if rest else None)

def toggle_plan_item(plan, exercise):
  items = plan_items(plan)
  if exercise in items:
    items.remove(exercise)
  else:
    items.append(exercise)
  _put('plan:' + plan, items)

# ---- Current plan ----

def current_plan():
  name = _get('meta:current')
  return name if name in plans() else None

def set_current_plan(name):
  _put('meta:current', name)

# ---- Workout logs ----

def get_log(day, exercise):
  log = _get('log:%s:%s' % (day, exercise), {})
  return {'done': bool(log.get('done')), 'sets': log.get('sets', [])}

def set_log(day, exercise, log):
  _put('log:%s:%s' % (day, exercise), log)

def is_logged(day, exercise):
  """True once the exercise has a checked 'done' box or at least one logged set."""
  info = exercise_info(exercise)
  log = get_log(day, exercise)
  if info['weight'] or info['reps'] or info['sets']:
    return bool(log['sets'])
  return log['done']
