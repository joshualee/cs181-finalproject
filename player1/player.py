import common
import data_collector
import qlearning
import simple_neural_net_player
import em
import dt

def get_move(view):
  # return dt.simple_dt_player.get_move(view)
  return em.em_player.get_move(view)
  # return simple_neural_net_player.get_move(view)
  # return qlearning.get_move(view)
  # return data_collector.collect_data(view)
