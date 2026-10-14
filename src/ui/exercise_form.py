import M5
from M5 import *
import db
import ui.nav as nav
from ui.base import *

class ExerciseForm(Screen):
  title = 'New Exercise'
  footer = '(ok)Next/Save'

  def __init__(self):
    Screen.__init__(self)
    # [label, value, max length]
    self.fields = [['Name', '', 24], ['Description', '', 60]]
    self.idx = 0

  def draw(self):
    super().draw()

    for i, (label, value, _) in enumerate(self.fields):
      sel = (i == self.idx)
      M5.Lcd.setTextColor(YELLOW if sel else GRAY, BLACK)
      M5.Lcd.drawString(label + ':', 4, 24 + i * 40)
      M5.Lcd.setTextColor(WHITE, BLACK)
      M5.Lcd.drawString(value[-18:] + ('_' if sel else ' ') + ' ' * 4, 4, 42 + i * 40)

  def on_key(self, k):
    field = self.fields[self.idx]
    if k in KEY_ENTER:
      if self.idx < len(self.fields) - 1:
        self.idx += 1
      elif self.fields[0][1].strip():
        db.add_exercise(self.fields[0][1].strip(), self.fields[1][1].strip())
        nav.go('exercises')
        return
      else:
        self.idx = 0
      self.dirty = True
    elif k in KEY_ESC:
      nav.go('exercises')
    elif k in KEY_BACK:
      field[1] = field[1][:-1]
      self.dirty = True
    elif 32 <= k < 127 and len(field[1]) < field[2]:
      field[1] += chr(k)
      self.dirty = True
