# Colors, sizes and key codes shared by every ccui view.
from unit import KeyCode

# Cardputer key codes; arrows are the ; . , / keys
KEY_ENTER = (13, 10)
KEY_BACK = (8, 127)
KEY_ESC = (27, 96)
KEY_UP = KeyCode.KEYCODE_UP
KEY_DOWN = KeyCode.KEYCODE_DOWN
KEY_LEFT = KeyCode.KEYCODE_LEFT
KEY_RIGHT = KeyCode.KEYCODE_RIGHT
KEY_TAB = 9
KEY_MENU = 1000  # synthetic: sent when ctrl is pressed (a bare modifier has no key code)
KEY_BACKTAB = 353  # fn+tab; UNVERIFIED code, confirm on the device

WHITE = 0xFFFFFF
GRAY = 0x808080
YELLOW = 0xFFCC00
BLACK = 0x000000
COLOR_BG = BLACK
COLOR_TITLE_BG = 0x3366ff
COLOR_TITLE_FG = 0xFFFFFF

HEADER_H = 18
LINE_H = 18
PAD = 4
