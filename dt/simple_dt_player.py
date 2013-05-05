import game_interface as gi
import random
import time
import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir + '/dt')
import dtree
import main
import pickle

DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]


def load_dtree(infile):
  infile = open(infile, 'r')
  return pickle.loads(infile.read())

def cur_plant_nutritious(view):
  # image requires an argument to serve as label, but unused here
  # since we just call classify, so give it a garbage value
  
  # add dummy label for Example class to have proper length input
  plant = list(view.GetImage()) + [0]
  example = dtree.Example(plant)
  
  nutritious = main.weighted_classify(view.dtree, example)
  print nutritious
  # 1 for nutritious, 0 for poisonous
  return (nutritious == 1)

def get_move(view):
  if view.GetRound() == 0:
    view.dtree = load_dtree('save/dtree_boost25_32k.pickle')
  # Choose a random direction.
  # If there is a plant in this location, then try and eat it.
  hasPlant = view.GetPlantInfo() == gi.STATUS_UNKNOWN_PLANT
  
  eat = hasPlant and cur_plant_nutritious(view)
    
  # Choose a random direction
  return (random.choice(DIRECTIONS), hasPlant)