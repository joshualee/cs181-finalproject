import os
import sys
mydir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, mydir)

import common
import data_collector
import qlearning
import simple_neural_net_player
import em
import dt

def get_move(view):
  return qlearning.get_move(view)