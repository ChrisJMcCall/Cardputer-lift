import M5
from M5 import *
import ui.nav as nav
from ui.base import *

class TextInput(Screen):
  """Single-line prompt. On Enter, goes to `back` then calls done(text)."""
  footer = '(ok)done'

  def __init__(self, prompt, done, back):
    Screen.__init__(self)
    self.prompt, self.done, self.back = prompt, done, back
    self.title = self.prompt
    self.buf = ''

  def draw(self):
    super().draw()

    M5.Lcd.setTextColor(WHITE, BLACK)
    M5.Lcd.drawString(self.buf + '_', 4, 40)

  def on_key(self, k):
    if k in KEY_ENTER:
      done, text = self.done, self.buf.strip()
      nav.go(self.back)
      done(text)
    elif k in KEY_ESC:
      nav.go(self.back)
    elif k in KEY_BACK:
      self.buf = self.buf[:-1]
      self.dirty = True
    elif 32 <= k < 127 and len(self.buf) < 24:
      self.buf += chr(k)
      self.dirty = True
