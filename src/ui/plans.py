import db
import ui.nav as nav
from ccui.screen import Screen
from ccui.view import ListView

class PlanList(Screen):
  title = 'Plans'

  def build(self):
    self.list = ListView(self.rows, lambda i: nav.go('plan_edit', db.plans()[i]))
    self.commands = [
      (ord('n'), 'New', lambda: nav.go('plan_form')),
      (ord('d'), 'Delete', self.delete),
      (ord('s'), 'Set current', self.set_current),
    ]
    return self.list

  def rows(self):
    cur = db.current_plan()
    return [('* ' if p == cur else '') + p for p in db.plans()]

  def delete(self):
    if self.list.rows:
      db.delete_plan(db.plans()[self.list.cursor])
      self.list.reload()

  def set_current(self):
    if self.list.rows:
      db.set_current_plan(db.plans()[self.list.cursor])
      self.list.reload()
