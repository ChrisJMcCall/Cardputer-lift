import M5
from M5 import *
import db
import ui.nav as nav
from ui.base import *

class ExerciseForm(Screen):
  title = 'New Exercise'
  footer = '(ok)Next/Save (sp)toggle'

  def __init__(self):
    Screen.__init__(self)
    # [label, value, max length]; a bool value is a toggle, a string is text
    self.fields = [['Name', '', 24], ['Desc', '', 60], ['Weight', False, 0], ['Reps', False, 0], ['Sets', False, 0]]
    self.idx = 0

  def draw(self):
    super().draw()

    for i, (label, value, _) in enumerate(self.fields):
      sel = (i == self.idx)
      if isinstance(value, bool):
        text = '%s: %s' % (label, '[x]' if value else '[ ]')
      else:
        prefix = label + ': '
        text = prefix + value[-(18 - len(prefix)):] + ('_' if sel else '')
      M5.Lcd.setTextColor(YELLOW if sel else WHITE, BLACK)
      M5.Lcd.drawString(text, 4, 22 + i * 18)

  def save(self):
    name = self.fields[0][1].strip()
    if name:
      db.add_exercise(name, self.fields[1][1].strip(), self.fields[2][1], self.fields[3][1], self.fields[4][1])
      nav.go('exercises')
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
      nav.go('exercises')
    elif isinstance(field[1], bool):
      if k == 32:
        field[1] = not field[1]
        self.dirty = True
    elif k in KEY_BACK:
      field[1] = field[1][:-1]
      self.dirty = True
    elif 32 <= k < 127 and len(field[1]) < field[2]:
      field[1] += chr(k)
      self.dirty = True
