from hardware import MatrixKeyboard
from hardware import RGB

kb = None
rgb21 = None
fnIndicatorOn = False
ctrlWasDown = False
ctrlPressedEvent = False

def setFnIndicator(setOn):
  global fnIndicatorOn

  if fnIndicatorOn != setOn:
    if setOn:
      rgb21.set_brightness(10)
      rgb21.fill_color(0xff6600)
      rgb21.set_color(0, 0xff6600)
    else:
      rgb21.set_brightness(0)

    fnIndicatorOn = setOn

def kb_pressed_event(kb_0):
  pass

def ctrl_pressed():
  """True once per ctrl press (a bare modifier produces no key code)."""
  global ctrlPressedEvent

  pressed, ctrlPressedEvent = ctrlPressedEvent, False
  return pressed

def tick():
  global ctrlWasDown, ctrlPressedEvent

  kb.tick()
  state = kb._keyboard.keys_state()
  ctrlDown = state.ctrl
  if ctrlDown and not ctrlWasDown:
    ctrlPressedEvent = True
  ctrlWasDown = ctrlDown
  fnKey = state.fn

  if fnKey:
    setFnIndicator(True)
  elif not fnKey and fnIndicatorOn:
    setFnIndicator(False)

def setup():
  global kb, rgb21

  kb = MatrixKeyboard()
  rgb21 = RGB(io=21, n=1, type="SK6812")
  kb.set_callback(kb_pressed_event)
