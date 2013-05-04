import common
import pickle
import random
import game_interface as gi

# Data Collector

DATA_FILENAME = "data/random_walk_data.csv"
ITERATIONS = 50
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

def get_move(view):
  if not hasattr(view, "iterations"):
    view.iterations = 0
    view.data = open(DATA_FILENAME, 'rw')
  
  view.iterations += 1
  
  cur_x, cur_y = view.GetXPos(), view.GetYPos()
  cur_plant_status = plant_status_to_str(view.GetPlantInfo())
  
  print "({0}, {1}): {2}".format(cur_x, cur_y, cur_plant_status)
  
  # current_life = view.GetLife()
  # 
  # view.previous
  direction = random.choice(DIRECTIONS)
  eat = False
  
  return (direction, eat)
