import random
import numpy
from numpy import matrix
from numpy import linalg

class Covariance:
    def __init__(self, matrix_list):
        self.matrix = matrix(matrix_list)

    @staticmethod
    def get_random_covariance(max_variance):
        var_x = random.uniform(1, max_variance)
        var_y = random.uniform(1, max_variance)
        correlation = random.uniform(-1,1)

        symmetric_entry = correlation * var_x * var_y

        return Covariance([[var_x**2, symmetric_entry],[symmetric_entry, var_y**2]])
