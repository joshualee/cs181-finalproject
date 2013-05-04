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
  gi.DOWN
]

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

def get_move(view):
  if not hasattr(view, "initialized"):
    view.initialized = True
    view.data_file = open(DATA_FILENAME, 'a')
  else:
    moved_direction = determine_direction(view)
    reward = view.GetLife() - view.prev_life
    
    if len(view.prev_plant_images[0]) != 0:
      new_data = json.dumps((view.prev_plant_images, reward))
      view.data_file.write("{0}\n".format(new_data))
        
  view.direction = random.choice(DIRECTIONS)
  view.eat = True
  set_previous_state(view)
  
  return (view.direction, view.eat)
