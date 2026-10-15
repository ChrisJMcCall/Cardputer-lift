import unittest

import db
import support
from support import BACK, DOWN, ENTER, ESC, UP, press
from ui.exercise_log import ExerciseLog


class ExerciseLogTest(unittest.TestCase):
  def setUp(self):
    support.open_db()

  def tearDown(self):
    support.close_db()

  def saved_sets(self, screen, name):
    return db.get_log(screen.day, name)['sets']

  def test_done_checkbox(self):
    db.add_exercise('Stretch')
    s = ExerciseLog('P', 'Stretch')
    self.assertEqual(s.rows(), ['[ ] Done'])
    press(s, ENTER)
    self.assertEqual(s.rows(), ['[x] Done'])
    self.assertTrue(db.is_logged(s.day, 'Stretch'))
    press(s, ENTER)
    self.assertFalse(db.is_logged(s.day, 'Stretch'))

  def test_logging_sets_with_weight_and_reps(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    s = ExerciseLog('P', 'Squat')
    self.assertEqual(s.rows(), ['+ Add set'])
    press(s, ENTER, '135', ENTER, '8', ENTER)
    self.assertEqual(s.rows(), ['Set 1: 135 x 8 reps', '+ Add set'])
    self.assertEqual(self.saved_sets(s, 'Squat'), [['135', '8']])

  def test_new_set_copies_the_previous_one(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    s = ExerciseLog('P', 'Squat')
    press(s, ENTER, '135', ENTER, '8', ENTER)
    press(s, DOWN, ENTER, ENTER, ENTER)
    self.assertEqual(self.saved_sets(s, 'Squat'), [['135', '8'], ['135', '8']])

  def test_escape_discards_a_new_set(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    s = ExerciseLog('P', 'Squat')
    press(s, ENTER, '135', ENTER, '8', ENTER)
    press(s, DOWN, ENTER, ESC)
    self.assertEqual(len(s.entries), 1)
    self.assertEqual(s.cursor, 0)
    self.assertEqual(self.saved_sets(s, 'Squat'), [['135', '8']])
    self.assertEqual(support.nav_calls, [])

  def test_escape_while_not_editing_goes_back_to_the_session(self):
    db.add_exercise('Stretch')
    press(ExerciseLog('P', 'Stretch'), ESC)
    self.assertEqual(support.nav_calls, [('session', ('P',))])

  def test_escape_keeps_an_existing_value(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    s = ExerciseLog('P', 'Squat')
    press(s, ENTER, '135', ENTER, '8', ENTER)
    press(s, ENTER, BACK, '9', ESC)
    self.assertEqual(self.saved_sets(s, 'Squat'), [['135', '8']])

  def test_weight_accepts_one_decimal_point(self):
    db.add_exercise('Curl', weight=True)
    s = ExerciseLog('P', 'Curl')
    press(s, ENTER, '12.5.', ENTER)
    self.assertEqual(self.saved_sets(s, 'Curl'), [['12.5', '']])
    self.assertEqual(s.rows(), ['12.5'])

  def test_reps_reject_non_digits(self):
    db.add_exercise('Pushup', reps=True)
    s = ExerciseLog('P', 'Pushup')
    press(s, ENTER, '1.a2', ENTER)
    self.assertEqual(self.saved_sets(s, 'Pushup'), [['', '12']])
    self.assertEqual(s.rows(), ['12 reps'])

  def test_backspace_edits_the_value(self):
    db.add_exercise('Pushup', reps=True)
    s = ExerciseLog('P', 'Pushup')
    press(s, ENTER, '123', BACK, ENTER)
    self.assertEqual(self.saved_sets(s, 'Pushup'), [['', '12']])

  def test_delete_a_set(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    s = ExerciseLog('P', 'Squat')
    press(s, ENTER, '100', ENTER, '5', ENTER)
    press(s, DOWN, ENTER, BACK, BACK, BACK, '110', ENTER, ENTER)  # the new set starts as a copy of 100 x 5
    press(s, UP, 'd')
    self.assertEqual(self.saved_sets(s, 'Squat'), [['110', '5']])
    self.assertEqual(s.rows(), ['Set 1: 110 x 5 reps', '+ Add set'])

  def test_sets_only_exercise_counts_sets(self):
    db.add_exercise('Plank', sets=True)
    s = ExerciseLog('P', 'Plank')
    press(s, ENTER)
    self.assertEqual(s.rows(), ['Set 1', '+ Add set'])
    self.assertTrue(db.is_logged(s.day, 'Plank'))

  def test_reopening_shows_saved_values(self):
    db.add_exercise('Squat', weight=True, reps=True, sets=True)
    s = ExerciseLog('P', 'Squat')
    press(s, ENTER, '135', ENTER, '8', ENTER)
    self.assertEqual(ExerciseLog('P', 'Squat').rows(), ['Set 1: 135 x 8 reps', '+ Add set'])
