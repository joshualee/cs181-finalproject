from coordinate import Coordinate
from covariance import Covariance
import random
import game_interface as gi

import numpy
from numpy import matrix
from numpy import linalg

DIRECTIONS = [
  gi.RIGHT, 
  gi.LEFT, 
  gi.UP, 
  gi.DOWN
]

class EM:
    def __init__(self, clusters=3, max_x=25, max_y=25,
                       max_variance = 5, use_threshold = 5):

        '''
            Our EM object uses a mixture of gaussians model to generate a PDF
            of plant locations. We feed it the coordinates of nutritious plants
            when we happen across them, and use the expectation maxmimization
            algorithm to update our distribution. We use the dimensions of the
            grid to initialize our EM object.

            clusters - Number of clusters we assume.
            use_threshold - get_direction will return a random direction until
            it has observed at least this many plants.

            -- Parameter Initialization Variables --
            max_x - Cap for initializion of abs(mean x) value
            max_y - Cap for initialization of abs(mean y) value
            max_variance - Cap on the initialization variance of x and y

        '''

        self.clusters = clusters
        self.max_x = max_x
        self.max_y = max_y
        self.max_variance = max_variance
        self.use_threshold = use_threshold
        self.initialize_parameters();
        self.data_points = []

    def initialize_parameters(self):

        '''
            We randomly assign values to our parameters. Currently, these
            parameters are completely random, but can be adjusted to account
            for some information learned from offline learning.

            param_pi[k] denotes probability of a datapoint being in cluster k
            param_mu[k] is the mean value of a coordinate in cluster k
            param_covariance[k] is the covariance matrix of a cluster k

            
        '''

        self.param_pi = []
        self.param_mu = []
        self.param_covariance = []

        self.old_pi = []
        self.old_mu = []
        self.old_covariance = []

        for cluster in range(self.clusters):
            self.param_pi.append(random.random())
            self.param_mu.append(Coordinate.get_random_coordinate(self.max_x, self.max_y))
            self.param_covariance.append(Covariance.get_random_covariance(self.max_variance))

        # Normalize pi values
        pi_sum = sum(self.param_pi)
        self.param_pi = map(lambda pi: pi / pi_sum, self.param_pi)

    def expectation(self):
        '''
            In the expectation step, we update the current posterior assignment
            probabilities.

            gammas[i][j] is the probablity that data point i is located in
            cluster j.

        '''
        num_data = len(self.data_points)
        self.gammas = [[0]*self.clusters]*num_data

        for index, data_point in enumerate(self.data_points):
            for cluster in range(self.clusters):
                self.gammas[index][cluster] = \
                    self.mog_probability(data_point, cluster)

        # Normalize the gammas
        for cluster,gamma in enumerate(self.gammas):
            sum_gamma = sum(gamma)
            self.gammas[cluster] = map(lambda g: g/sum_gamma, gamma)

    def maximization(self):
        '''
            The maximization step is responsible for updating our parameters
            according to our predicted classifications.
        '''

        num_data = len(self.data_points)

        for cluster in range(self.clusters):
            # Number of data points we expect to belong to a cluster
            num_expected_cluster = sum(g[cluster] for g in self.gammas)

            ''' The new pi for a cluster k is the sum of the probabilities
                every data point is in that cluster. '''
            self.param_pi[cluster] = num_expected_cluster / num_data

            ''' To calculate new mu for cluster k, we get the weighted sum of
                all the data points where our weights are the probability of
                appearing in cluster k. We then divide by the number of
                datapoints we expect in the cluster. '''
            weighted_sum = reduce(lambda x, y: x+y, \
                    (v.scale_coordinate(p[cluster]) for \
                    p,v in zip(self.gammas, self.data_points)))

            self.param_mu[cluster] = weighted_sum.scale_coordinate(1./num_expected_cluster)

            ''' To get the covariance we get the weighted sum of the matrix
                formed by multiplying the differnece of a point and its mean
                with the transpose of this 1x2 matrix. Like before, we weight
                by probability of appearing in cluster k, and divide by number
                of expected datapoints in the cluster. '''
            new_covariance = matrix([[0,0],[0,0]])
            for p,v in zip(self.gammas, self.data_points):
                mat = numpy.matrix( (v - self.param_mu[cluster]).to_list() )
                new_covariance += (mat * numpy.transpose(mat)) * p[cluster]

            self.param_covariance[cluster].matrix = new_covariance * (1./num_expected_cluster)

    def train(self, iterations = None):
        '''
            Loops over expectation and maximization steps iteration times, or
            until convergence.
        '''

        converged = False

        # If we have no data we can't train
        if len(self.data_points) == 0:
            return

        if iterations:
            for i in range(iterations):
                self.expectation()
                self.maximization()
        else:
            while not converged:
                self.expectation()
                self.maximization()
                # Eventually might want some way to measure convergence
                if random.randint(0,181) == 181:
                    converged = True

    def best_move(self, potential_moves):
        '''
            Given a list of coordinates, it returns the index of the coordinate
            that has the highest value on our probability density function.

        '''
        pdf = []
        for index,move in enumerate(potential_moves):
            pdf.append(0)
            # Sum probability at position for each cluster
            for cluster in range(self.clusters):
                pdf[index] += self.mog_probability(move, cluster)

        return pdf.index(max(pdf))

    def get_direction(self, view):
        '''
            Given the current position it will return which direction will
            yield the highest probability of finding a plant

        '''
        if len(self.data_points) < self.use_threshold:
            return random.choice(DIRECTIONS)

        current_pos = Coordinate(view.GetXPos(), view.GetYPos())
        possible_directions= DIRECTIONS
        possible_coordinates = []

        possible_coordinates.append(current_pos.right())
        possible_coordinates.append(current_pos.left())
        possible_coordinates.append(current_pos.up())
        possible_coordinates.append(current_pos.down())

        best_move = self.best_move(possible_coordinates)

        return possible_directions[best_move]

    def mog_probability(self, data_point, cluster):
        '''
            Using a Mixture of Gaussian distirbution, it calculates the
            value of the PDF evaluated at data_point.
        '''

        pi = self.param_pi[cluster]
        mean = self.param_mu[cluster]
        covariance = self.param_covariance[cluster]

        x_variance = numpy.sqrt(covariance.matrix[0,0])
        y_variance = numpy.sqrt(covariance.matrix[1,1])
        correlation = covariance.matrix[0,1] / x_variance / y_variance

        # http://en.wikipedia.org/wiki/Multivariate_normal_distribution#Density_function
        term1 = 1. / (2 * numpy.pi * x_variance * y_variance * numpy.sqrt(1-correlation**2))
        term2 = -1./(2 * (1-correlation**2))
        term3 = ((data_point.x-mean.x)**2)/x_variance**2
        term4 = ((data_point.y-mean.y)**2)/y_variance**2
        term5 = (2*correlation*(data_point.x - mean.x)*(data_point.y - mean.y))/(x_variance * y_variance)
        pdf = term1 * numpy.exp(term2*(term3 + term4 - term5))

        return pi * pdf

    def add_data_point(self, x, y):
        '''
            When we encounter a new nutritious plant we add it to our list of
            data points.
        '''
        self.data_points.append(Coordinate(x, y))
