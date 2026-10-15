import unittest

import db
import support

DAY = '2024-01-01'


class DbTest(unittest.TestCase):
  def setUp(self):
    support.open_db()

  def tearDown(self):
    support.close_db()

  def test_add_exercise_rejects_duplicates(self):
    self.assertTrue(db.add_exercise('Squat'))
    self.assertFalse(db.add_exercise('Squat'))
    self.assertEqual(db.exercises(), ['Squat'])

  def test_exercise_info_defaults_for_older_records(self):
    db._put('ex:Old', {'description': 'x'})
    self.assertEqual(db.exercise_info('Old'), {'description': 'x', 'weight': False, 'reps': False, 'sets': False})

  def test_exercise_info_roundtrip(self):
    db.add_exercise('Squat', 'legs', weight=True, sets=True)
    info = db.exercise_info('Squat')
    self.assertEqual((info['description'], info['weight'], info['reps'], info['sets']), ('legs', True, False, True))

  def test_delete_exercise_removes_it_from_plans(self):
    db.add_exercise('Squat')
    db.add_plan('A')
    db.toggle_plan_item('A', 'Squat')
    db.delete_exercise('Squat')
    self.assertEqual(db.exercises(), [])
    self.assertEqual(db.plan_items('A'), [])

  def test_plans_default_to_creation_order(self):
    for name in ('B', 'A', 'C'):
      db.add_plan(name)
    self.assertEqual(db.plans(), ['B', 'A', 'C'])

  def test_add_plan_position(self):
    db.add_plan('A')
    db.add_plan('B')
    db.add_plan('C', 0)
    db.add_plan('D', 99)
    self.assertEqual(db.plans(), ['C', 'A', 'B', 'D'])

  def test_plans_missing_from_order_go_last_alphabetically(self):
    db.add_plan('A')
    db._put('plan:Z', [])
    db._put('plan:M', [])
    self.assertEqual(db.plans(), ['A', 'M', 'Z'])

  def test_add_plan_rejects_duplicates(self):
    self.assertTrue(db.add_plan('A'))
    self.assertFalse(db.add_plan('A'))

  def test_first_plan_becomes_current(self):
    db.add_plan('A')
    db.add_plan('B')
    self.assertEqual(db.current_plan(), 'A')

  def test_deleting_current_plan_selects_the_next_one(self):
    db.add_plan('A')
    db.add_plan('B')
    db.delete_plan('A')
    self.assertEqual(db.plans(), ['B'])
    self.assertEqual(db.current_plan(), 'B')

  def test_deleting_last_plan_clears_current(self):
    db.add_plan('A')
    db.delete_plan('A')
    self.assertIsNone(db.current_plan())

  def test_toggle_plan_item(self):
    db.add_plan('A')
    db.toggle_plan_item('A', 'Squat')
    db.toggle_plan_item('A', 'Press')
    self.assertEqual(db.plan_items('A'), ['Squat', 'Press'])
    db.toggle_plan_item('A', 'Squat')
    self.assertEqual(db.plan_items('A'), ['Press'])

  def test_empty_log(self):
    self.assertEqual(db.get_log(DAY, 'Squat'), {'done': False, 'sets': []})

  def test_done_checkbox_exercise(self):
    db.add_exercise('Stretch')
    self.assertFalse(db.is_logged(DAY, 'Stretch'))
    db.set_log(DAY, 'Stretch', {'done': True, 'sets': []})
    self.assertTrue(db.is_logged(DAY, 'Stretch'))

  def test_set_based_exercise_is_logged_once_it_has_sets(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    self.assertFalse(db.is_logged(DAY, 'Squat'))
    db.set_log(DAY, 'Squat', {'done': False, 'sets': [['135', '8']]})
    self.assertTrue(db.is_logged(DAY, 'Squat'))

  def test_logs_are_per_day(self):
    db.add_exercise('Stretch')
    db.set_log(DAY, 'Stretch', {'done': True, 'sets': []})
    self.assertFalse(db.is_logged('2024-01-02', 'Stretch'))
