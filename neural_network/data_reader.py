import json

class Image:
  def __init__(self, label):
    self.pixels = []
    self.label = label

class DataReader:
  @staticmethod
  def GetImages(filename, limit):
    """Returns a list of image objects
    filename: The file to read in
    limit: The maximum number of images to read.  -1 = no limit
    """
    images = []
    infile = open(filename, 'r')
    
    for line in infile:
      plant, reward = json.loads(line)
      
      if reward == -1:
        reward = 0
      
      image = Image(reward)
      image.pixels = plant[:]
      images.append(image)
        
    return images

  @staticmethod
  def DumpWeights(weights, filename):
    """Dump the weights vector to filename"""
    outfile = open(filename, 'w')
    for weight in weights:
      outfile.write('%r\n' % weight)

  @staticmethod
  def ReadWeights(filename):
    """Returns a weight vector retrieved by reading file filename"""
    infile = open(filename, 'r')
    weights = []
    for line in infile:
      weight = float(line.strip())
      weights.append(weight)
