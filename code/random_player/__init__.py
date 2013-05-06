import game_interface as gi
import random
import time

DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]

def get_move(view):
  # Choose a random direction.
  # If there is a plant in this location, then try and eat it.
  hasPlant = view.GetPlantInfo() == gi.STATUS_UNKNOWN_PLANT
  
  eat = False
  if hasPlant and random.uniform(0, 1) < 0.5:
    eat = True
  
  # Choose a random direction
  return (random.choice(DIRECTIONS), hasPlant)