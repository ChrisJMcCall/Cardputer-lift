import os, sys, io
import M5
from M5 import *
import time
import date_time
import menu

def setup():
  M5.begin()
  Widgets.fillScreen(0x000000)
  M5.Lcd.setTextColor(0xFFFFFF, 0x000000)
  M5.Lcd.drawString('Syncing time...', 4, 4)
  if date_time.sync_time():
    print('time synced:', date_time.now())
  menu.start()

def loop():
  M5.update()
  menu.tick()
  time.sleep_ms(20)

if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    sys.print_exception(e)
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
