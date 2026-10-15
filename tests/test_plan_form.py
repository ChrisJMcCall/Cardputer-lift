import unittest

import db
import support
from support import BACK, ENTER, ESC, press
from ui.plan_form import PlanForm


class PlanFormTest(unittest.TestCase):
  def setUp(self):
    support.open_db()

  def tearDown(self):
    support.close_db()

  def test_creates_a_plan_and_opens_the_exercise_picker(self):
    press(PlanForm(), 'Push', ENTER, ENTER)
    self.assertEqual(db.plans(), ['Push'])
    self.assertEqual(support.nav_calls, [('plan_edit', ('Push',))])

  def test_order_defaults_to_last(self):
    db.add_plan('A')
    s = PlanForm()
    self.assertEqual(s.fields[1][1], '2')
    press(s, 'B', ENTER, ENTER)
    self.assertEqual(db.plans(), ['A', 'B'])

  def test_order_places_the_plan(self):
    db.add_plan('A')
    db.add_plan('B')
    press(PlanForm(), 'C', ENTER, BACK, '1', ENTER)
    self.assertEqual(db.plans(), ['C', 'A', 'B'])

  def test_order_beyond_the_end_goes_last(self):
    db.add_plan('A')
    press(PlanForm(), 'B', ENTER, BACK, '9', ENTER)
    self.assertEqual(db.plans(), ['A', 'B'])

  def test_cleared_order_goes_last(self):
    db.add_plan('A')
    press(PlanForm(), 'B', ENTER, BACK, ENTER)
    self.assertEqual(db.plans(), ['A', 'B'])

  def test_order_field_takes_digits_only(self):
    s = PlanForm()
    press(s, 'X', ENTER, BACK, 'a1b')
    self.assertEqual(s.fields[1][1], '1')

  def test_duplicate_name_stays_on_the_form(self):
    db.add_plan('A')
    s = PlanForm()
    press(s, 'A', ENTER, ENTER)
    self.assertEqual(db.plans(), ['A'])
    self.assertEqual(s.idx, 0)
    self.assertEqual(support.nav_calls, [])

  def test_empty_name_is_rejected(self):
    s = PlanForm()
    press(s, ENTER, ENTER)
    self.assertEqual(db.plans(), [])
    self.assertEqual(s.idx, 0)

  def test_escape_returns_to_plans(self):
    press(PlanForm(), ESC)
    self.assertEqual(support.nav_calls, [('plans', ())])
