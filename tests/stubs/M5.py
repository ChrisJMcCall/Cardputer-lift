# Stand-in for the UIFlow2 M5 module: drawing calls are accepted and recorded.
class _Recorder:
  def __init__(self):
    self.calls = []

  def width(self):
    return 240

  def height(self):
    return 135

  def __getattr__(self, name):
    def record(*args):
      self.calls.append((name, args))
    return record

Display = _Recorder()
Lcd = _Recorder()

def begin():
  pass

def update():
  pass
