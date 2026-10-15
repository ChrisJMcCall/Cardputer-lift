"""Compiles src/ to MicroPython bytecode (.mpy) in build/.

Run with: uv run util/build.py
Entry points (run.py, lift.py) stay as .py so the firmware can launch them.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
OUT = ROOT / 'build'
KEEP_AS_PY = {'run.py'}


def main():
  if OUT.exists():
    shutil.rmtree(OUT)
  failed = False
  for path in sorted(SRC.rglob('*.py')):
    rel = path.relative_to(SRC)
    dest = OUT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if rel.as_posix() in KEEP_AS_PY:
      shutil.copy(path, dest)
      continue
    result = subprocess.run(
      [sys.executable, '-m', 'mpy_cross', '-o', str(dest.with_suffix('.mpy')), str(path)],
      capture_output=True, text=True,
    )
    if result.returncode:
      failed = True
      print(f'{rel}: {result.stderr.strip() or result.stdout.strip()}')
    else:
      print(f'compiled {rel}')
  sys.exit(1 if failed else 0)


if __name__ == '__main__':
  main()
