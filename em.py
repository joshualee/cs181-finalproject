import random
import numpy
from numpy import matrix
from numpy import linalg

import game_interface

class coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scale_coordinate(self, scalar):
        x = self.x * scalar
        y = self.y * scalar

        return coordinate(x, y)

    def __add__(self, other):
         x = self.x + other.x
         y = self.y + other.y
         coord = coordinate(x,y)

         return coord

    def __sub__(self, other):
         x = self.x - other.x
         y = self.y - other.y
         coord = coordinate(x,y)

         return coord

    def up(self):
        return coordinate(self.x, self.y + 1)
    def left(self):
        return coordinate(self.x - 1, self.y)
    def down(self):
        return coordinate(self.x, self.y - 1)
    def right(self):
        return coordinate(self.x + 1, self.y)

    def get_random_coordinate(max_x, max_y):
        x = random.randint(-max_x, max_x)
        y = random.randint(-max_y, max_y)

        return coordinate(x, y)

    def to_list(self):
        return [[self.x], [self.y]]

class covariance:
    def __init__(self, matrix_list):
        self.matrix = matrix(matrix_list)

    def get_random_covariance(max_variance):
        var_x = random.randint(0, max_variance)
        var_y = random.randint(0, max_variance)
        correlation = random.uniform(-1,1)

        symmetric_entry = correlation * var_x * var_y

        return covariance([[var_x**2, symmetric_entry][symmetric_entry, var_y**2]]

class EM:
    def __init__(self, max_x, max_y, clusters, max_variance = 5):

        '''
            We use the dimensions of the grid to initialize our EM object which
            models a mixture of Gaussians....

            max_x - Largest x value in our grid.
            max_y - Largest y value in our grid.
            clusters - Number of clusters we assume.
            max_variance - We choose a cap on the variance of the x and y
            coordinates for a single cluster.

        '''

        self.max_x = max_x
        self.max_y = max_y
        self.clusters = clusters
        self.initialize_parameters();
        self.data_points = []

    def initialize_paramters(self):

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

        for cluster in range(clusters):
            self.param_pi.append
                ( random.random() )
            self.param_mu.append
                ( coordinate.get_random_coordinate(max_y, max_y) )
            self.param_covariance.append
                ( covariance.get_random_covariance(max_variance) )

        # Normalize pi values
        pi_sum = sum(self.param_pi[cluster])
        for cluster in range(clusters):
            self.param_pi[cluster] / pi_sum

    def expectation(self):
        '''
            In the expectation step, we update the current posterior assignment
            probabilities.

            gammas[i][j] is the probablity that data point i is located in
            cluster j.

        '''
        num_data = len(self.data_points)
        self.gammas = [[0]*self.cluster]*num_data

        for data_point in self.data_point:
            for cluster in range(self.cluster):
                gamma[data][cluster] = mog_probability(data_point, cluster)

    def maximazation(self):
        '''
            The maximization step is responsible updating our parameters
            according to our predicted classifications.
        '''

        num_data = len(self.data_points)

        for cluster in range(self.clusters):
            # Number of data points we expect to belong to a cluster
            num_expected_cluster = sum(l[cluster] for l in self.gammas)

            ''' The new pi for a cluster k is the value is the sum of the k
                cluster for each of the data points '''
            self.param_pi[cluster] = num_expected_cluster / num_data

            ''' To calculate new mu for cluster k, we get the weighted sum of
                all the data points where our weights are the probability of
                appearing in cluster k. We then divide by the number of
                datapoints we expect in the cluster.  '''
            weighted_sum = reduce(lambda x, y: x+y:
                (v.scale_coordinate(p[cluster]) for
                    p,v in zip(self.gammas, self.data_points)))

            self.param_mu[cluster] = weighted_sum.scale_coordinate(1./num_expected_cluster)

            ''' To get the covariance we get the weighted sum of the matrix
                formed by multiplying the differnece of a point and its mean
                with the transpose of this 1x2 matrix. Like before, we weight
                by probability of appearing in cluster k, and divide by number
                of expected datapoints in the cluster. '''
            new_covariance = matrix([[0,0],[0,0]])
            for gamma,data_point in zip(self.gammas, self.data_points):
                mat = numpy.matrix( (data_point - self.param_mu[cluster]).to_list() )
                new_covariance += (mat * numpy.transpose(mat)) * gamma[cluster]

            self.covariance = new_covariance * (1./num_expected_cluster)

    def em_loop(self, iterations = None):
        '''
            Loops over expectation and maximization steps iteration times, or
            until convergence.
        '''

        converged = False

        if iterations:
            for i in iterations:
                self.expectation()
                self.maximization()
        else:
            while !converged:
                self.expectation()
                self.maximization()
                # Eventually might want some way to measure convergence
                if random.randint(0,181) == 181:
                    converged = True

    def add_data_point(self, x, y):
        '''
            When we encounter a new nutritious plant we add it to our list of
            data points.
        '''
        self.data_points.append(coordinate(x, y))

    def get_move(self, potential_moves):
        '''
            Given a list of coordinates, it returns the index of the coordinate
            that has the highest value on our probability density function.

        '''
        pdf = []
        for index,move in enumerate(potential_moves):
            pdf.append(0)
            for cluster in self.clusters:
                pdf[index] += mog_probability(move, cluster)

        return pdf.index(max(pdf))

    def get_direction(self, current_pos):
        '''
            Given the current position it will return which direction will
            yield the highest probability of finding a plant

        '''
        possible_directions= []
        possible_coordinates = []
        if current_pos.x + 1 <= max_x:
            possible_coordinates.append(current_pos.right())
            possible_directions.append(RIGHT)
        if current_pos.y -1 >= -max_x
            possible_coordinates.append(current_pos.left())
            possible_directions.append(LEFT)
        if current_pos.y + 1 <= max_y:
            possible_coordinates.append(current_pos.up())
            possible_directions.append(UP)
        if current_pos.y - 1 >= -max_y:
            possible_coordinates.append(current_pos.down())
            possible_directions.append(DOWN)

        best_move = self.get_move(possible_coordinates)
        return possible_directions[best_move]

    def mog_probability(self, data_point, cluster):
        '''
            Using a Mixture of Gaussian distirbution, it calculates the
            value of the PDF evaluated at data_point.
        '''

        pi = self.param_pi[cluster]
        mean = self.param_mu[cluster]
        covariance = self.param_mu[cluster]
        x_variance = numpy.sqrt(covariance[0][0])
        y_variance = numpy.sqrt(covariance[1][1])
        correlation = covariance[0][1] / x_variance / y_variance

        # http://en.wikipedia.org/wiki/Multivariate_normal_distribution#Density_function
        term1 = 1. / (2 * numpy.pi * x_variance * y_variance * numpy.sqrt(1-correlation**2))
        term2 = -1./(2 * (1-correlation**2))
        term3 = ((data_point.x-mean.x)**2)/x_variance**2
        term4 = ((data_point.y-mean.y)**2)/y_variance**2
        term5 = (2*correlation*(data_point.x - mean.x)*(data_point.y - mean.y))/(x_variance * y_variance)
        pdf = term1 * numpy.exp(term2*(term3 + term4 - term5))

        return pi * pdf
