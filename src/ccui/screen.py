# A screen owns a retained view tree, its focus, and its commands.
import M5
from ccui.menu import CommandMenu
from ccui.theme import *


class Screen:
  """Subclass and implement build(). Set `commands` to [(key, label, action)] in build(): each key
  runs its action, and ctrl lists them in a popup. ESC pops by default."""
  title = ''

  def __init__(self):
    self.nav = None
    self.root = None
    self.commands = []
    self.menu = None
    self.order = []
    self.focus = -1
    self.chrome_dirty = True

  def build(self):
    """Returns the root view. Called once, when the screen is pushed."""
    return None

  def mount(self, nav):
    self.nav = nav
    self.root = self.build()
    top = HEADER_H if self.title else 0
    if self.root:
      self.root.place(PAD, top + 2, M5.Display.width() - 2 * PAD, M5.Display.height() - top - 4)
      self.root.focusables(self.order)
    if self.order:
      self.set_focus(0, True)
    self.menu = CommandMenu(self.commands)

  def set_focus(self, i, editing=False):
    if 0 <= self.focus < len(self.order):
      self.order[self.focus].set_focus(False)
    self.focus = i
    self.order[i].set_focus(True, editing)

  def on_key(self, k):
    if self.menu.open:
      action = self.menu.on_key(k)
      if not self.menu.open:
        self.chrome_dirty = True  # repaint what the popup covered
      if action:
        action()
      return
    if k == KEY_MENU:
      if self.commands:
        self.menu.show()
      return
    if self.order and self.order[self.focus].on_key(k):
      return
    if k in (KEY_UP, KEY_DOWN, KEY_TAB, KEY_BACKTAB) and self.order:
      self.set_focus((self.focus + (1 if k in (KEY_DOWN, KEY_TAB) else -1)) % len(self.order))
    elif self.run_command(k):
      pass
    elif k in KEY_ENTER and self.order and self.focus + 1 < len(self.order):
      self.set_focus(self.focus + 1, True)  # form flow: Enter moves on ready to type
    elif k in KEY_ESC:
      self.nav.pop()

  def run_command(self, k):
    for c in self.commands:
      if c[0] == k:
        c[2]()
        return True
    return False

  def tick(self):
    pass

  def render(self):
    if self.chrome_dirty:
      self.chrome_dirty = False
      M5.Display.fillRect(0, 0, M5.Display.width(), M5.Display.height(), COLOR_BG)
      if self.title:
        M5.Display.fillRect(0, 0, M5.Display.width(), HEADER_H, COLOR_TITLE_BG)
        M5.Lcd.setTextColor(COLOR_TITLE_FG, COLOR_TITLE_BG)
        M5.Lcd.drawString(self.title, PAD, 2)
      if self.root:
        self.root.invalidate()
      if self.menu.open:
        self.menu.dirty = True
    if self.root:
      self.root.draw()
    if self.menu.open:
      self.menu.draw()
