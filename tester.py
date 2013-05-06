import subprocess as sp
import re

def main():
  regexp = re.compile("Player (\d+) wins: (-?\d+) v. (-?\d+)")
  
  num_games = 100
  p1_wins = 0
  p2_wins = 0
  p1_score = 0.0
  p2_score = 0.0
  
  for i in range(num_games):
    output = sp.check_output([
      "python", "run_game.py",
      "--starting_life", "200",
      "-d", "0"
    ])
    
    match = regexp.search(output)
    
    if match == None:
      print output
      continue
    
    p_num, p1_s, p2_s = match.groups()
    
    print "{0}: Player {1} won {2} v. {3}".format(i, p_num, p1_s, p2_s)
    
    if int(p_num) == 1:
      p1_wins += 1
      p1_score += int(p1_s)
    else:
      p2_wins += 1
      p2_score += int(p2_s)
  
  print "Player 1 won: {0} with average score {1}".format(p1_wins, p1_score / num_games)
  print "Player 2 won: {0} with average score {1}".format(p2_wins, p2_score / num_games)

if __name__ == '__main__':
  main()