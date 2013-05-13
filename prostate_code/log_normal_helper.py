import matplotlib.pyplot as plt
import math
import scipy.optimize
import scipy.integrate
import numpy.random

def log_normal_pdf(x, mu, sigma):
    a = math.exp(-1.0 * (pow(math.log(x) - mu, 2) / (2 * pow(sigma, 2))))
    b = x * sigma * pow(2 * math.pi, 0.5)
    return a/b


def plot_pdf(ax, mu, sigmas, label_f):

    num_points = 1000
    max_point = 5
    x_vals = [max_point * x / float(num_points) for x in xrange(1,num_points)]

    for sigma in sigmas:
        y_vals = [log_normal_pdf(x, mu, sigma) for x in x_vals]
        ax.plot(x_vals, y_vals, label = label_f(sigma))

def log_normal_mode(mu, sigma):
    ans = scipy.optimize.fmin(lambda x: -1.0 * log_normal_pdf(math.exp(x), mu, sigma), 0.5)
    return math.exp(ans)


