import pymc
import pdb
import matplotlib.pyplot as plt
import numpy as np
from pymc_real import *
import random


###############################################
# generate samples from the joint distribution#
###############################################


prior_variables = [MM_sigma_mu_a, MM_B_mu_a, MM_sigma_epsilon_mu_a, VM_epsilon_i_mu_a, VM_mu_i_a, \
                       VM_rho_i_a, \
                       VM_a_i, \
                       MM_sigma_mu_b, MM_B_mu_b, MM_sigma_epsilon_mu_b, VM_epsilon_i_mu_b, VM_mu_i_b, \
                       VM_rho_i_b, \
                       VM_b_i, \
                       MM_sigma_mu_c, MM_B_mu_c, VM_mu_i_c, \
                       VM_c_i]



M = pymc.MCMC(prior_variables)

num_samples = 150000

M.sample(num_samples)



max_time = 10
num_points = 5

for pid in pid_iterator:

    #a_var = 'MM_a_%s' % pid
    a_var = 'MM_mu_%s_a' % pid
    b_var = 'MM_b_%s' % pid
    c_var = 'MM_c_%s' % pid

    x_vals = np.zeros(num_points * num_samples)
    y_vals = np.zeros(num_points * num_samples)

    a_vals = np.zeros(num_samples)
    b_vals = np.zeros(num_samples)
    c_vals = np.zeros(num_samples)

    for a, b, c, i in zip(M.trace(a_var), M.trace(b_var), M.trace(c_var), xrange(num_samples)):
        
        this_x_vals = [random.random() * max_time for x in xrange(num_points)]
        this_y_vals = [f(x, 1.0, a, b, c) for x in this_x_vals]

        x_vals[(i*num_points):((i+1)*num_points)] = this_x_vals
        y_vals[(i*num_points):((i+1)*num_points)] = this_y_vals

        a_vals[i] = a
        b_vals[i] = b
        c_vals[i] = c


    fig = plt.figure()
    ax = fig.add_subplot(2,2,1)
    ax.scatter(x_vals, y_vals, s = 0.001)
    ax.set_xlim([0,10])
    #ax.set_ylim([0,1])
    ax.set_title('f')

    ax = fig.add_subplot(2,2,2)
    ax.hist(a_vals, bins = 50)
    ax.set_title('a')

    ax = fig.add_subplot(2,2,3)
    ax.hist(b_vals, bins = 50)
    ax.set_title('b')

    ax = fig.add_subplot(2,2,4)
    ax.hist(c_vals, bins = 50)
    ax.set_title('c')


    plt.show()

    pdb.set_trace()
    









samples = M.trace('MM_a_10105')[:]
print np.std(samples)
plt.hist(samples)
plt.show()

pdb.set_trace()
