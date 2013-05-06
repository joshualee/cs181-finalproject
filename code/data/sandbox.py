import json

def compare_dict(d1, d2):
  for k in d1:
    if k in d2:
      assert d1[k] == d2[k], "{0}: d1[k]={1}, d2[k]={2}".format(k, d1[k], d2[k])

def main():
  d1_file = open('data/d1', 'r')
  d2_file = open('data/d2', 'r')
  d3_file = open('data/d3', 'r')
  d4_file = open('data/d4', 'r')
  
  d1 = json.loads(d1_file.read())
  d2 = json.loads(d2_file.read())
  d3 = json.loads(d3_file.read())
  d4 = json.loads(d4_file.read())
  
  compare_dict(d1, d2)
  
if __name__ == '__main__':
  main()