import game_interface as gi
import random
import time
import em
import simple_neural_net_player as nnp
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
  
  view.prev_plant_status = view.GetPlantInfo()
  view.prev_dtree_class = view.cur_dtree_class
  view.prev_nn_class = view.cur_nn_class
  
  # view.prev_eat = view.eat

def joint_classify(view):
  view.cur_dtree_class = dt.cur_plant_nutritious(view)
  view.cur_nn_class = nnp.cur_plant_nutritious(view)  
  view.prev_eat = (view.cur_dtree_class or view.cur_nn_class)
  return view.prev_eat
  # p = view.cur_dtree_class + view.cur_nn_class
  # print "p: {0}".format(p)
  # view.prev_eat = (p >= 1)
  # return p >= 1
  # u = random.uniform(0, 1)
  # p = view.cur_dtree_class * view.cur_nn_class
  # view.prev_eat = (u <= p)
  # return u <= p

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
  if view.GetRound() == 0:
    view.record = {}
    view.cur_dtree_class = 0
    view.cur_nn_class = 0
    view.start_x, view.start_y = view.GetXPos(), view.GetYPos()
        
    view.em = em.EM()
    view.network = nnp.load_neural_net('save/nn_15.pickle')
    view.dtree = dt.load_dtree('save/dtree_boost25_32k.pickle')
  else:
    reward = view.GetLife() - view.prev_life
    if reward > 0:
      view.em.add_data_point(view.prev_x, view.prev_y)
      
    # increment record counts
    if view.prev_plant_status == gi.STATUS_UNKNOWN_PLANT:
      prev_class = (view.prev_eat, reward)
      if prev_class in view.record: view.record[prev_class] += 1
      else: view.record[prev_class] = 1
      print view.record
    
    view.em.train(10)
  
  view.eat = True
  if view.GetPlantInfo() == gi.STATUS_UNKNOWN_PLANT:
    view.eat = joint_classify(view)
  
  # always eat, for data collection
  view.eat = True
  
  # view.direction = view.em.get_direction(view)
  view.direction = dir_within_z(view, 50)
  set_prev_state(view)

  return (view.direction, view.eat)