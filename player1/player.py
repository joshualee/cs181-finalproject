import common
import data_collector
import qlearning

def get_move(view):
  # return qlearning.get_move(view)
  return data_collector.collect_data(view)
