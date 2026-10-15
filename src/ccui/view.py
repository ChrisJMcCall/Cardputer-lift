# Retained views: built once, laid out once, redrawn in place when invalidated.
import M5
from ccui.state import as_state
from ccui.theme import *


class View:
  focusable = False
  flex = 0  # share of leftover space in a stack; 0 = natural size

  def __init__(self):
    self.x = self.y = self.w = self.h = 0
    self.dirty = True
    self.focused = False

  def measure(self, w, h):
    """Natural (width, height) given the space on offer."""
    return w, LINE_H

  def place(self, x, y, w, h):
    self.x, self.y, self.w, self.h = x, y, w, h
    self.dirty = True

  def invalidate(self):
    self.dirty = True

  def set_focus(self, on, editing=False):
    """`editing` asks text-entry views to start typing straight away."""
    self.focused = on
    self.dirty = True

  def focusables(self, out):
    if self.focusable:
      out.append(self)

  def on_key(self, k):
    """Returns True if the key was handled."""
    return False

  def clear(self):
    M5.Display.fillRect(self.x, self.y, self.w, self.h, COLOR_BG)

  def draw(self, force=False):
    if self.dirty or force:
      self.dirty = False
      self.clear()
      self.paint()

  def paint(self):
    pass


class Text(View):
  """Label bound to a State (or a fixed string)."""

  def __init__(self, text='', color=WHITE):
    View.__init__(self)
    self.text = as_state(text).bind(self)
    self.color = color

  def paint(self):
    M5.Lcd.setTextColor(self.color, COLOR_BG)
    M5.Lcd.drawString(str(self.text.value), self.x, self.y)


class Checkbox(View):
  focusable = True

  def __init__(self, label, checked=False, on_change=None):
    View.__init__(self)
    self.label = label
    self.checked = as_state(checked).bind(self)
    self.on_change = on_change

  def on_key(self, k):
    if k in KEY_ENTER or k == 32:
      self.checked.value = not self.checked.value
      if self.on_change:
        self.on_change(self.checked.value)
      return True
    return False

  def paint(self):
    M5.Lcd.setTextColor(YELLOW if self.focused else WHITE, COLOR_BG)
    M5.Lcd.drawString('%s %s' % ('[x]' if self.checked.value else '[ ]', self.label), self.x, self.y)


class TextField(View):
  """Typing needs editing mode: Enter-advance or Enter starts it, ESC stops it. Tab, arrows and ESC navigate only when not editing (arrows always)."""
  focusable = True

  def __init__(self, label='', text='', max_len=24, on_submit=None):
    View.__init__(self)
    self.label, self.max_len, self.on_submit = label, max_len, on_submit
    self.text = as_state(text).bind(self)
    self.editing = False

  def set_focus(self, on, editing=False):
    self.editing = on and editing
    View.set_focus(self, on)

  def on_key(self, k):
    t = self.text.value
    if not self.editing:
      if k in KEY_ENTER:
        self.editing, self.dirty = True, True
        return True
      return False
    if k in KEY_ESC:
      self.editing, self.dirty = False, True
      return True
    if k in KEY_ENTER:
      if self.on_submit:
        self.on_submit(t)
        return True
      return False  # let the screen advance focus / submit
    if k in KEY_BACK:
      self.text.value = t[:-1]
    elif 32 <= k < 127 and len(t) < self.max_len:
      self.text.value = t + chr(k)
    elif k in (KEY_TAB, KEY_BACKTAB):
      pass  # tab only navigates when not editing
    elif not 32 <= k < 127:
      return False  # arrows (fn held) and other non-text keys still navigate
    return True

  def paint(self):
    prefix = self.label + ': ' if self.label else ''
    shown = self.text.value[-max(0, 18 - len(prefix)):]
    M5.Lcd.setTextColor(YELLOW if self.focused else WHITE, COLOR_BG)
    M5.Lcd.drawString(prefix + shown + ('_' if self.editing else ''), self.x, self.y)


class Spacer(View):
  flex = 1

  def measure(self, w, h):
    return 0, 0


class ListView(View):
  """Scrolling list with a cursor. `rows` is called on reload() and returns strings."""
  focusable = True
  flex = 1

  def __init__(self, rows, on_select=None):
    View.__init__(self)
    self.rows_fn, self.on_select = rows, on_select
    self.rows = []
    self.cursor = 0
    self.reload()

  def measure(self, w, h):
    return w, h

  def reload(self):
    self.rows = self.rows_fn()
    self.cursor = max(0, min(self.cursor, len(self.rows) - 1))
    self.dirty = True

  def visible(self):
    return max(1, self.h // LINE_H)

  def on_key(self, k):
    n = len(self.rows)
    if k == KEY_UP and n:
      self.cursor = (self.cursor - 1) % n
    elif k == KEY_DOWN and n:
      self.cursor = (self.cursor + 1) % n
    elif k in KEY_ENTER and n and self.on_select:
      self.on_select(self.cursor)
      return True
    else:
      return False
    self.dirty = True
    return True

  def paint(self):
    if not self.rows:
      M5.Lcd.setTextColor(GRAY, COLOR_BG)
      M5.Lcd.drawString('(empty)', self.x, self.y)
      return
    size = self.visible()
    first = max(0, self.cursor - size + 1)
    for i, row in enumerate(self.rows[first:first + size]):
      sel = first + i == self.cursor
      M5.Lcd.setTextColor(BLACK if sel else WHITE, WHITE if sel else COLOR_BG)
      M5.Lcd.drawString(' ' + row + ' ' * 20, self.x, self.y + i * LINE_H)


class Stack(View):
  """Lays children along an axis. Fixed children take their natural size; flex children split the rest."""
  vertical = True

  def __init__(self, *children, spacing=0, pad=0):
    View.__init__(self)
    self.children, self.spacing, self.pad = children, spacing, pad

  def _sizes(self, w, h):
    main = h if self.vertical else w
    sizes, flex_total, used = [], 0, self.spacing * max(0, len(self.children) - 1)
    for c in self.children:
      cw, ch = c.measure(w, h)
      size = ch if self.vertical else cw
      if c.flex:
        flex_total += c.flex
        size = 0
      used += size
      sizes.append(size)
    free = max(0, main - used)
    for i, c in enumerate(self.children):
      if c.flex:
        sizes[i] = free * c.flex // flex_total
    return sizes

  def measure(self, w, h):
    return w, h if any(c.flex for c in self.children) else sum(self._sizes(w, h)) + self.spacing * max(0, len(self.children) - 1)

  def place(self, x, y, w, h):
    View.place(self, x, y, w, h)
    x, y, w, h = x + self.pad, y + self.pad, w - 2 * self.pad, h - 2 * self.pad
    pos = y if self.vertical else x
    for c, size in zip(self.children, self._sizes(w, h)):
      if self.vertical:
        c.place(x, pos, w, size)
      else:
        c.place(pos, y, size, h)
      pos += size + self.spacing

  def invalidate(self):
    for c in self.children:
      c.invalidate()

  def focusables(self, out):
    for c in self.children:
      c.focusables(out)

  def draw(self, force=False):
    force = force or self.dirty
    self.dirty = False
    for c in self.children:
      c.draw(force)


class VStack(Stack):
  vertical = True


class HStack(Stack):
  vertical = False
