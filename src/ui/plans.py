import db
import ui.nav as nav
from ui.base import *

def add_plan(name):
  if name and db.add_plan(name):
    nav.go('plan_edit', name)

class PlanList(ListScreen):
  title = 'Plans'
  footer = '(n)ew (d)elete (s)et (ok)edit'

  def rows(self):
    cur = db.current_plan()
    return [('* ' if p == cur else '') + p for p in db.plans()]

  def on_key(self, k):
    if super().on_key(k):
      return
    n = self.count()
    if k in KEY_ESC:
      nav.go('main')
    elif k == ord('n'):
      nav.go('text', 'New plan', add_plan, 'plans')
    elif n and k == ord('d'):
      db.delete_plan(db.plans()[self.cursor])
      self.move_after_delete(n)
    elif n and k == ord('s'):
      db.set_current_plan(db.plans()[self.cursor])
      self.dirty = True
    elif n and k in KEY_ENTER:
      nav.go('plan_edit', db.plans()[self.cursor])
