import sys
import os
import time
import common
import random
import pickle
import game_interface as gi
import neural_network as nn


# to import neural network
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parentdir += '/neural_network'
sys.path.insert(0,parentdir)
import neural_net_impl
import neural_net

Q_FILENAME = "save/q_11.pickle"

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
  x_dist = cur_x - view.start_x
  y_dist = cur_y - view.start_y
  up_left = get_grid(view, cur_x-1, cur_y+1)
  up_right = get_grid(view, cur_x+1, cur_y+1)
  down_left = get_grid(view, cur_x-1, cur_y-1)
  down_right = get_grid(view, cur_x+1, cur_y-1)
  view.cur_state = (cur, up, right, down, left, up_left, up_right, down_left, down_right, x_dist, y_dist)

def update_grid(view):
  view.grid[(view.GetXPos(), view.GetYPos())] = view.GetPlantInfo()

def load_q(view):
  try:
    q_file = open(Q_FILENAME, 'r')
    view.q = pickle.loads(q_file.read())
    print "successfully loaded!!!\n\n\n\n\n~~~~~~~~~~~~~~"
  # file not found -- start new q function
  except IOError: view.q = {}
  except EOFError: view.q = {}

def save_q(view):
  q_file = open(Q_FILENAME, 'w')
  q_file.write(pickle.dumps(view.q))

def dir_towards_start(view):
  cur_x, cur_y, start_x, start_y = view.GetXPos(), view.GetYPos(), view.start_x, view.start_y

  if cur_x == start_x and cur_y == start_y:
    return random.choice(DIRECTIONS)
  else:
    if abs(cur_x - start_x) >= abs(cur_y - start_y):
      # move in x direction
      if cur_x > start_x: return gi.LEFT
      else: return gi.RIGHT
    else:
      # move in y direction
      if cur_y > start_y: return gi.DOWN
      else: return gi.UP

def dir_within_z(view, z):
  cur_x, cur_y, start_x, start_y = view.GetXPos(), view.GetYPos(), view.start_x, view.start_y

  if abs(cur_x - start_x) >= z or abs(cur_y - start_y) >= z:
    return dir_towards_start(view)
  else:
    return get_argmax_qsa(view)

def bootstrap(view):
  view.bootstrapped = True

  view.start_x = view.GetXPos()
  view.start_y = view.GetYPos()

  load_q(view)
  view.grid = {}

  view.network = nn.neural_net_pickle.load_neural_network('save/nn.pickle')

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

def cur_plant_nutritious(view):
  # image requires an argument to serve as label, but unused here
  # since we just call classify, so give it a garbage value
  image = nn.data_reader.Image(0)
  image.pixels = view.GetImage()
  # 1 for nutritious, 0 for poisonous
  return (view.network.Classify(image) == 1)

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
  # view.direction = get_argmax_qsa(view)
  # view.direction = dir_within_z(view, 50)


  view.eat = False
  if view.GetPlantInfo() == gi.STATUS_UNKNOWN_PLANT:
    view.eat = cur_plant_nutritious(view)

  # for now, save the q function each iteration
  save_q(view)

  set_previous_state(view)

  return (view.direction, view.eat)
