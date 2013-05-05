import random
import json
from collections import defaultdict

RAW_DATA_FILENAME = 'data/raw_data.json'
DATA_FILENAME = 'data/data.json'

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

def create_nn_files(infile, training_size, validation_size, test_size):
  infile = open(infile, 'r')
  
  test_name = "32kset-test-{0}.json".format(test_size)
  validation_name = "32kset-validation-{0}.json".format(validation_size)
  training_name = "32kset-training-{0}.json".format(training_size)
  
  test = open(test_name, 'w')
  validation = open(validation_name, 'w')
  training = open(training_name, 'w')
  
  plants = []
  
  for line in infile:
    plants.append(json.loads(line))
  
  print len(plants)
  
  training_plants = random.sample(plants, training_size)
  for p in training_plants:
    training.write(json.dumps(p) + '\n')
    plants.remove(p)
  
  validation_plants = random.sample(plants, validation_size)
  for p in validation_plants:
    validation.write(json.dumps(p) + '\n')
    plants.remove(p)
  
  print len(plants)
  assert(len(plants) == test_size)
  test_plants = plants
  for p in test_plants:
    test.write(json.dumps(p) + '\n')  

if __name__ == '__main__':
  # get_data_stats(RAW_DATA_FILENAME)
  # get_data_stats(DATA_FILENAME)
  
  print "training"
  get_data_stats('32kset-training-22000.json')
  print "validation"
  get_data_stats('32kset-validation-5000.json')
  print "test"
  get_data_stats('32kset-test-5000.json')
  
  # num_nutritious = 12000
  # num_poisonous = 20000
  # outfile = 'data/{0}n_{1}p.json'.format(num_nutritious, num_poisonous)  
  # create_data_file(RAW_DATA_FILENAME, outfile, num_nutritious, num_poisonous)
  
  # create_nn_files('data/12000n_20000p.json', 22000, 5000, 5000)