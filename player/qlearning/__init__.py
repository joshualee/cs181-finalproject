import sys
import os
import time
import common
import random
import pickle
import game_interface as gi
import neural_network as nn

import simple_neural_net_player as nnp
import dt.simple_dt_player as dt

# to import neural network
mydir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,mydir)
sys.path.insert(0,mydir+"/neural_network")
import neural_net_impl
import neural_net

Q_FILENAME = "player/q_tournament.pickle"
NN_FILENAME = "player/nn_15.pickle"
DTREE_FILENAME = "player/dtree_boost25_32k.pickle"

DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]

# magic number for unvisted grid location
GI_NOT_VISITED = 4

ALPHA = 1.0
GAMMA = 0.75

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
  up_left = get_grid(view, cur_x-1, cur_y+1)
  up_right = get_grid(view, cur_x+1, cur_y+1)
  down_left = get_grid(view, cur_x-1, cur_y-1)
  down_right = get_grid(view, cur_x+1, cur_y-1)
  view.cur_state = (cur_x, cur_y, cur, up, right, down, left, up_left, up_right, down_left, down_right)

def update_grid(view):
  view.grid[(view.GetXPos(), view.GetYPos())] = view.GetPlantInfo()

def load_q(view):
  try:
    q_file = open(Q_FILENAME, 'r')
    view.q = pickle.loads(q_file.read())
    
  # file not found -- start new q function
  except IOError: assert False, "Could not load pickled Q function -- must change "
  except EOFError: assert False, "Could not load pickled Q function"
  # except IOError: view.q = {}
  # except EOFError: view.q = {}

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

  view.network = nnp.load_neural_net(NN_FILENAME)
  view.dtree = dt.load_dtree(DTREE_FILENAME)

  update_state(view)

def joint_classify(view):
  plant_img = view.GetImage()
  plant_img2 = view.GetImage()
  dtree1 = dt.cur_plant_nutritious(view, plant_img)
  nn1 = nnp.cur_plant_nutritious(view, plant_img)  
  dtree2 = dt.cur_plant_nutritious(view, plant_img2)
  nn2 = nnp.cur_plant_nutritious(view, plant_img2)
  p = dtree1 + nn1 + dtree2 + nn2
  return p >= 2

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

  if u < e: return random.choice(DIRECTIONS)
  else: return get_argmax_qsa(view)

def get_move(view):
  test = open("test.tmp", 'w')
  test.write("test")
  if not hasattr(view, "bootstrapped"):
    # Initialize
    bootstrap(view)
  else:
    # Figure out results of previous action
    moved_dir = determine_direction(view)
    reward = view.GetLife() - view.prev_life
    update_state(view)
  
    # Update Q function
    sa = (view.prev_state, moved_dir)
    prev_q = view.q.get(sa, 0)
    max_qsa = get_max_qsa(view)
    view.q[sa] = \
      prev_q + ALPHA * (reward + GAMMA * max_qsa - prev_q)
  
  # Choose direction to move in
  view.direction = e_greedy(view)
  # view.direction = get_argmax_qsa(view)
  # view.direction = dir_within_z(view, 50)
  
  # Determine if we should eat or not
  view.eat = False
  if view.GetPlantInfo() == gi.STATUS_UNKNOWN_PLANT:
    view.eat = joint_classify(view)
  
  set_previous_state(view)
  return (view.direction, view.eat)