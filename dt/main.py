# main.py
# -------
# Joshua Lee

from dtree import *
import sys
import utils
import collections
import matplotlib.pyplot as plt
from pylab import *
import math
import json

class Globals:
    noisyFlag = False
    pruneFlag = False
    valSetSize = 0
    dataset = None

##Classify
#---------

def classify(decisionTree, example):
    return decisionTree.predict(example)

##Learn
#-------
def learn(dataset):
    learner = DecisionTreeLearner(max_depth=dataset.max_depth)
    learner.train(dataset)
    return learner.dt

# main
# ----
# The main program loop
# You should modify this function to run your experiments

def parseArgs(args):
  """Parses arguments vector, looking for switches of the form -key {optional value}.
  For example:
    parseArgs([ 'main.py', '-n', '-p', 5 ]) = { '-n':True, '-p':5 }"""
  args_map = {}
  curkey = None
  for i in xrange(1, len(args)):
    if args[i][0] == '-':
      args_map[args[i]] = True
      curkey = args[i]
    else:
      assert curkey
      args_map[curkey] = args[i]
      curkey = None
  return args_map

def validateInput(args):
    args_map = parseArgs(args)
    valSetSize = 0
    noisyFlag = False
    pruneFlag = False
    boostRounds = -1
    maxDepth = -1
    if '-n' in args_map:
      noisyFlag = True
    if '-p' in args_map:
      pruneFlag = True
      valSetSize = int(args_map['-p'])
    if '-d' in args_map:
      maxDepth = int(args_map['-d'])
    if '-b' in args_map:
      boostRounds = int(args_map['-b'])
    return [noisyFlag, pruneFlag, valSetSize, maxDepth, boostRounds]

# returns the key that has the maximum corresponding value (int)
def max_key_in_dict(d):
    return max(d.items(), key=lambda x: x[1])[0]

def accuracy(tree, dataset, set=False):
    # no examples to test
    if len(dataset.examples) == 0:
        return 0
    
    correct = 0
    for example in dataset.examples:
        answer = example.attrs[-1]
        prediction = classify(tree, example) if not set else weighted_classify(tree, example)
        if answer == prediction:
            correct += 1        
            
    return float(correct) / len(dataset.examples)

def filter_data(dataset, branch, k):
    filtered_examples = filter(lambda e: e.attrs[branch.attr] == k, dataset.examples)
    return DataSet(filtered_examples, values=dataset.values)

def prune(current, validation_data):
    if current.nodetype == DecisionTree.LEAF:
        return current
        
    for k, sub_tree in current.branches.iteritems():
        # only pass the data that applies to the branch we are pruning
        # this allows our recursive method to stay clean and not have
        # to keep pointers to things like the parents or roots
        filtered_data = filter_data(validation_data, current, k)
        current.branches[k] = prune(sub_tree, filtered_data)  
        
    # use attr_count to find majority label
    label_count = collections.defaultdict(int)
    for sub_tree in current.branches.values():
        # branch cannot be pruned unless all children are leaf nodes
        if sub_tree.nodetype == DecisionTree.NODE:
            return current
        label_count[sub_tree.classification] += 1
    majority = max_key_in_dict(label_count)
        
    no_prune_score = accuracy(current, validation_data)
        
    # test pruned tree
    new_leaf = DecisionTree(DecisionTree.LEAF, classification=majority)
    with_prune_score = accuracy(new_leaf, validation_data)
        
    if with_prune_score >= no_prune_score:
        return new_leaf
    else:
        return current        

def partition_dataset(dataset, validation_size, fold, num_folds):
    num_examples = len(dataset.examples) / 2 # divde by 2 because we doubled the list for convenience
    test_start, test_end = fold * num_folds, (fold + 1) * num_folds
    validation_start, validation_end = test_end, test_end + validation_size
    training_start, training_end = validation_end, validation_end + num_examples - num_folds - validation_size
            
    test_set = DataSet(dataset.examples[test_start:test_end], values=dataset.values)
    validation_set = DataSet(dataset.examples[validation_start:validation_end], values=dataset.values)
    training_set = DataSet(dataset.examples[training_start:training_end], values=dataset.values)
    test_set.max_depth, test_set.num_rounds = dataset.max_depth, dataset.num_rounds
    validation_set.max_depth, validation_set.num_rounds = dataset.max_depth, dataset.num_rounds
    training_set.max_depth, training_set.num_rounds = dataset.max_depth, dataset.num_rounds
    
    return test_set, validation_set, training_set
    
def weighted_classify(trees, example):
    votes = collections.defaultdict(float)
    for tree in trees:
        vote = tree.predict(example)
        votes[vote] += tree.weight
    majority = max_key_in_dict(votes)
    return majority

# For HW1 problem 2a
def do_p2a(dataset):
    num_folds = 10
    avg_training_performance = 0.0
    avg_test_performance = 0.0
    
    for fold in range(num_folds):
        # partition the test and training set
        test_start, test_end = fold * num_folds, (fold + 1) * num_folds
        
        test_set = DataSet(dataset.examples[test_start:test_end], values=dataset.values)
        training_set = DataSet(dataset.examples[test_end:test_end+90], values=dataset.values)
        
        # create decision tree based on training set and test accuracy
        tree = learn(training_set)
        training_accuracy = accuracy(tree, training_set)
        
        # test accuracy of tree based on test data
        test_accuracy = accuracy(tree, test_set)
        
        # update accumulators
        avg_training_performance += training_accuracy
        avg_test_performance += test_accuracy
        
    avg_training_performance /= num_folds
    avg_test_performance /= num_folds
    
    print "Cross validated training performance = {0}".format(avg_training_performance)
    print "Cross validated test performance     = {0}".format(avg_test_performance)

# For HW1 problem 2b
def do_pruning(dataset, validation_max, noisy_flag):
    num_folds = 10
    validation_range = range(1, validation_max+1)
    training_performances = []
    test_performances = []
    
    for validation_size in validation_range:
        avg_training_performance = 0.0
        avg_test_performance = 0.0
        for fold in range(num_folds):
            # partition the test, training, and validation set
            test_set, validation_set, training_set = partition_dataset(dataset, validation_size, fold, num_folds)
            
            # create decision tree based on training set and test accuracy
            tree = learn(training_set)
            prune(tree, validation_set)
            
            training_accuracy = accuracy(tree, training_set)
            test_accuracy = accuracy(tree, test_set)
        
            # update accumulators
            avg_training_performance += training_accuracy
            avg_test_performance += test_accuracy
        
        training_performances.append(avg_training_performance/num_folds)
        test_performances.append(avg_test_performance/num_folds)
    
    
    if noisy_flag: graph_title = "Pruning | Noisy"
    else: graph_title = "Pruning | Non-Noisy"
    
    # plot the data
    
    plt.clf()
    training_plot, = plt.plot(validation_range, training_performances, color='b')
    test_plot, = plt.plot(validation_range, test_performances, color='r')
    plt.title(graph_title)
    plt.xlabel("Validation Set Size")
    plt.ylabel("Cross Validated Performance")
    plt.legend((training_plot, test_plot), ("Training", "Test"), "lower right")
    savefig(graph_title + ".pdf") # save the figure to a file
    plt.show() # show the figure

def reset_weights(dataset):
    total = len(dataset.examples) / 2 # divide by 2 because we duplicate list for convenience during partitioning
    total *= 0.9
    for e in dataset.examples:
        e.weight = 1. / total

def normalize_weights(dataset):
    total_weight = sum(map(lambda e: e.weight, dataset.examples))

    for e in dataset.examples:
        e.weight = e.weight / float(total_weight)

def adaboost(dataset, trees=[]):
    if dataset.num_rounds <= 0:
        return trees
    
    new_tree = learn(dataset)
    
    # calculate hypothesis weight
    e_r = 0.0
    for e in dataset.examples:
        answer = e.attrs[-1]
        prediction = new_tree.predict(e)
        if answer != prediction:
            e_r += e.weight
    
    # if there is no training error, return the "perfect" tree
    if e_r == 0.0:
        new_tree.weight = 1.0
        return [new_tree]
    
    a_r = math.log((1-e_r)/e_r)/2
    new_tree.weight = a_r
    
    # update weights
    for e in dataset.examples:
        answer = e.attrs[-1]
        prediction = new_tree.predict(e)
        exp = -a_r if answer == prediction else a_r
        e.weight *= pow(math.e, exp)
    
    normalize_weights(dataset)
    
    trees.append(new_tree)
    dataset.num_rounds -= 1
    return adaboost(dataset, trees=trees)

# For HW1 p3    
def do_boosting(dataset, noisy_flag):
    num_folds = 10
    part_a = True
    part_b = False
    
    if part_a:    
        avg_training_performance = 0.0
        avg_test_performance = 0.0
        for fold in range(num_folds):
            reset_weights(dataset)
            # partition the test, training, and validation set
            test_set, _, training_set = partition_dataset(dataset, 0, fold, num_folds)
            
            # create set of decision trees based on training set and test accuracy
            trees = adaboost(training_set, trees=[])
            training_accuracy = accuracy(trees, training_set, set=True)
            test_accuracy = accuracy(trees, test_set, set=True)
            
            # update accumulators
            avg_training_performance += training_accuracy
            avg_test_performance += test_accuracy
        
        avg_training_performance /= num_folds
        avg_test_performance /= num_folds
    
        print "Cross validated training performance (with boosting) = {0}".format(avg_training_performance)
        print "Cross validated test performance (with boosting)     = {0}".format(avg_test_performance)
    
    if part_b:
        boosting_rounds = range(1, 31)
        training_performances = []
        test_performances = []
        
        for b_rounds in boosting_rounds:
            dataset.num_rounds = b_rounds
            avg_training_performance = 0.0
            avg_test_performance = 0.0
            
            for fold in range(num_folds):
                reset_weights(dataset)
                # partition the test, training, and validation set
                test_set, _, training_set = partition_dataset(dataset, 0, fold, num_folds)
            
                # create set of decision trees based on training set and test accuracy
                trees = adaboost(training_set, trees=[])

                training_accuracy = accuracy(trees, training_set, set=True)
                test_accuracy = accuracy(trees, test_set, set=True)
            
                # update accumulators
                avg_training_performance += training_accuracy
                avg_test_performance += test_accuracy
            
            training_performances.append(avg_training_performance/num_folds)
            test_performances.append(avg_test_performance/num_folds)
    
        if noisy_flag: graph_title = "Boosting | Noisy"
        else: graph_title = "Boosting | Non-Noisy"
        
        # Plot the data
        plt.clf()
        training_plot, = plt.plot(boosting_rounds, training_performances, color='b')
        test_plot, = plt.plot(boosting_rounds, test_performances, color='r')
        plt.title(graph_title)
        plt.xlabel("Boosting Rounds")
        plt.ylabel("Cross Validated Performance")
        plt.legend((training_plot, test_plot), ("Training", "Test"), "lower right")
        savefig(graph_title + ".pdf") # save the figure to a file
        plt.show() # show the figure
    
    
def main():
    arguments = validateInput(sys.argv)
    noisyFlag, pruneFlag, valSetSize, maxDepth, boostRounds = arguments
    print noisyFlag, pruneFlag, valSetSize, maxDepth, boostRounds

    # Read in the data file
    
    f = open("../data/100n_200p.json")
    # f = open("../data/12000n_20000p.json")
    
    data = []
    
    for line in f:
      plant, reward = json.loads(line)
      if reward == -1:
        reward = 0
      
      plant.append(reward)
      data.append(Example(plant))
      
    dataset = DataSet(data)
    
    # Copy the dataset so we have two copies of it
    examples = dataset.examples[:]
 
    dataset.examples.extend(examples)
    dataset.max_depth = maxDepth
    if boostRounds != -1:
      dataset.use_boosting = True
      dataset.num_rounds = boostRounds
    
    p2a = not (pruneFlag or dataset.use_boosting)
    p2b = pruneFlag
    p3 = dataset.use_boosting
    
    if(p2a):
        do_p2a(dataset)
    
    if (p2b):
        do_pruning(dataset, valSetSize, noisyFlag)
        
    if (p3):
        do_boosting(dataset, noisyFlag)

main()