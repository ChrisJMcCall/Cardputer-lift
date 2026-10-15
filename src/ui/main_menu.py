import M5
from M5 import *
import date_time
import db
import ui.nav as nav
from ui.base import *

def clock_strings():
  t = date_time.now()
  if t[0] < 2024:
    return '--- -/-/-', '--:--'
  return '%s %04d-%02d-%02d' % (date_time.DAYS[t[6]], t[0], t[1], t[2]), '%02d:%02d' % (t[3], t[4])

class MainMenu(ListScreen):
  def __init__(self):
    ListScreen.__init__(self)
    self.last_time = ''

  def rows(self):
    return ['Start: ' + (db.current_plan() or 'none'), 'Plans', 'Exercises']

  def tick(self):
    t = clock_strings()[1]
    if t != self.last_time:
      self.last_time, self.dirty = t, True

  def draw(self):
    if self._needsFullRefresh:
      M5.Display.fillRect(0, 0, M5.Display.width(), M5.Display.height(), COLOR_BG)
      self._needsFullRefresh = False

    self.draw_header()
    self.draw_rows()

  def draw_header(self):
    M5.Display.fillRect(0, 0, M5.Display.width(), 24, COLOR_BG)
    date_s, time_s = clock_strings()
    M5.Lcd.setTextColor(WHITE, BLACK)
    M5.Lcd.drawString(date_s, 4, 4)
    M5.Lcd.drawString(time_s, 170, 4)
    M5.Lcd.drawLine(0, 24, 240, 24, GRAY)

  def draw_rows(self):
    M5.Display.fillRect(0, 25, M5.Display.width(), M5.Display.height()-25, COLOR_BG)
    for i, row in enumerate(self.rows()):
      draw_row(row, i == self.cursor, 34 + i * 22 + (12 if i else 0))

  def on_key(self, k):
    if super().on_key(k):
      return
    if k in KEY_ENTER:
      if self.cursor == 0:
        plan = db.current_plan()
        if plan:
          nav.go('session', plan)
      elif self.cursor == 1:
        nav.go('plans')
      elif self.cursor == 2:
        nav.go('exercises')
