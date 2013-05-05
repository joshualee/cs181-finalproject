import random
import json
from collections import defaultdict

RAW_DATA_FILENAME = 'data/raw_data.json'

def get_data_stats(filename):  
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


def create_data_file(infile, outfile, num_nutritious, num_poisonous):
  infile = open(infile, 'r')
  outfile = open(outfile, 'w')
  
  n_plants = []
  p_plants = []
  
  # read the plants into memory
  for line in infile:
    plant, reward = json.loads(line)
    
    if reward > 0:
      n_plants.append(plant)
    else:
      p_plants.append(plant)
  
  n_p = float(num_nutritious) / (num_nutritious + num_poisonous)
  
  n_samples = random.sample(n_plants, num_nutritious)
  p_samples = random.sample(p_plants, num_poisonous)
  
  while len(n_samples) > 0 or len(p_samples) > 0:
    if (random.uniform(0,1) <= n_p and len(n_samples) != 0) or len(p_samples) == 0:
      n = n_samples.pop()
      outfile.write(json.dumps((n, 1)) + '\n')
    else:
      p = p_samples.pop()
      outfile.write(json.dumps((p, -1)) + '\n')

if __name__ == '__main__':
  # get_data_stats(RAW_DATA_FILENAME);
  num_nutritious = 1000
  num_poisonous = 2000
  outfile = 'data/{0}n_{1}p.json'.format(num_nutritious, num_poisonous)
  
  create_data_file(RAW_DATA_FILENAME, outfile, num_nutritious, num_poisonous)