import time
import common
import random
import json
import pickle
import game_interface as gi

DATA_FILENAME = "data/random_walk.json"
JSON_FILENAME = "data/raw_data.json"
OBS_PER_PLANT = 10
DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]

# magic number for unvisted grid location
GI_NOT_VISITED = 4

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
    assert False, "determine_direction: didn't move"

def dir_to_str(d):
  if d == gi.UP: return "up"
  if d == gi.DOWN: return "down"
  if d == gi.LEFT: return "left"
  if d == gi.RIGHT: return "right"

def init_dir_dict(view):
  view.dir_dict = {}
  for d1 in DIRECTIONS:
    view.dir_dict[dir_to_str(d1)] = {}
    for d2 in DIRECTIONS:
      view.dir_dict[dir_to_str(d1)][dir_to_str(d2)] = 0

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
  view.state = (cur, up, right, down, left)

# (Current, Up, Right, Down, Left)
def init_state(view):
  view.state = (
    view.GetPlantInfo(),
    gi.STATUS_UNKNOWN_PLANT,
    gi.STATUS_UNKNOWN_PLANT, 
    gi.STATUS_UNKNOWN_PLANT, 
    gi.STATUS_UNKNOWN_PLANT
  )

def update_grid(view):
  view.grid[(view.GetXPos(), view.GetYPos())] = view.GetPlantInfo()

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
    return random.choice(DIRECTIONS)
       
def get_move(view):
  if not hasattr(view, "initialized"):
    view.initialized = True
    view.data_file = open(DATA_FILENAME, 'a')
    view.reward_dict = {}
    view.state_dict = {}
    view.grid = {}
    view.start_x = view.GetXPos()
    view.start_y = view.GetYPos()
    view.reward_grid = {}
    
    init_dir_dict(view)
    update_grid(view)
    set_state(view)
    
    # print "START LOCATION: ({0}, {1})".format(view.GetXPos(), view.GetYPos())

  else:
    moved_direction = determine_direction(view)
    update_grid(view)
    set_state(view)
    # print "{0}: {1}".format(view.GetRound(), view.state)
    # print "{0}: ({1}, {2})".format(view.GetRound(), view.GetXPos(), view.GetYPos())
    
    # if view.GetRound() > 50000:
    # view.dir_dict[dir_to_str(view.prev_direction)][dir_to_str(moved_direction)] += 1    
    reward = view.GetLife() - view.prev_life
    
    prev_pos = str((view.prev_x, view.prev_y))
    
    if reward != 0:
      assert prev_pos not in view.reward_grid
      view.reward_grid[prev_pos] = reward
    elif prev_pos not in view.reward_grid:
      view.reward_grid[prev_pos] = reward
  
    # if reward in view.reward_dict:
    #   view.reward_dict[reward] += 1
    # else:
    #   view.reward_dict[reward] = 1
    
    # if view.state in view.state_dict:
    #   view.state_dict[view.state] += 1
    # else:
    #   view.state_dict[view.state] = 1
    
    if len(view.prev_plant_images[0]) != 0:
      new_data = json.dumps((view.prev_plant_images, reward))
      view.data_file.write("{0}\n".format(new_data))
        
  # if view.GetRound() < 50000:
  #   view.direction = gi.LEFT
  # else:
  #   view.direction = random.choice(DIRECTIONS)
    
  view.direction = random.choice(DIRECTIONS)
  # view.direction = dir_within_z(view, 500)
  view.eat = True
  set_previous_state(view)
  
  if view.GetRound() == 10000:
    # print view.dir_dict
    # print view.reward_dict
    # print view.state_dict
    outfile = open('data/d4', 'w')
    outfile.write(json.dumps(view.reward_grid))
    view.direction = None
  
  return (view.direction, view.eat)

def collect_data(view):
  if not hasattr(view, "initialized"):
    view.initialized = True
    view.data_file = open(JSON_FILENAME, 'a')
    
    view.start_x, view.start_y = view.GetXPos(), view.GetYPos()
  else:
    reward = view.GetLife() - view.prev_life
    
    if len(view.prev_plants[0]) != 0 and view.prev_status == gi.STATUS_UNKNOWN_PLANT and reward > 0:
      for plant in view.prev_plants:
        new_data = json.dumps((plant, reward))
        view.data_file.write(new_data + "\n")
    
  view.prev_life = view.GetLife()
  view.prev_plants = []
  for i in range(OBS_PER_PLANT):
    view.prev_plants.append(view.GetImage())
  view.prev_status = view.GetPlantInfo()
  
  # d = random.choice(DIRECTIONS)
  d = dir_within_z(view, 200)
  eat = True
  
  return (d, eat)