# Navigation stack and main-loop glue between the keyboard and the top screen.
class Navigator:
  def __init__(self, kb=None, on_exit=None):
    self.kb = kb
    self.on_exit = on_exit  # called when ESC pops the last screen
    self.stack = []

  @property
  def top(self):
    return self.stack[-1] if self.stack else None

  def push(self, screen):
    self.stack.append(screen)
    screen.mount(self)

  def pop(self):
    """Returns to the previous screen (redrawn). The last screen stays unless on_exit is set."""
    if len(self.stack) > 1:
      self.stack.pop()
      self.top.chrome_dirty = True
    elif self.on_exit:
      self.on_exit()

  def replace(self, screen):
    if self.stack:
      self.stack.pop()
    self.push(screen)

  def root(self, screen):
    del self.stack[:]
    self.push(screen)

  def tick(self):
    if self.kb.is_pressed():
      self.top.on_key(self.kb.get_key())
    self.top.tick()
    self.top.render()
