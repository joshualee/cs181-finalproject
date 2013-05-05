import game_interface as gi
import random
import time
import em

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

def get_move(view):
  if view.GetRound() == 0:
    view.em = em.EM()
  else:
    reward = view.GetLife() - view.prev_life
    if reward > 0:
      view.em.add_data_point(view.prev_x, view.prev_y)
    
    view.em.train(5)
  
  view.eat = True
  view.direction = view.em.get_direction(view)

  set_prev_state(view)

  return (view.direction, view.eat)