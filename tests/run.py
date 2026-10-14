# Runs every tests/test_*.py on the MicroPython unix port: micropython tests/run.py
# Device-only modules come from tests/stubs, app code from src, unittest from tests/lib.
import os
import sys

sys.path[:0] = ['tests/stubs', 'tests', 'src', 'tests/lib']

import unittest  # noqa: E402

names = sorted(f[:-3] for f in os.listdir('tests') if f.startswith('test_') and f.endswith('.py'))
failed = False
for name in names:
  print('==', name)
  if not unittest.main(name).wasSuccessful():
    failed = True
sys.exit(1 if failed else 0)
