# Screen router and main-loop glue between the keyboard and the active screen.
import db
from ccui.nav import Navigator
from ccui.theme import KEY_MENU

current = None
kb = None
ctrl = None  # callable: True once per ctrl press

# Screens built on ccui, and the legacy screen ESC returns to from them.
CCUI_BACK = {'plans': 'main'}

class Host:
  """Runs a ccui screen inside this router."""
  dirty = True  # ccui views only redraw themselves when invalidated

  def __init__(self, screen, back):
    self.nav = Navigator(on_exit=lambda: go(back))
    self.nav.push(screen)

  def on_key(self, k):
    self.nav.top.on_key(k)

  def tick(self):
    self.nav.top.tick()

  def draw(self):
    self.nav.top.render()

def go(name, *args):
  global current
  # Imported lazily so screens can import nav without a cycle.
  if name == 'main':
    from ui.main_menu import MainMenu as S
  elif name == 'exercises':
    from ui.exercises import ExerciseList as S
  elif name == 'exercise_form':
    from ui.exercise_form import ExerciseForm as S
  elif name == 'plans':
    from ui.plans import PlanList as S
  elif name == 'plan_form':
    from ui.plan_form import PlanForm as S
  elif name == 'plan_edit':
    from ui.plan_edit import PlanEdit as S
  elif name == 'session':
    from ui.session import Session as S
  elif name == 'exercise_log':
    from ui.exercise_log import ExerciseLog as S
  elif name == 'text':
    from ui.text_input import TextInput as S
  current = Host(S(*args), CCUI_BACK[name]) if name in CCUI_BACK else S(*args)

def start(kb_0, ctrl_0=None):
  global kb, ctrl

  kb, ctrl = kb_0, ctrl_0
  db.open_db()
  go('main')

def tick():
  if ctrl and ctrl():
    current.on_key(KEY_MENU)
  if kb.is_pressed():
    current.on_key(kb.get_key())
  current.tick()
  if current.dirty:
    current.dirty = False
    current.draw()
