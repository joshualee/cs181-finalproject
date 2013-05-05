import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import data_collector
import random_player
import qlearning