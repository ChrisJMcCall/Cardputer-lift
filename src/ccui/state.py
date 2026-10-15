# Observable value. Setting a different value invalidates the views bound to it.
class State:
  def __init__(self, value=None):
    self._value = value
    self.views = []

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, v):
    if v != self._value:
      self._value = v
      for view in self.views:
        view.invalidate()

  def bind(self, view):
    self.views.append(view)
    return self


def as_state(v):
  """Wraps a plain value in a State; States pass through."""
  return v if isinstance(v, State) else State(v)
