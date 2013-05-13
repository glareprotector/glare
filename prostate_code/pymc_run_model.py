import pymc
import sys
sys.path.insert(0,'/Library/Python/2.7/site-packages')
import pdb
import ucla_features as uf
import features as f
import basic_features as bf
import aggregate_features as af
import pandas
from helper import get_branded_version as brand
import numpy as np
import math
import helper


import matplotlib.pyplot as plt
import get_model
import random



attribute_fs = [brand(bf.hard_coded_f,'age')(1)]
num_attributes = len(attribute_fs)
pid_iterator = bf.restricted_pid_iterable(bf.all_ucla_pid_iterable(), 1)
X = bf.data_frame_feature_alternate(attribute_fs)(pid_iterator)
X_pop = bf.dataset_aggregate_f(bf.hard_coded_f(0.0), bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs)))(pid_iterator)
the_pid = iter(pid_iterator).next()

mu_pop_a, mu_pop_b, mu_pop_c = 0.5, 0.5, 1
sigma_mu_a, sigma_mu_b, sigma_mu_c = .01, .01, .1

M = get_model.get_model(X, X_pop, mu_pop_a, mu_pop_b, mu_pop_c, sigma_mu_a, sigma_mu_b, sigma_mu_c)


num_samples = 10000
max_time = 10
num_points = 5

M.sample(num_samples)

for pid in pid_iterator:

    #a_var = 'MM_a_%s' % pid
    a_var = 'MM_mu_%s_a' % pid
    b_var = 'MM_mu_%s_b' % pid
    c_var = 'MM_c_%s' % pid

    x_vals = np.zeros(num_points * num_samples)
    y_vals = np.zeros(num_points * num_samples)

    a_vals = np.zeros(num_samples)
    b_vals = np.zeros(num_samples)
    c_vals = np.zeros(num_samples)

    for a, b, c, i in zip(M.trace(a_var), M.trace(b_var), M.trace(c_var), xrange(num_samples)):
        
        this_x_vals = [random.random() * max_time for x in xrange(num_points)]
        this_y_vals = [get_model.f(x, 1.0, a, b, c) for x in this_x_vals]

        x_vals[(i*num_points):((i+1)*num_points)] = this_x_vals
        y_vals[(i*num_points):((i+1)*num_points)] = this_y_vals

        a_vals[i] = a
        b_vals[i] = b
        c_vals[i] = c




    fig = plt.figure()
    ax = fig.add_subplot(2,2,1)
    ax.scatter(x_vals, y_vals, s = 0.1)
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
