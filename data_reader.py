import json
from collections import defaultdict

def read_data(filename):  
  file = open(filename, 'r')
  rewards = defaultdict(int)
  plant_dict = {}
  
  count = 0
  bad_lines = 0
  total_reward = 0
  for line in file:
    print "Reading line {0}".format(count)
    count += 1
    
    if count == 1000:
      break
    
    try:
      plants, reward = json.loads(line)
    except ValueError:
      bad_lines += 1
      continue
    
    rewards[reward] += 1
    total_reward += reward
    
    for plant in plants:
      plant = str(plant)
      if plant in plant_dict:
       plant_dict[plant] += 1
      else:
        plant_dict[plant] = 1
  
  print "Total lines: {0}".format(count)
  print "Bad Lines: {0}".format(bad_lines)
  print "Total Reward: {0}".format(total_reward)
  print "Average Reward: {0}".format(total_reward/count)
  
  output = open('data/random_walk_summary.json', 'w')
  output.write(json.dumps(rewards) + "\n")
  output.write(json.dumps(plant_dict) + "\n")
      
if __name__ == '__main__':
  read_data('data/random_walk.json');