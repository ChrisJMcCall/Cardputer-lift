import M5
from M5 import *
from unit import KeyCode

# Cardputer key codes; arrows are the ; . , / keys
KEY_ENTER = (13, 10)
KEY_BACK = (8, 127)
KEY_ESC = (27, 96)
KEY_UP = KeyCode.KEYCODE_UP
KEY_DOWN = KeyCode.KEYCODE_DOWN
KEY_RIGHT = KeyCode.KEYCODE_RIGHT
KEY_LEFT = KeyCode.KEYCODE_LEFT

# ---- Theme ----
WHITE = 0xFFFFFF
GRAY = 0x808080
YELLOW = 0xFFCC00
BLACK = 0x000000
COLOR_TITLE_BG = 0x3366ff
COLOR_TITLE_FG = 0xFFFFFF 

def draw_footer(text):
  M5.Lcd.setTextColor(GRAY, BLACK)
  M5.Lcd.drawString(text, 4, 118)

def draw_row(text, selected, y):
  M5.Lcd.setTextColor(BLACK if selected else WHITE, WHITE if selected else BLACK)
  M5.Lcd.drawString((' ' if selected else ' ') + text + ' ' * 20, 4, y)

class Screen:
  """A screen draws itself when dirty and reacts to key presses."""
  def __init__(self):
    self.dirty = True

  def draw(self):
    pass

  def on_key(self, k):
    pass

  def tick(self):
    pass

class ListScreen(Screen):
  """A screen with a cursor moved by the up/down keys."""
  title = ''
  footer = ''

  def __init__(self):
    Screen.__init__(self)
    self.cursor = 0

  def rows(self):
    return []

  def count(self):
    return len(self.rows())

  def move_after_delete(self, n):
    self.cursor = max(0, min(self.cursor, n - 2))
    self.dirty = True

  def draw(self):
    M5.Display.fillRect(0, 0, 240, 160, 0x000000)
    M5.Lcd.setTextColor(COLOR_TITLE_FG, COLOR_TITLE_BG)
    M5.Lcd.drawString(self.title, 4, 2)
    rows = self.rows()
    first = max(0, self.cursor - 4)
    for i, row in enumerate(rows[first:first + 5]):
      draw_row(row, first + i == self.cursor, 20 + i * 18)
    if not rows:
      M5.Lcd.setTextColor(GRAY, BLACK)
      M5.Lcd.drawString('(empty)', 4, 20)
    draw_footer(self.footer)

  def on_key(self, k):
    """Moves the cursor. Returns True if the key was a movement key."""
    n = self.count()
    if k == KEY_UP and n:
      self.cursor, self.dirty = (self.cursor - 1) % n, True
      return True
    if k == KEY_DOWN and n:
      self.cursor, self.dirty = (self.cursor + 1) % n, True
      return True
    return False
