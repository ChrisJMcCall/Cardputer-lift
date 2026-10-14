import unittest

import date_time


class FakeTime:
  seen = None

  @staticmethod
  def time():
    return 1700000000

  @staticmethod
  def localtime(secs):
    FakeTime.seen = secs
    return (2024, 3, 5, 7, 9, 0, 1, 65)


class DateTimeTest(unittest.TestCase):
  def setUp(self):
    self.real_time = date_time.time
    date_time.time = FakeTime

  def tearDown(self):
    date_time.time = self.real_time

  def test_now_applies_utc_offset(self):
    date_time.now()
    self.assertEqual(FakeTime.seen, 1700000000 + date_time.UTC_OFFSET_HOURS * 3600)

  def test_today_is_zero_padded(self):
    self.assertEqual(date_time.today(), '2024-03-05')
