import unittest

import db
import support
from support import DOWN, ENTER, ESC, press
from ui.session import Session


class SessionTest(unittest.TestCase):
  def setUp(self):
    support.open_db()
    db.add_exercise('A')
    db.add_exercise('B', weight=True, reps=True, sets=True)
    db.add_plan('P')
    db.toggle_plan_item('P', 'A')
    db.toggle_plan_item('P', 'B')

  def tearDown(self):
    support.close_db()

  def test_rows_show_what_is_logged_today(self):
    s = Session('P')
    self.assertEqual(s.rows(), ['[ ] A', '[ ] B'])
    db.set_log(s.day, 'A', {'done': True, 'sets': []})
    self.assertEqual(s.rows(), ['[x] A', '[ ] B'])

  def test_yesterdays_log_does_not_count(self):
    db.set_log('2000-01-01', 'A', {'done': True, 'sets': []})
    self.assertEqual(Session('P').rows(), ['[ ] A', '[ ] B'])

  def test_enter_opens_the_selected_exercise(self):
    press(Session('P'), DOWN, ENTER)
    self.assertEqual(support.nav_calls, [('exercise_log', ('P', 'B'))])

  def test_empty_plan_ignores_enter(self):
    db.add_plan('Empty')
    press(Session('Empty'), ENTER)
    self.assertEqual(support.nav_calls, [])

  def test_escape_returns_to_the_main_menu(self):
    press(Session('P'), ESC)
    self.assertEqual(support.nav_calls, [('main', ())])
