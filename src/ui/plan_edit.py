import db
import ui.nav as nav
from ui.base import *

class PlanEdit(ListScreen):
  footer = '(ok)toggle'

  def __init__(self, plan):
    ListScreen.__init__(self)
    self.plan = plan
    self.title = 'Plan: ' + plan

  def rows(self):
    items = db.plan_items(self.plan)
    return [('[x] ' if e in items else '[ ] ') + e for e in db.exercises()]

  def on_key(self, k):
    if super().on_key(k):
      return
    if k in KEY_ESC:
      nav.go('plans')
    elif k in KEY_ENTER and self.count():
      db.toggle_plan_item(self.plan, db.exercises()[self.cursor])
      self.dirty = True
