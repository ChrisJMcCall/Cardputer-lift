# Popup listing a screen's commands; opened with ctrl.
import M5
from ccui.theme import *


class CommandMenu:
  """commands: list of (key, label, action). Picking one (Enter, or its key) closes the menu and runs it."""

  def __init__(self, commands):
    self.commands = commands
    self.open = False
    self.cursor = 0
    self.dirty = False

  def show(self):
    self.open, self.cursor, self.dirty = True, 0, True

  def on_key(self, k):
    """Returns the action to run, or None. Closes on ESC, ctrl, or a pick."""
    n = len(self.commands)
    if k in KEY_ESC or k == KEY_MENU:
      self.open = False
    elif k == KEY_UP:
      self.cursor, self.dirty = (self.cursor - 1) % n, True
    elif k == KEY_DOWN:
      self.cursor, self.dirty = (self.cursor + 1) % n, True
    else:
      for i, c in enumerate(self.commands):
        if k == c[0] or (k in KEY_ENTER and i == self.cursor):
          self.open = False
          return c[2]
    return None

  def draw(self):
    if not self.dirty:
      return
    self.dirty = False
    w, h = 140, len(self.commands) * LINE_H + 2 * PAD
    x, y = (M5.Display.width() - w) // 2, (M5.Display.height() - h) // 2
    M5.Display.fillRect(x, y, w, h, COLOR_BG)
    M5.Display.drawRect(x, y, w, h, GRAY)
    for i, (key, label, _) in enumerate(self.commands):
      sel = i == self.cursor
      M5.Lcd.setTextColor(BLACK if sel else WHITE, WHITE if sel else COLOR_BG)
      M5.Lcd.drawString(' %s  %s ' % (chr(key), label), x + 2, y + PAD + i * LINE_H)
