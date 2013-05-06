import pickle

def save_neural_network(network, outfile):
  outfile = open(outfile, 'w')
  outfile.write(pickle.dumps(network))

def load_neural_network(infile):
  infile = open(infile, 'r')
  network = pickle.loads(infile.read())
  return network
