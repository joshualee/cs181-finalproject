import common
import data_collector
import qlearning
import simple_neural_net_player
import em.em_player

def get_move(view):
  return em_player.get_move(view)
  # return simple_neural_net_player.get_move(view)
  # return qlearning.get_move(view)
  # return data_collector.collect_data(view)
