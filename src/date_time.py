from M5 import *
import esp32
import network
import ntptime
import time

nvs = esp32.NVS("uiflow")
WIFI_SSID = nvs.get_str("ssid0")
WIFI_PASSWORD = nvs.get_str("pswd0")
WIFI_TIMEOUT_MS = 15000
UTC_OFFSET_HOURS = 6
DAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

def connect_wifi():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    try:
      wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except OSError as e:
      print('wifi connect error:', e)
      return False
    start = time.ticks_ms()
    while not wlan.isconnected():
      if time.ticks_diff(time.ticks_ms(), start) > WIFI_TIMEOUT_MS:
        return False
  return True

def sync_time():
  # ntptime sets the RTC to UTC; use now() for local time
  if not connect_wifi():
    print('wifi connect failed, time not synced')
    return False
  try:
    ntptime.host = "time.google.com"
    ntptime.settime()
  except OSError as e:
    print('ntp sync failed:', e)
    return False
  return True

def now():
  return time.localtime(time.time() + UTC_OFFSET_HOURS * 3600)
