import os
import json
import btree
from hardware import sdcard

# ---- Configuration ----

SD_MOUNT = '/sd'
DB_PATH = SD_MOUNT + '/lift.db'

# Key layout (values are JSON):
#   ex:<name>    -> 1
#   plan:<name>  -> [exercise names in order]
#   meta:current -> current plan name
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

def open_db():
  global _f, _db
  _mount_sd()
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

def add_exercise(name):
  if _get('ex:' + name) is None:
    _put('ex:' + name, 1)

def delete_exercise(name):
  _del('ex:' + name)
  for plan in plans():
    items = plan_items(plan)
    if name in items:
      items.remove(name)
      _put('plan:' + plan, items)

# ---- Plans ----

def plans():
  return _keys('plan:')

def plan_items(name):
  return _get('plan:' + name, [])

def add_plan(name):
  if _get('plan:' + name) is not None:
    return False
  _put('plan:' + name, [])
  if current_plan() is None:
    set_current_plan(name)
  return True

def delete_plan(name):
  _del('plan:' + name)
  if current_plan() == name:
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
