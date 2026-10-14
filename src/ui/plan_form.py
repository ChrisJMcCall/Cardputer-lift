import M5
from M5 import *
import db
import ui.nav as nav
from ui.base import *

class PlanForm(Screen):
  title = 'New Plan'
  footer = '(ok)Next/Save'

  def __init__(self):
    Screen.__init__(self)
    # [label, value, max length, digits only]
    self.fields = [
      ['Name', '', 24, False],
      ['Order (1-%d)' % (len(db.plans()) + 1), str(len(db.plans()) + 1), 2, True],
    ]
    self.idx = 0

  def draw(self):
    super().draw()

    for i, (label, value, _, _) in enumerate(self.fields):
      sel = (i == self.idx)
      M5.Lcd.setTextColor(YELLOW if sel else GRAY, BLACK)
      M5.Lcd.drawString(label + ':', 4, 24 + i * 40)
      M5.Lcd.setTextColor(WHITE, BLACK)
      M5.Lcd.drawString(value[-18:] + ('_' if sel else ' ') + ' ' * 4, 4, 42 + i * 40)

  def save(self):
    name = self.fields[0][1].strip()
    order = self.fields[1][1]
    position = int(order) - 1 if order else None
    if name and db.add_plan(name, position):
      nav.go('plan_edit', name)  # pick the plan's exercises
    else:
      self.idx = 0
      self.dirty = True

  def on_key(self, k):
    field = self.fields[self.idx]
    if k in KEY_ENTER:
      if self.idx < len(self.fields) - 1:
        self.idx += 1
        self.dirty = True
      else:
        self.save()
    elif k in KEY_ESC:
      nav.go('plans')
    elif k in KEY_BACK:
      field[1] = field[1][:-1]
      self.dirty = True
    elif 32 <= k < 127 and len(field[1]) < field[2] and (not field[3] or 48 <= k <= 57):
      field[1] += chr(k)
      self.dirty = True
