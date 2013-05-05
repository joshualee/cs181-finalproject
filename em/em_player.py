import game_interface as gi
import random
import time
import em
import simple_neural_net_player as nn
import dt.simple_dt_player as dt

DIRECTIONS = [
  gi.UP,
  gi.DOWN,
  gi.LEFT,
  gi.RIGHT
]

def set_prev_state(view):
  view.prev_x = view.GetXPos()
  view.prev_y = view.GetYPos()
  
  view.prev_life = view.GetLife()


def joint_classify(view):
  dtree_class = dt.cur_plant_nutritious(view)
  nn_class = nn.cur_plant_nutritious(view)

def get_move(view):
  if view.GetRound() == 0:    
    view.em = em.EM()
    view.network = nn.load_neural_net('save/nn_15.pickle')
    view.dtree = dt.load_dtree('save/dtree_boost25_32k.pickle')
  else:
    reward = view.GetLife() - view.prev_life
    if reward > 0:
      view.em.add_data_point(view.prev_x, view.prev_y)
    
    view.em.train(5)
  
  view.eat = True
  view.direction = view.em.get_direction(view)

  set_prev_state(view)

  return (view.direction, view.eat)