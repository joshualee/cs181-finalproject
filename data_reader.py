import json
from collections import defaultdict

def read_data(filename):  
  file = open(filename, 'r')

  n_plants = 0
  p_plants = 0
  for line in file:
    plants, reward = json.loads(line)
    if reward > 0:
      n_plants += 1
    else:
      p_plants += 1
  
  print 'Nutritious plants: {0}'.format(n_plants)
  print 'Poisonous plants:  {0}'.format(p_plants)
      
if __name__ == '__main__':
  read_data('data/data.json');