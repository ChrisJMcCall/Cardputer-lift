import unittest

from ccui.nav import Navigator
from ccui.screen import Screen
from ccui.state import State
from ccui.theme import LINE_H
from ccui.view import Checkbox, HStack, ListView, Spacer, Text, TextField, VStack

from ccui.theme import KEY_MENU

ENTER, ESC, BACK, UP, DOWN, TAB, BACKTAB = 13, 27, 8, 181, 182, 9, 353


class FakeKb:
  def is_pressed(self):
    return False


def press(screen, *keys):
  for k in keys:
    for code in ([ord(c) for c in k] if isinstance(k, str) else [k]):
      screen.on_key(code)


class Form(Screen):
  title = 'Form'

  def build(self):
    self.name = TextField('Name', max_len=5)
    self.flag = Checkbox('Flag')
    self.saved = []
    self.commands = [(ord('?'), 'Save', lambda: self.saved.append(1))]
    return VStack(self.name, self.flag, spacing=2)


class StateTest(unittest.TestCase):
  def test_set_invalidates_bound_views_only_on_change(self):
    s = State('a')
    t = Text(s)
    t.dirty = False
    s.value = 'a'
    self.assertFalse(t.dirty)
    s.value = 'b'
    self.assertTrue(t.dirty)


class LayoutTest(unittest.TestCase):
  def test_vstack_flex_takes_leftover(self):
    a, sp, b = Text('a'), Spacer(), Text('b')
    VStack(a, sp, b).place(0, 0, 100, 100)
    self.assertEqual((a.y, sp.y, sp.h, b.y), (0, LINE_H, 100 - 2 * LINE_H, 100 - LINE_H))

  def test_hstack_splits_flex_evenly(self):
    a, b = Spacer(), Spacer()
    HStack(a, b, spacing=10).place(0, 0, 110, 20)
    self.assertEqual((a.x, a.w, b.x, b.w), (0, 50, 60, 50))

  def test_padding_and_spacing(self):
    a, b = Text('a'), Text('b')
    VStack(a, b, spacing=2, pad=4).place(10, 10, 100, 100)
    self.assertEqual((a.x, a.y, a.w, b.y), (14, 14, 92, 14 + LINE_H + 2))


class FocusTest(unittest.TestCase):
  def setUp(self):
    self.nav = Navigator(FakeKb())
    self.form = Form()
    self.nav.push(self.form)

  def test_arrows_move_focus_even_while_editing(self):
    self.assertTrue(self.form.name.focused and self.form.name.editing)
    press(self.form, DOWN)
    self.assertTrue(self.form.flag.focused and not self.form.name.editing)
    press(self.form, DOWN)
    self.assertTrue(self.form.name.focused)
    press(self.form, UP)
    self.assertTrue(self.form.flag.focused)

  def test_esc_stops_editing_then_tab_navigates(self):
    press(self.form, TAB)  # ignored while editing
    self.assertTrue(self.form.name.focused)
    press(self.form, ESC)
    self.assertFalse(self.form.name.editing)
    self.assertTrue(self.form.name.focused)
    press(self.form, TAB)
    self.assertTrue(self.form.flag.focused)
    press(self.form, BACKTAB)  # arriving by tab doesn't start editing
    self.assertTrue(self.form.name.focused)
    self.assertFalse(self.form.name.editing)

  def test_non_editing_field_ignores_text_until_enter(self):
    press(self.form, ESC, 'abc')
    self.assertEqual(self.form.name.text.value, '')
    press(self.form, ENTER, 'ab')
    self.assertEqual(self.form.name.text.value, 'ab')

  def test_esc_pops_only_when_not_editing(self):
    nav2 = Navigator(FakeKb())
    nav2.push(Form())
    f = Form()
    nav2.push(f)
    press(f, ESC)
    self.assertIs(nav2.top, f)
    press(f, ESC)
    self.assertIsNot(nav2.top, f)

  def test_typing_goes_to_focused_field_and_respects_max_len(self):
    press(self.form, 'abcdefg')
    self.assertEqual(self.form.name.text.value, 'abcde')
    press(self.form, BACK)
    self.assertEqual(self.form.name.text.value, 'abcd')

  def test_enter_advances_then_toggles(self):
    press(self.form, ENTER)
    self.assertTrue(self.form.flag.focused)
    press(self.form, ENTER)
    self.assertTrue(self.form.flag.checked.value)

  def test_shortcut_runs_when_not_consumed(self):
    press(self.form, DOWN, '?')
    self.assertEqual(self.form.saved, [1])


class ListViewTest(unittest.TestCase):
  def test_cursor_wraps_and_select_reports_index(self):
    picked = []
    lv = ListView(lambda: ['a', 'b', 'c'], picked.append)
    lv.place(0, 0, 100, 2 * LINE_H)
    press(lv, UP)
    self.assertEqual(lv.cursor, 2)
    press(lv, ENTER)
    self.assertEqual(picked, [2])

  def test_reload_clamps_cursor(self):
    rows = ['a', 'b', 'c']
    lv = ListView(lambda: rows)
    lv.cursor = 2
    del rows[1:]
    lv.reload()
    self.assertEqual(lv.cursor, 0)


class NavTest(unittest.TestCase):
  def test_esc_pops_but_keeps_last_screen(self):
    nav = Navigator(FakeKb())
    a, b = Form(), Form()
    nav.push(a)
    nav.push(b)
    press(b, ESC, ESC)  # the first ESC ends text editing
    self.assertIs(nav.top, a)
    press(a, ESC, ESC)
    self.assertIs(nav.top, a)

  def test_replace_and_root(self):
    nav = Navigator(FakeKb())
    nav.push(Form())
    nav.push(Form())
    c = Form()
    nav.root(c)
    self.assertEqual(nav.stack, [c])


class MenuTest(unittest.TestCase):
  def setUp(self):
    self.form = Form()
    Navigator(FakeKb()).push(self.form)

  def test_menu_key_opens_and_esc_closes_without_popping(self):
    press(self.form, KEY_MENU)
    self.assertTrue(self.form.menu.open)
    press(self.form, ESC)
    self.assertFalse(self.form.menu.open)
    self.assertTrue(self.form.nav.top is self.form)

  def test_enter_runs_the_highlighted_command_and_closes(self):
    press(self.form, KEY_MENU, ENTER)
    self.assertEqual(self.form.saved, [1])
    self.assertFalse(self.form.menu.open)

  def test_command_key_works_inside_the_menu(self):
    press(self.form, KEY_MENU, '?')
    self.assertEqual(self.form.saved, [1])

  def test_menu_swallows_other_keys(self):
    press(self.form, KEY_MENU, 'abc', DOWN)
    self.assertEqual(self.form.name.text.value, '')
    self.assertTrue(self.form.menu.open)

  def test_second_menu_key_closes(self):
    press(self.form, KEY_MENU, KEY_MENU)
    self.assertFalse(self.form.menu.open)

  def test_no_commands_means_no_menu(self):
    s = Screen()
    Navigator(FakeKb()).push(s)
    press(s, KEY_MENU)
    self.assertFalse(s.menu.open)
