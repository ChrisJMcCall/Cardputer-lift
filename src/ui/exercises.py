import db
import ui.nav as nav
from ui.base import *

class ExerciseList(ListScreen):
  title = 'Exercises'
  footer = '(n)ew  (d)elete'

  def rows(self):
    return db.exercises()

  def on_key(self, k):
    if super().on_key(k):
      return
    n = self.count()
    if k in KEY_ESC:
      nav.go('main')
    elif k == ord('n'):
      nav.go('exercise_form')
    elif k == ord('d') and n:
      db.delete_exercise(db.exercises()[self.cursor])
      self.move_after_delete(n)
