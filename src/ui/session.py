import db
import date_time
import ui.nav as nav
from ui.base import *

class Session(ListScreen):
  """Today's exercises for a plan, with a checkbox for the ones already logged."""
  footer = '(ok)open'

  def __init__(self, plan):
    ListScreen.__init__(self)
    self.plan = plan
    self.title = plan
    self.day = date_time.today()

  def rows(self):
    return [('[x] ' if db.is_logged(self.day, e) else '[ ] ') + e for e in db.plan_items(self.plan)]

  def on_key(self, k):
    if super().on_key(k):
      return
    if k in KEY_ESC:
      nav.go('main')
    elif k in KEY_ENTER and self.count():
      nav.go('exercise_log', self.plan, db.plan_items(self.plan)[self.cursor])
