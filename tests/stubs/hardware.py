class _Sdcard:
  def SDCard(self, *args, **kwargs):
    raise OSError('no SD card in tests')

sdcard = _Sdcard()

class MatrixKeyboard:
  pass

class RGB:
  def __init__(self, *args, **kwargs):
    pass
