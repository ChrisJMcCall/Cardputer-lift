from hardware import MatrixKeyboard
from unit import KeyCode
from hardware import RGB

kb = None
rgb21 = None
fnIndicatorOn = False

def setFnIndicator(setOn):
  global fnIndicatorOn

  if fnIndicatorOn != setOn:
    if setOn:
      print('set on')
      rgb21.set_brightness(50)
      rgb21.fill_color(0xff6600)
      rgb21.set_color(0, 0xff6600)
    else:
      print('set off')
      rgb21.set_brightness(0)

    fnIndicatorOn = setOn

def kb_pressed_event(kb_0):
  pass

def tick():
  kb.tick()
  fnKey = kb._keyboard.keys_state().fn

  if fnKey:
    setFnIndicator(True)
  elif fnKey == False and fnIndicatorOn == True:
    setFnIndicator(False)

def setup():
  global kb, rgb21

  kb = MatrixKeyboard()
  print('kb set up')
  rgb21 = RGB(io=21, n=1, type="SK6812")
  kb.set_callback(kb_pressed_event)
