# Screen router and main-loop glue between the keyboard and the active screen.
import db

current = None
kb = None

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
  elif name == 'text':
    from ui.text_input import TextInput as S
  current = S(*args)

def start(kb_0):
  global kb

  kb = kb_0
  db.open_db()
  go('main')

def tick():
  if kb.is_pressed():
    current.on_key(kb.get_key())
  current.tick()
  if current.dirty:
    current.dirty = False
    current.draw()
