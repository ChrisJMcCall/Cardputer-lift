import db
import date_time
import ui.nav as nav
from ui.base import *

class ExerciseLog(ListScreen):
  """Logs one exercise for today.

  No weight/reps/sets enabled: a 'Done' checkbox.
  Sets enabled: one row per set plus an 'Add set' row.
  Otherwise: a single entry. Entry values are [weight, reps] strings ('' when unused).
  """

  def __init__(self, plan, exercise):
    ListScreen.__init__(self)
    self.plan, self.exercise = plan, exercise
    self.title = exercise
    self.day = date_time.today()
    info = db.exercise_info(exercise)
    self.has_sets = info['sets']
    self.fields = [i for i, key in enumerate(('weight', 'reps')) if info[key]]
    self.simple = not (self.fields or self.has_sets)
    log = db.get_log(self.day, exercise)
    self.done = log['done']
    self.entries = log['sets']
    if not self.has_sets and not self.simple and not self.entries:
      self.entries = [['', '']]
    self.edit = None  # [index into self.fields, text buffer] while typing
    self.edit_new = False
    self.footer = '(ok)toggle' if self.simple else ('(ok)edit (d)elete' if self.has_sets else '(ok)edit')

  def entry_text(self, n):
    entry = self.entries[n]
    parts = []
    for i in self.fields:
      v = entry[i]
      if self.edit and n == self.cursor and self.fields[self.edit[0]] == i:
        v = self.edit[1] + '_'
      v = v or '-'
      parts.append(v if i == 0 else v + ' reps')
    text = ' x '.join(parts)
    if self.has_sets:
      text = 'Set %d%s' % (n + 1, ': ' + text if text else '')
    return text

  def rows(self):
    if self.simple:
      return ['[x] Done' if self.done else '[ ] Done']
    rows = [self.entry_text(n) for n in range(len(self.entries))]
    if self.has_sets:
      rows.append('+ Add set')
    return rows

  def save(self):
    db.set_log(self.day, self.exercise, {'done': self.done, 'sets': self.entries})

  def start_edit(self):
    if self.fields:
      self.edit = [0, self.entries[self.cursor][self.fields[0]]]
    else:
      self.save()  # sets only: nothing to type
    self.dirty = True

  def edit_key(self, k):
    field = self.fields[self.edit[0]]
    buf = self.edit[1]
    if k in KEY_ENTER:
      self.entries[self.cursor][field] = buf
      if self.edit[0] + 1 < len(self.fields):
        self.edit = [self.edit[0] + 1, self.entries[self.cursor][self.fields[self.edit[0] + 1]]]
      else:
        self.edit = None
        self.edit_new = False
        self.save()
    elif k in KEY_ESC:
      if self.edit_new:
        del self.entries[self.cursor]
        self.cursor = max(0, self.cursor - 1)
      self.edit, self.edit_new = None, False
    elif k in KEY_BACK:
      self.edit[1] = buf[:-1]
    elif 48 <= k <= 57 and len(buf) < 6:
      self.edit[1] = buf + chr(k)
    elif k == 46 and field == 0 and '.' not in buf and len(buf) < 6:  # decimal point, weight only
      self.edit[1] = buf + '.'
    self.dirty = True

  def on_key(self, k):
    if self.edit:
      self.edit_key(k)
      return
    if super().on_key(k):
      return
    if k in KEY_ESC:
      nav.go('session', self.plan)
    elif self.simple:
      if k in KEY_ENTER:
        self.done = not self.done
        self.save()
        self.dirty = True
    elif k in KEY_ENTER:
      if self.cursor == len(self.entries):  # 'Add set' row: copy the previous set
        self.entries.append(list(self.entries[-1]) if self.entries else ['', ''])
        self.edit_new = True
      self.start_edit()
    elif k == ord('d') and self.has_sets and self.cursor < len(self.entries):
      del self.entries[self.cursor]
      self.save()
      self.dirty = True
