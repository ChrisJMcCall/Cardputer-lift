import M5
from M5 import *
import time
import date_time
import db

# Cardputer key codes; arrows are the ; . , / keys
KEY_ENTER = (13, 10)
KEY_BACK = (8, 127)
KEY_ESC = (27, 96)
KEY_UP = 59
KEY_DOWN = 46

WHITE = 0xFFFFFF
GRAY = 0x808080
YELLOW = 0xFFCC00
BLACK = 0x000000

kb = None
screen = 'menu'
cursor = 0
dirty = True
text_buf = ''
text_prompt = ''
text_done = None
edit_plan = None
last_clock = ''

def clock_strings():
  t = date_time.now()
  if t[0] < 2024:
    return '--- -/-/-', '--:--'
  return '%s %04d-%02d-%02d' % (date_time.DAYS[t[6]], t[0], t[1], t[2]), '%02d:%02d' % (t[3], t[4])

def go(name, pos=0):
  global screen, cursor, dirty
  screen, cursor, dirty = name, pos, True

def ask_text(prompt, done):
  global text_buf, text_prompt, text_done
  text_buf, text_prompt, text_done = '', prompt, done
  go('text')

def draw_list(title, rows, footer):
  Widgets.fillScreen(BLACK)
  M5.Lcd.setTextColor(YELLOW, BLACK)
  M5.Lcd.drawString(title, 4, 2)
  first = max(0, cursor - 4)
  for i, row in enumerate(rows[first:first + 5]):
    sel = (first + i == cursor)
    M5.Lcd.setTextColor(BLACK if sel else WHITE, WHITE if sel else BLACK)
    M5.Lcd.drawString(('> ' if sel else '  ') + row + ' ' * 20, 4, 20 + i * 18)
  if not rows:
    M5.Lcd.setTextColor(GRAY, BLACK)
    M5.Lcd.drawString('(empty)', 4, 20)
  M5.Lcd.setTextColor(GRAY, BLACK)
  M5.Lcd.drawString(footer, 4, 118)

def draw_menu():
  Widgets.fillScreen(BLACK)
  date_s, time_s = clock_strings()
  M5.Lcd.setTextColor(WHITE, BLACK)
  M5.Lcd.drawString(date_s, 4, 4)
  M5.Lcd.drawString(time_s, 170, 4)
  M5.Lcd.drawLine(0, 24, 240, 24, GRAY)
  rows = ['Start: ' + (db.current_plan() or 'none'), 'Plans', 'Exercises']
  for i, row in enumerate(rows):
    sel = (i == cursor)
    M5.Lcd.setTextColor(BLACK if sel else WHITE, WHITE if sel else BLACK)
    M5.Lcd.drawString(('> ' if sel else '  ') + row + ' ' * 20, 4, 34 + i * 22 + (12 if i else 0))
  M5.Lcd.setTextColor(GRAY, BLACK)
  M5.Lcd.drawString(';/. move  Enter select', 4, 118)

def draw():
  global dirty
  dirty = False
  if screen == 'menu':
    draw_menu()
  elif screen == 'exercises':
    draw_list('Exercises', db.exercises(), 'n new  d delete  Esc back')
  elif screen == 'plans':
    cur = db.current_plan()
    draw_list('Plans', [('* ' if p == cur else '') + p for p in db.plans()],
              'n new d del s set Ent edit')
  elif screen == 'plan_edit':
    items = db.plan_items(edit_plan)
    rows = [('[x] ' if e in items else '[ ] ') + e for e in db.exercises()]
    draw_list('Plan: ' + edit_plan, rows, 'Enter toggle  Esc back')
  elif screen == 'text':
    Widgets.fillScreen(BLACK)
    M5.Lcd.setTextColor(YELLOW, BLACK)
    M5.Lcd.drawString(text_prompt, 4, 4)
    M5.Lcd.setTextColor(WHITE, BLACK)
    M5.Lcd.drawString(text_buf + '_', 4, 40)
    M5.Lcd.setTextColor(GRAY, BLACK)
    M5.Lcd.drawString('Enter ok  Esc cancel', 4, 118)

def list_len():
  if screen == 'menu':
    return 3
  if screen in ('exercises', 'plan_edit'):
    return len(db.exercises())
  if screen == 'plans':
    return len(db.plans())
  return 0

def add_exercise(name):
  if name:
    db.add_exercise(name)

def add_plan(name):
  global edit_plan
  if name and db.add_plan(name):
    edit_plan = name
    go('plan_edit')

def handle_text(k):
  global text_buf, dirty
  if k in KEY_ENTER:
    done = text_done
    text = text_buf.strip()
    go('exercises' if done is add_exercise else 'plans')
    done(text)
  elif k in KEY_ESC:
    go('exercises' if text_done is add_exercise else 'plans')
  elif k in KEY_BACK:
    text_buf = text_buf[:-1]
    dirty = True
  elif 32 <= k < 127 and len(text_buf) < 24:
    text_buf += chr(k)
    dirty = True

def handle_key(k):
  global cursor, dirty, edit_plan
  if screen == 'text':
    handle_text(k)
    return
  n = list_len()
  if k == KEY_UP and n:
    cursor, dirty = (cursor - 1) % n, True
  elif k == KEY_DOWN and n:
    cursor, dirty = (cursor + 1) % n, True
  elif k in KEY_ESC and screen != 'menu':
    go('plans' if screen == 'plan_edit' else 'menu', 0)
  elif screen == 'menu' and k in KEY_ENTER:
    if cursor == 1:
      go('plans')
    elif cursor == 2:
      go('exercises')
    # cursor 0 (Start) is a placeholder until workout sessions exist
  elif screen == 'exercises':
    if k == ord('n'):
      ask_text('New exercise', add_exercise)
    elif k == ord('d') and n:
      db.delete_exercise(db.exercises()[cursor])
      cursor = max(0, min(cursor, n - 2))
      dirty = True
  elif screen == 'plans':
    if k == ord('n'):
      ask_text('New plan', add_plan)
    elif n and k == ord('d'):
      db.delete_plan(db.plans()[cursor])
      cursor = max(0, min(cursor, n - 2))
      dirty = True
    elif n and k == ord('s'):
      db.set_current_plan(db.plans()[cursor])
      dirty = True
    elif n and k in KEY_ENTER:
      edit_plan = db.plans()[cursor]
      go('plan_edit')
  elif screen == 'plan_edit' and k in KEY_ENTER and n:
    db.toggle_plan_item(edit_plan, db.exercises()[cursor])
    dirty = True

def start():
  global kb
  from hardware import MatrixKeyboard
  kb = MatrixKeyboard()
  db.open_db()

def tick():
  global dirty, last_clock
  kb.tick()
  if kb.is_pressed():
    handle_key(kb.get_key())
  if screen == 'menu':
    t = clock_strings()[1]
    if t != last_clock:
      last_clock, dirty = t, True
  if dirty:
    draw()
