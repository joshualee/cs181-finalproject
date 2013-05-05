import time
import common
import random
import json
import game_interface as gi

DATA_FILENAME = "data/random_walk.json"
OBS_PER_PLANT = 10
DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]

# magic number for unvisted grid location
GI_NOT_VISITED = 4

ALPHA = 1.0
GAMMA = 0.95

def plant_status_to_str(status):
  if status == gi.STATUS_NO_PLANT:
    return "no plant"
  elif status == gi.STATUS_UNKNOWN_PLANT:
    return "unknown"
  elif status == gi.STATUS_POISONOUS_PLANT:
    return "poisonous"
  elif status == gi.STATUS_NUTRITIOUS_PLANT:
    return "nutritious"
  else:
    return "type not recognized"

def set_previous_state(view):
  view.prev_x = view.GetXPos()
  view.prev_y = view.GetYPos()
  view.prev_life = view.GetLife()
  view.prev_plant_status = view.GetPlantInfo()
  
  view.prev_plant_images = []
  for i in range(OBS_PER_PLANT):
    view.prev_plant_images.append(view.GetImage())
  
  view.prev_direction = view.direction
  view.prev_eat = view.eat
  
  view.prev_state = view.cur_state

def determine_direction(view):
  assert((view.prev_x != view.GetXPos() and view.prev_y == view.GetYPos())
    or (view.prev_x == view.GetXPos() and view.prev_y != view.GetYPos()))
  
  if view.prev_x < view.GetXPos():
    return gi.RIGHT
  elif view.prev_x > view.GetXPos():
    return gi.LEFT
  elif view.prev_y < view.GetYPos():
    return gi.UP
  elif view.prev_y > view.GetYPos():
    return gi.DOWN
  else:
    assert False, "determine_direction: player didn't move (fatal game error)"

def dir_to_str(d):
  if d == gi.UP: return "up"
  if d == gi.DOWN: return "down"
  if d == gi.LEFT: return "left"
  if d == gi.RIGHT: return "right"

def get_grid(view, x, y):
  try: return view.grid[x, y]
  except KeyError: return GI_NOT_VISITED

def set_state(view):
  cur_x, cur_y = view.GetXPos(), view.GetYPos()
  cur = get_grid(view, cur_x, cur_y)
  up = get_grid(view, cur_x, cur_y+1)
  right = get_grid(view, cur_x+1, cur_y)
  down = get_grid(view, cur_x, cur_y-1)
  left = get_grid(view, cur_x-1, cur_y)
  view.cur_state = (cur, up, right, down, left)

def update_grid(view):
  view.grid[(view.GetXPos(), view.GetYPos())] = view.GetPlantInfo()

def bootstrap(view):
  view.bootstrapped = True
  
  view.start_x = view.GetXPos()
  view.start_y = view.GetYPos()
  
  view.q = {}
  view.grid = {}
  
  update_state(view)

def update_state(view):
  update_grid(view)
  set_state(view)

def get_argmax_qsa(view):
  neg_inf = float('-inf')
  
  max_dirs = []
  max_val = neg_inf
  for d in DIRECTIONS:
    sa = (view.cur_state, d)
    if view.q.get(sa, neg_inf) == max_val:
      max_dirs.append(d)
    elif view.q.get(sa, neg_inf) > max_val:
      max_val = view.q[sa]
      max_dirs = [d]
  
  # If no actions for this state are in the dict, eturn a random direction
  # Otherwise return the best direction, but break ties randomly  
  return random.choice(max_dirs)

def get_max_qsa(view):
  best_dir = get_argmax_qsa(view)
  sa = (view.cur_state, best_dir)
  return view.q.get(sa, 0)

def e_greedy(view):
  t = view.GetRound() + 1 # get round is 0 indexed
  e = 1.0 / t
  u = random.uniform(0, 1)
  
  if u < e:
    return random.choice(DIRECTIONS)
  else:
    return get_argmax_qsa(view)

def get_move(view):
  if not hasattr(view, "bootstrapped"):
    bootstrap(view)
  else:
    moved_dir = determine_direction(view)
    reward = view.GetLife() - view.prev_life
    update_state(view)
    
    sa = (view.prev_state, moved_dir)
    
    prev_q = view.q.get(sa, 0)
    max_qsa = get_max_qsa(view)
    
    view.q[(view.prev_state, moved_dir)] = \
      prev_q + ALPHA * (reward + GAMMA * max_qsa - prev_q)
  
  view.direction = e_greedy(view)
  
  view.eat = True
  
  set_previous_state(view)
  
  return (view.direction, view.eat)