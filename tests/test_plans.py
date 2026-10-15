import unittest

import db
import support
from support import DOWN, ENTER, ESC, press
from ui.plans import PlanList
from ccui.nav import Navigator


def open_screen(on_exit=None):
  nav = Navigator(on_exit=on_exit)
  s = PlanList()
  nav.push(s)
  return s


class PlanListTest(unittest.TestCase):
  def setUp(self):
    support.open_db()
    db.add_plan('A')
    db.add_plan('B')

  def tearDown(self):
    support.close_db()

  def test_set_marks_the_current_plan(self):
    s = open_screen()
    press(s, DOWN, 's')
    self.assertEqual(db.current_plan(), 'B')
    self.assertEqual(s.list.rows, ['A', '* B'])

  def test_delete_removes_the_plan_and_keeps_the_cursor_in_range(self):
    s = open_screen()
    press(s, DOWN, 'd')
    self.assertEqual(db.plans(), ['A'])
    self.assertEqual(s.list.cursor, 0)

  def test_delete_with_no_plans_is_ignored(self):
    db.delete_plan('A')
    db.delete_plan('B')
    press(open_screen(), 'd', 's')
    self.assertEqual(db.plans(), [])

  def test_enter_edits_the_selected_plan(self):
    press(open_screen(), DOWN, ENTER)
    self.assertEqual(support.nav_calls, [('plan_edit', ('B',))])

  def test_new_opens_the_plan_form(self):
    press(open_screen(), 'n')
    self.assertEqual(support.nav_calls, [('plan_form', ())])

  def test_escape_leaves_through_on_exit(self):
    exits = []
    press(open_screen(lambda: exits.append(1)), ESC)
    self.assertEqual(exits, [1])
