import game_interface as gi
import random
import time
import os
import sys
import neural_network as nn
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parentdir += '/neural_network'
sys.path.insert(0,parentdir)
import neural_net_impl
import neural_net

DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]

def load_neural_net(infile):
  return nn.neural_net_pickle.load_neural_network(infile)

def cur_plant_nutritious(view, plant_img):
  # image requires an argument to serve as label, but unused here
  # since we just call classify, so give it a garbage value
  image = nn.data_reader.Image(0)
  image.pixels = plant_img
  return view.network.ClassifySoft(image)

def get_move(view):
  if view.GetRound() == 0:
    view.network = load_neural_net('save/nn.pickle')
  # Choose a random direction.
  # If there is a plant in this location, then try and eat it.
  hasPlant = view.GetPlantInfo() == gi.STATUS_UNKNOWN_PLANT
  
  eat = hasPlant and cur_plant_nutritious(view) > 0.5
    
  # Choose a random direction
  return (random.choice(DIRECTIONS), hasPlant)