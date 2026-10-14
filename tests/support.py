# Shared helpers: a throwaway database, a recording stand-in for nav.go and key presses.
import os

import db
import ui.nav as nav

DIR = '/tmp/lift_test'
ENTER, ESC, BACK = 13, 27, 8
UP, DOWN = 59, 46

nav_calls = []


def _remove_db():
  try:
    os.remove(db.DB_PATH)
  except OSError:
    pass


def open_db():
  db._mount_sd = lambda: None
  db.DATA_DIR = DIR
  db.DB_PATH = DIR + '/lift.db'
  _remove_db()
  db.open_db()
  del nav_calls[:]
  nav.go = lambda name, *args: nav_calls.append((name, args))


def close_db():
  db.close_db()
  _remove_db()
  try:
    os.rmdir(DIR)
  except OSError:
    pass


def press(screen, *keys):
  """Sends key codes (ints) or text (each character is a key) to a screen."""
  for k in keys:
    for code in ([ord(c) for c in k] if isinstance(k, str) else [k]):
      screen.on_key(code)
