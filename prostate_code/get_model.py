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
import random

import get_model_helper

"""
convention: to denote x_a^b, write x_a_b
variables of model prefaced with MM_
variables that represent observed values preceded with DD_ (this is underspecified)
vectors of observed variables preceded with VD_
vector variables of models prefaced with VM_
need to choose squashing function range so that input to g_{\mu}^a is generally close to 0.
for variables for which there is one for each patient, store in dictionary indexed by pid
"""

def f(t, s, a, b, c):
    return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*t/c))



def get_curve_parameters(series):
    """
    given a curve, returns the a b c curve parameters
    raises exception if no fxn value at time 0
    """
    def f_wrapped(t, a, b, c):
        return f(t, s, a, b, c)

def plot_a_for_several_l_a(ax, num_samples, a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_as, l_b, l_c):

    num_bins = 50

    for l_a in l_as:
        M, pid = get_one_sample_model(a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c)
        M.sample(num_samples)
        a_var = 'MM_a_%s' % pid
        ax.hist(M.trace(a_var)[:], bins = num_bins, histtype = 'step', normed = True, label = r'$\lambda^a=$'+str(l_a))
    
    return ax


def plot_c_for_several_l_c(ax, num_samples, a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_cs):

    num_bins = 50

    for l_c in l_cs:
        M, pid = get_one_sample_model(a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c)
        M.sample(num_samples)
        c_var = 'MM_c_%s' % pid
        ax.hist(M.trace(c_var)[:], bins = num_bins, histtype = 'step', normed = True, label = r'$\lambda^c=$'+str(l_c))
    
    return ax

def plot_curve_prior(ax, num_samples, a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c):

    M, pid = get_one_sample_model(a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c)

    M.sample(num_samples)

    max_time = 10
    num_points = 5

    a_var = 'MM_a_%s' % pid
    b_var = 'MM_b_%s' % pid
    c_var = 'MM_c_%s' % pid

    x_vals = np.zeros(num_points * num_samples)
    y_vals = np.zeros(num_points * num_samples)

    import itertools

    for a, b, c, i in itertools.izip(M.trace(a_var), M.trace(b_var), M.trace(c_var), xrange(num_samples)):
        
        this_x_vals = [random.random() * max_time for x in xrange(num_points)]
        this_y_vals = [f(x, 1.0, a, b, c) for x in this_x_vals]

        x_vals[(i*num_points):((i+1)*num_points)] = this_x_vals
        y_vals[(i*num_points):((i+1)*num_points)] = this_y_vals

    
    a_vals = M.trace(a_var)[:]
    b_vals = M.trace(b_var)[:]
    c_vals = M.trace(c_var)[:]

    ax.scatter(x_vals, y_vals, s = 0.003)
    ax.set_xlim([0,10])
    #ax.set_ylim([0,1])
    #ax.set_title('f')
    ax.set_xlabel('$t$')
    ax.set_ylabel('$f(t)$')
    return ax



def plot_simple_dashboard_mus(fig, num_samples, a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c):
    """
    plots mu_a, mu_b, mu_c and curves based on them
    """


    M, pid = get_one_sample_model(a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c)

    M.sample(num_samples)

    max_time = 10
    num_points = 5

    a_var = 'MM_mu_%s_a' % pid
    b_var = 'MM_mu_%s_b' % pid
    c_var = 'MM_mu_%s_c' % pid

    a_var = 'MM_a_%s' % pid
    b_var = 'MM_b_%s' % pid
    c_var = 'MM_c_%s' % pid

    x_vals = np.zeros(num_points * num_samples)
    y_vals = np.zeros(num_points * num_samples)

    import itertools

    for a, b, c, i in itertools.izip(M.trace(a_var), M.trace(b_var), M.trace(c_var), xrange(num_samples)):
        
        this_x_vals = [random.random() * max_time for x in xrange(num_points)]
        this_y_vals = [f(x, 1.0, a, b, c) for x in this_x_vals]

        x_vals[(i*num_points):((i+1)*num_points)] = this_x_vals
        y_vals[(i*num_points):((i+1)*num_points)] = this_y_vals

        #a_vals[i] = a
        #b_vals[i] = b
        #c_vals[i] = c
    
    a_vals = M.trace(a_var)[:]
    b_vals = M.trace(b_var)[:]
    c_vals = M.trace(c_var)[:]

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

    return fig


def get_one_sample_model(a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c):

    attribute_fs = [brand(bf.hard_coded_f,'age')(1)]
    num_attributes = len(attribute_fs)
    pid_iterator = bf.restricted_pid_iterable(bf.all_ucla_pid_iterable(), 1)
    X = bf.data_frame_feature_alternate(attribute_fs)(pid_iterator)
    X_pop = bf.dataset_aggregate_f(bf.hard_coded_f(0.0), bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs)))(pid_iterator)
    the_pid = iter(pid_iterator).next()

    M = get_model(X, X_pop, a_pop, b_pop, c_pop, sigma_a, sigma_b, sigma_c, l_a, l_b, l_c)

    return M, the_pid


def get_model(X, X_pop, a_pop, b_pop, c_pop, sigma_mu_a, sigma_mu_b, sigma_mu_c, l_a, l_b, l_c):
    """
    would be nice if i could go in and change 
    """



    ########################
    # define some variables#
    ########################

    pid_iterator = X.index
    num_attributes = X.shape[1]

    #####################################
    # define functions used in the model#
    #####################################

    """
    define squashing function for \mu_i^a and its inverse
    squashing function is logistic function, and it is scaled to have range(0, r_mu_a)
    """
    r_mu_a = 1.0

    def g_mu_a(x):
        return r_mu_a / (1.0 + math.exp(-1.0 * x))

    def g_mu_a_inv(y):
        c = 1.0 / r_mu_a
        return math.log((c*y)/(1-c*y))

    g_mu_b = g_mu_a
    g_mu_b_inv = g_mu_a_inv

    def g_mu_c(x):
        return math.exp(x)

    def g_mu_c_inv(y):
        return math.log(y)

    """
    define function f that takes in curve parameters, time, and returns the ture value at that time
    at time 0, level is a + (1-b)(1-a).  asymptotic drop is a
    """

    def f(t, s, a, b, c):
        return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*c*t))


    ###################################
    # define some model constants here#
    ###################################
    MM_sigma_mu_a_initial = sigma_mu_a
    MM_rho_i_a_initial = 0.2
    MM_sigma_mu_b_initial = sigma_mu_b
    MM_rho_i_b_initial = 0.2
    MM_sigma_mu_c_initial = sigma_mu_c
    MM_rho_i_c_initial = 0.2

    K_sigma_mu_a = 100
    K_sigma_mu_b = 100
    K_sigma_mu_c = 100
    K_epsilon_mu_a = 20
    K_epsilon_mu_b = 20



    mu_pop_a = a_pop
    mu_pop_b = b_pop
    mu_pop_c = c_pop

    mu_pop_a_prime = g_mu_a_inv(mu_pop_a)
    mu_pop_b_prime = g_mu_b_inv(mu_pop_b)
    mu_pop_c_prime = g_mu_c_inv(mu_pop_c)






    ################################
    # define variables of the model#
    ################################

    ####################
    # model for \mu_i^a#
    ####################

    """
    define B_{\mu}^a to be multivariate normal centered at 0, covariance sigma_{\mu}^a * I
    define sigma_{\mu}^a to be uniform(0, K_sigma_{\mu}^a)
    define K_sigma_{\mu}^{\mu,a} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_mu_a(value = MM_sigma_mu_a_initial, max = K_sigma_mu_a):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = False)
    def MM_B_mu_a(value = np.zeros(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i for a single i.  later, will generalize
    define \mu_pop^{a'} to be such that g_{\mu}^a(\mu_pop^{a'}} = \mu_pop^a
    define \mu_i^a = g_{\mu}^a(\mu_pop^{a') + (X_i - X_pop) * B_{\mu}^a + \epsilon_i^{\mu, a})
    define \epsilon_i^{\mu, a} to be normal(0, \sigma_{\epsilon}^{\mu, a})
    define \sigma_{\epsilon}^{\mu, a} to be uniform(0, K_{\epsilon}^{\mu,a})
    define K_{\epsilon}^{\mu,a} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_epsilon_mu_a(value = .08, max = K_epsilon_mu_a):
        return pymc.distributions.uniform_like(value, 0, max)


    VM_epsilon_i_mu_a = {}
    VM_mu_i_a = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_a', pid))
        def MM_mu_i_a(anchor = mu_pop_a_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_a):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_a(anchor + inside)
            return ans

        VM_epsilon_i_mu_a[pid] = MM_epsilon_i_mu_a
        VM_mu_i_a[pid] = MM_mu_i_a




    #####################
    # model for \rho_i^a#
    #####################


    """
    here, define model for \rho_i^a.  it will NOT depend on covariates
    \rho_i^a will be some diffuse distribution in (0,1).  let's say uniform for now
    """

    VM_rho_i_a = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_a', pid), observed = False)
        def MM_rho_i_a(value = MM_rho_i_a_initial):
            return helper.truncated_exponential_likelihood(value, l_a)
            return pymc.distributions.exponential_like(value, l_a)
            return pymc.distributions.uniform_like(value, 0, 1)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_a[pid] = MM_rho_i_a
    

    #################
    # model for a_i #
    #################

    """
    define a_i to be beta(\mu_i^a, \mu_i^a * \rho_i^a )
    """

    VM_a_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('a', pid), observed = False)
        def MM_a_i(value = 0.4, mu = VM_mu_i_a[pid], rho = VM_rho_i_a[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_a_i[pid] = MM_a_i


    ####################
    # model for \mu_i^b#
    ####################

    """
    define B_{\mu}^b to be multivariate normal centered at 0, covariance sigma_{\mu}^b * I
    define sigma_{\mu}^b to be uniform(0, K_sigma_{\mu}^b)
    define K_sigma_{\mu}^{\mu,b} to be some constant
    """

    @pymc.stochastic(observed = True)
    def MM_sigma_mu_b(value = MM_sigma_mu_b_initial, max = K_sigma_mu_b):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = False)
    def MM_B_mu_b(value = np.zeros(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i^b for a single i.  later, will generalize
    define \mu_pop^{b'} to be such that g_{\mu}^b(\mu_pop^{b'}} = \mu_pop^b
    define \mu_i^b = g_{\mu}^b(\mu_pop^{b') + (X_i - X_pop) * B_{\mu}^b + \epsilon_i^{\mu, b})
    define \epsilon_i^{\mu, b} to be normal(0, \sigma_{\epsilon}^{\mu, b})
    define \sigma_{\epsilon}^{\mu, b} to be uniform(0, K_{\epsilon}^{\mu,b})
    define K_{\epsilon}^{\mu,b} to be some constant
    """

    def MM_sigma_epsilon_mu_b(value = .08, max = K_epsilon_mu_b):
        return pymc.distributions.uniform_like(value, 0, max)


    VM_epsilon_i_mu_b = {}
    VM_mu_i_b = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = 'MM_epsilon_%s_mu_b' % pid,observed = True)
        def MM_epsilon_i_mu_b(value = 0, sigma = MM_sigma_epsilon_mu_b):
            return pymc.distributions.normal_like(value, 0, 1.0/pow(sigma,2))

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_b', pid))
        def MM_mu_i_b(anchor = mu_pop_b_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_b):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_b(anchor + inside)
            return ans

        VM_epsilon_i_mu_b[pid] = MM_epsilon_i_mu_b
        VM_mu_i_b[pid] = MM_mu_i_b




    #####################
    # model for \rho_i^b#
    #####################


    """
    here, define model for \rho_i^b.  it will NOT depend on covariates
    \rho_i^b will be some diffuse distribution in (0,1).  let's say uniform for now
    """

    VM_rho_i_b = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_b', pid), observed = False)
        def MM_rho_i_b(value = MM_rho_i_b_initial):
            return helper.truncated_exponential_likelihood(value, l_b)
            return pymc.distributions.exponential_like(value, l_b)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_b[pid] = MM_rho_i_b
    

    #################
    # model for b_i #
    #################

    """
    define b_i to be beta(\mu_i^b, \mu_i^b * \rho_i^b )
    """

    VM_b_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('b', pid), observed = False)
        def MM_b_i(value = 0.4, mu = VM_mu_i_b[pid], rho = VM_rho_i_b[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_b_i[pid] = MM_b_i


    #################
    # model for c_i #
    #################


    """
    define B_{\mu}^c to be multivariate normal centered at 0, covariance sigma_{\mu}^c * I
    define sigma_{\mu}^c to be uniform(0, K_sigma_{\mu}^c)
    define K_sigma_{\mu}^{\mu,c} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_mu_c(value = MM_sigma_mu_c_initial, max = K_sigma_mu_c):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = False)
    def MM_B_mu_c(value = np.zeros(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_c):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i_c for a single i.  later, will generalize
    define \mu_pop^{c'} to be such that g_{\mu}^c(\mu_pop^{c'}} = \mu_pop^c
    for now, define \mu_i^c = g_{\mu}^a(\mu_pop^{a') + (X_i - X_pop) * B_{\mu}^a). note the lack of noise.
    for now, define c_i = \mu_i_c
    """

    VM_mu_i_c = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_c', pid))
        def MM_mu_i_c(anchor = mu_pop_c_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_c):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_c(anchor + inside)
            return ans

        VM_mu_i_c[pid] = MM_mu_i_c


    VM_rho_i_c = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_c', pid), observed = True)
        def MM_rho_i_c(value = MM_rho_i_c_initial):
            #assert value > 0
            return pymc.distributions.exponential_like(value, l_c)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_c[pid] = MM_rho_i_c



    VM_c_i = {}

    for pid in pid_iterator:
        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('c', pid), observed = False)
        def MM_c_i(value = 0.4, mu = VM_mu_i_c[pid], rho = VM_rho_i_c[pid]):
            
            k, theta = helper.gamma_mu_phi_to_k_theta(mu, rho)
            rate = 1.0 / theta
            return pymc.distributions.gamma_like(value, k, rate)
            return mu

        VM_c_i[pid] = MM_c_i


    ####################
    # create the model #
    ####################    

    prior_variables = [MM_sigma_mu_a, MM_B_mu_a, MM_sigma_epsilon_mu_a, VM_epsilon_i_mu_a, VM_mu_i_a, \
                       VM_rho_i_a, \
                       VM_a_i, \
                       MM_sigma_mu_b, MM_B_mu_b, MM_sigma_epsilon_mu_b, VM_epsilon_i_mu_b, VM_mu_i_b, \
                       VM_rho_i_b, \
                       VM_b_i, \
                       MM_sigma_mu_c, MM_B_mu_c, VM_mu_i_c, \
                       VM_c_i]



    M = pymc.MCMC(prior_variables)

    return M


def get_model_abc_observed(X, X_pop, a_pop, b_pop, c_pop, sigma_mu_a, sigma_mu_b, sigma_mu_c, l_a, l_b, l_c, data):
    """
    a b c are observed for every patient.  this means for those variables, change it to observed.  first, name variables using that helper function
    """



    ########################
    # define some variables#
    ########################

    pid_iterator = X.index
    num_attributes = X.shape[1]

    #####################################
    # define functions used in the model#
    #####################################

    """
    define squashing function for \mu_i^a and its inverse
    squashing function is logistic function, and it is scaled to have range(0, r_mu_a)
    """
    r_mu_a = 1.0

    def g_mu_a(x):
        return r_mu_a / (1.0 + math.exp(-1.0 * x))

    def g_mu_a_inv(y):
        c = 1.0 / r_mu_a
        return math.log((c*y)/(1-c*y))

    g_mu_b = g_mu_a
    g_mu_b_inv = g_mu_a_inv

    def g_mu_c(x):
        return math.exp(x)

    def g_mu_c_inv(y):
        return math.log(y)

    """
    define function f that takes in curve parameters, time, and returns the ture value at that time
    at time 0, level is a + (1-b)(1-a).  asymptotic drop is a
    """

    def f(t, s, a, b, c):
        return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*c*t))


    ###################################
    # define some model constants here#
    ###################################
    MM_sigma_mu_a_initial = sigma_mu_a
    MM_rho_i_a_initial = 0.2
    MM_sigma_mu_b_initial = sigma_mu_b
    MM_rho_i_b_initial = 0.2
    MM_sigma_mu_c_initial = sigma_mu_c
    MM_rho_i_c_initial = 0.2

    K_sigma_mu_a = 100
    K_sigma_mu_b = 100
    K_sigma_mu_c = 100
    K_epsilon_mu_a = 20
    K_epsilon_mu_b = 20



    mu_pop_a = a_pop
    mu_pop_b = b_pop
    mu_pop_c = c_pop

    mu_pop_a_prime = g_mu_a_inv(mu_pop_a)
    mu_pop_b_prime = g_mu_b_inv(mu_pop_b)
    mu_pop_c_prime = g_mu_c_inv(mu_pop_c)






    ################################
    # define variables of the model#
    ################################

    ####################
    # model for \mu_i^a#
    ####################

    """
    define B_{\mu}^a to be multivariate normal centered at 0, covariance sigma_{\mu}^a * I
    define sigma_{\mu}^a to be uniform(0, K_sigma_{\mu}^a)
    define K_sigma_{\mu}^{\mu,a} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_mu_a(value = MM_sigma_mu_a_initial, max = K_sigma_mu_a):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = False)
    def MM_B_mu_a(value = np.zeros(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i for a single i.  later, will generalize
    define \mu_pop^{a'} to be such that g_{\mu}^a(\mu_pop^{a'}} = \mu_pop^a
    define \mu_i^a = g_{\mu}^a(\mu_pop^{a') + (X_i - X_pop) * B_{\mu}^a + \epsilon_i^{\mu, a})
    define \epsilon_i^{\mu, a} to be normal(0, \sigma_{\epsilon}^{\mu, a})
    define \sigma_{\epsilon}^{\mu, a} to be uniform(0, K_{\epsilon}^{\mu,a})
    define K_{\epsilon}^{\mu,a} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_epsilon_mu_a(value = .08, max = K_epsilon_mu_a):
        return pymc.distributions.uniform_like(value, 0, max)


    VM_epsilon_i_mu_a = {}
    VM_mu_i_a = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_a', pid))
        def MM_mu_i_a(anchor = mu_pop_a_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_a):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_a(anchor + inside)
            return ans


        VM_mu_i_a[pid] = MM_mu_i_a




    #####################
    # model for \rho_i^a#
    #####################


    """
    here, define model for \rho_i^a.  it will NOT depend on covariates
    \rho_i^a will be some diffuse distribution in (0,1).  let's say uniform for now
    """

    VM_rho_i_a = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_a', pid), observed = False)
        def MM_rho_i_a(value = MM_rho_i_a_initial):
            return helper.truncated_exponential_likelihood(value, l_a)
            return pymc.distributions.exponential_like(value, l_a)
            return pymc.distributions.uniform_like(value, 0, 1)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_a[pid] = MM_rho_i_a
    

    #################
    # model for a_i #
    #################

    """
    define a_i to be beta(\mu_i^a, \mu_i^a * \rho_i^a )
    """

    VM_a_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('a', pid), observed = True)
        def MM_a_i(value = data.get_value('a', pid), mu = VM_mu_i_a[pid], rho = VM_rho_i_a[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_a_i[pid] = MM_a_i


    ####################
    # model for \mu_i^b#
    ####################

    """
    define B_{\mu}^b to be multivariate normal centered at 0, covariance sigma_{\mu}^b * I
    define sigma_{\mu}^b to be uniform(0, K_sigma_{\mu}^b)
    define K_sigma_{\mu}^{\mu,b} to be some constant
    """

    @pymc.stochastic(observed = True)
    def MM_sigma_mu_b(value = MM_sigma_mu_b_initial, max = K_sigma_mu_b):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = False)
    def MM_B_mu_b(value = np.zeros(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i^b for a single i.  later, will generalize
    define \mu_pop^{b'} to be such that g_{\mu}^b(\mu_pop^{b'}} = \mu_pop^b
    define \mu_i^b = g_{\mu}^b(\mu_pop^{b') + (X_i - X_pop) * B_{\mu}^b + \epsilon_i^{\mu, b})
    define \epsilon_i^{\mu, b} to be normal(0, \sigma_{\epsilon}^{\mu, b})
    define \sigma_{\epsilon}^{\mu, b} to be uniform(0, K_{\epsilon}^{\mu,b})
    define K_{\epsilon}^{\mu,b} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_epsilon_mu_b(value = .08, max = K_epsilon_mu_b):
        return pymc.distributions.uniform_like(value, 0, max)


    VM_epsilon_i_mu_b = {}
    VM_mu_i_b = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_b', pid))
        def MM_mu_i_b(anchor = mu_pop_b_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_b):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_b(anchor + inside)
            return ans


        VM_mu_i_b[pid] = MM_mu_i_b




    #####################
    # model for \rho_i^b#
    #####################


    """
    here, define model for \rho_i^b.  it will NOT depend on covariates
    \rho_i^b will be some diffuse distribution in (0,1).  let's say uniform for now
    """

    VM_rho_i_b = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_b', pid), observed = False)
        def MM_rho_i_b(value = MM_rho_i_b_initial):
            return helper.truncated_exponential_likelihood(value, l_b)
            return pymc.distributions.exponential_like(value, l_b)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_b[pid] = MM_rho_i_b
    

    #################
    # model for b_i #
    #################

    """
    define b_i to be beta(\mu_i^b, \mu_i^b * \rho_i^b )
    """

    VM_b_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('b', pid), observed = True)
        def MM_b_i(value = data.get_value('b', pid), mu = VM_mu_i_b[pid], rho = VM_rho_i_b[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_b_i[pid] = MM_b_i


    #################
    # model for c_i #
    #################


    """
    define B_{\mu}^c to be multivariate normal centered at 0, covariance sigma_{\mu}^c * I
    define sigma_{\mu}^c to be uniform(0, K_sigma_{\mu}^c)
    define K_sigma_{\mu}^{\mu,c} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_mu_c(value = MM_sigma_mu_c_initial, max = K_sigma_mu_c):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = False)
    def MM_B_mu_c(value = np.zeros(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_c):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i_c for a single i.  later, will generalize
    define \mu_pop^{c'} to be such that g_{\mu}^c(\mu_pop^{c'}} = \mu_pop^c
    for now, define \mu_i^c = g_{\mu}^a(\mu_pop^{a') + (X_i - X_pop) * B_{\mu}^a). note the lack of noise.
    for now, define c_i = \mu_i_c
    """

    VM_mu_i_c = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_c', pid))
        def MM_mu_i_c(anchor = mu_pop_c_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_c):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_c(anchor + inside)
            return ans

        VM_mu_i_c[pid] = MM_mu_i_c


    VM_rho_i_c = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_c', pid), observed = True)
        def MM_rho_i_c(value = MM_rho_i_c_initial):
            #assert value > 0
            return pymc.distributions.exponential_like(value, l_c)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_c[pid] = MM_rho_i_c



    VM_c_i = {}

    for pid in pid_iterator:
        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('c', pid), observed = True)
        def MM_c_i(value = data.get_value('c', pid), mu = VM_mu_i_c[pid], rho = VM_rho_i_c[pid]):
            
            k, theta = helper.gamma_mu_phi_to_k_theta(mu, rho)
            rate = 1.0 / theta
            return pymc.distributions.gamma_like(value, k, rate)
            return mu

        VM_c_i[pid] = MM_c_i


    ####################
    # create the model #
    ####################    

    prior_variables = [MM_sigma_mu_a, MM_B_mu_a, MM_sigma_epsilon_mu_a, VM_epsilon_i_mu_a, VM_mu_i_a, \
                       VM_rho_i_a, \
                       VM_a_i, \
                       MM_sigma_mu_b, MM_B_mu_b, MM_sigma_epsilon_mu_b, VM_epsilon_i_mu_b, VM_mu_i_b, \
                       VM_rho_i_b, \
                       VM_b_i, \
                       MM_sigma_mu_c, MM_B_mu_c, VM_mu_i_c, \
                       VM_c_i]



    M = pymc.MCMC(prior_variables)

    return M



def get_model_Bs_fixed(X, X_pop, a_pop, b_pop, c_pop, sigma_mu_a, sigma_mu_b, sigma_mu_c, l_a, l_b, l_c, B_a, B_b, B_c):
    """
    would be nice if i could go in and change 
    """



    ########################
    # define some variables#
    ########################

    pid_iterator = X.index
    num_attributes = X.shape[1]

    #####################################
    # define functions used in the model#
    #####################################

    """
    define squashing function for \mu_i^a and its inverse
    squashing function is logistic function, and it is scaled to have range(0, r_mu_a)
    """
    r_mu_a = 1.0

    def g_mu_a(x):
        return r_mu_a / (1.0 + math.exp(-1.0 * x))

    def g_mu_a_inv(y):
        c = 1.0 / r_mu_a
        return math.log((c*y)/(1-c*y))

    g_mu_b = g_mu_a
    g_mu_b_inv = g_mu_a_inv

    def g_mu_c(x):
        return math.exp(x)

    def g_mu_c_inv(y):
        return math.log(y)

    """
    define function f that takes in curve parameters, time, and returns the ture value at that time
    at time 0, level is a + (1-b)(1-a).  asymptotic drop is a
    """

    def f(t, s, a, b, c):
        return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*c*t))


    ###################################
    # define some model constants here#
    ###################################
    MM_sigma_mu_a_initial = sigma_mu_a
    MM_rho_i_a_initial = 0.2
    MM_sigma_mu_b_initial = sigma_mu_b
    MM_rho_i_b_initial = 0.2
    MM_sigma_mu_c_initial = sigma_mu_c
    MM_rho_i_c_initial = 0.2

    K_sigma_mu_a = 100
    K_sigma_mu_b = 100
    K_sigma_mu_c = 100
    K_epsilon_mu_a = 20
    K_epsilon_mu_b = 20



    mu_pop_a = a_pop
    mu_pop_b = b_pop
    mu_pop_c = c_pop

    mu_pop_a_prime = g_mu_a_inv(mu_pop_a)
    mu_pop_b_prime = g_mu_b_inv(mu_pop_b)
    mu_pop_c_prime = g_mu_c_inv(mu_pop_c)






    ################################
    # define variables of the model#
    ################################

    ####################
    # model for \mu_i^a#
    ####################

    """
    define B_{\mu}^a to be multivariate normal centered at 0, covariance sigma_{\mu}^a * I
    define sigma_{\mu}^a to be uniform(0, K_sigma_{\mu}^a)
    define K_sigma_{\mu}^{\mu,a} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_mu_a(value = MM_sigma_mu_a_initial, max = K_sigma_mu_a):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = True)
    def MM_B_mu_a(value = B_a * np.eye(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i for a single i.  later, will generalize
    define \mu_pop^{a'} to be such that g_{\mu}^a(\mu_pop^{a'}} = \mu_pop^a
    define \mu_i^a = g_{\mu}^a(\mu_pop^{a') + (X_i - X_pop) * B_{\mu}^a + \epsilon_i^{\mu, a})
    define \epsilon_i^{\mu, a} to be normal(0, \sigma_{\epsilon}^{\mu, a})
    define \sigma_{\epsilon}^{\mu, a} to be uniform(0, K_{\epsilon}^{\mu,a})
    define K_{\epsilon}^{\mu,a} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_epsilon_mu_a(value = .08, max = K_epsilon_mu_a):
        return pymc.distributions.uniform_like(value, 0, max)


    VM_epsilon_i_mu_a = {}
    VM_mu_i_a = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_a', pid))
        def MM_mu_i_a(anchor = mu_pop_a_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_a):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_a(anchor + inside)
            return ans


        VM_mu_i_a[pid] = MM_mu_i_a




    #####################
    # model for \rho_i^a#
    #####################


    """
    here, define model for \rho_i^a.  it will NOT depend on covariates
    \rho_i^a will be some diffuse distribution in (0,1).  let's say uniform for now
    """

    VM_rho_i_a = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_a', pid), observed = False)
        def MM_rho_i_a(value = MM_rho_i_a_initial):
            return helper.truncated_exponential_likelihood(value, l_a)
            return pymc.distributions.exponential_like(value, l_a)
            return pymc.distributions.uniform_like(value, 0, 1)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_a[pid] = MM_rho_i_a
    

    #################
    # model for a_i #
    #################

    """
    define a_i to be beta(\mu_i^a, \mu_i^a * \rho_i^a )
    """

    VM_a_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('a', pid), observed = False)
        def MM_a_i(value = 0.4, mu = VM_mu_i_a[pid], rho = VM_rho_i_a[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_a_i[pid] = MM_a_i


    ####################
    # model for \mu_i^b#
    ####################

    """
    define B_{\mu}^b to be multivariate normal centered at 0, covariance sigma_{\mu}^b * I
    define sigma_{\mu}^b to be uniform(0, K_sigma_{\mu}^b)
    define K_sigma_{\mu}^{\mu,b} to be some constant
    """

    @pymc.stochastic(observed = True)
    def MM_sigma_mu_b(value = MM_sigma_mu_b_initial, max = K_sigma_mu_b):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = True)
    def MM_B_mu_b(value = B_b * np.eye(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i^b for a single i.  later, will generalize
    define \mu_pop^{b'} to be such that g_{\mu}^b(\mu_pop^{b'}} = \mu_pop^b
    define \mu_i^b = g_{\mu}^b(\mu_pop^{b') + (X_i - X_pop) * B_{\mu}^b + \epsilon_i^{\mu, b})
    define \epsilon_i^{\mu, b} to be normal(0, \sigma_{\epsilon}^{\mu, b})
    define \sigma_{\epsilon}^{\mu, b} to be uniform(0, K_{\epsilon}^{\mu,b})
    define K_{\epsilon}^{\mu,b} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_epsilon_mu_b(value = .08, max = K_epsilon_mu_b):
        return pymc.distributions.uniform_like(value, 0, max)


    VM_epsilon_i_mu_b = {}
    VM_mu_i_b = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_b', pid))
        def MM_mu_i_b(anchor = mu_pop_b_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_b):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_b(anchor + inside)
            return ans


        VM_mu_i_b[pid] = MM_mu_i_b




    #####################
    # model for \rho_i^b#
    #####################


    """
    here, define model for \rho_i^b.  it will NOT depend on covariates
    \rho_i^b will be some diffuse distribution in (0,1).  let's say uniform for now
    """

    VM_rho_i_b = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_b', pid), observed = False)
        def MM_rho_i_b(value = MM_rho_i_b_initial):
            return helper.truncated_exponential_likelihood(value, l_b)
            return pymc.distributions.exponential_like(value, l_b)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_b[pid] = MM_rho_i_b
    

    #################
    # model for b_i #
    #################

    """
    define b_i to be beta(\mu_i^b, \mu_i^b * \rho_i^b )
    """

    VM_b_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('b', pid), observed = False)
        def MM_b_i(value = 0.4, mu = VM_mu_i_b[pid], rho = VM_rho_i_b[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_b_i[pid] = MM_b_i


    #################
    # model for c_i #
    #################


    """
    define B_{\mu}^c to be multivariate normal centered at 0, covariance sigma_{\mu}^c * I
    define sigma_{\mu}^c to be uniform(0, K_sigma_{\mu}^c)
    define K_sigma_{\mu}^{\mu,c} to be some constant
    """



    @pymc.stochastic(observed = True)
    def MM_sigma_mu_c(value = MM_sigma_mu_c_initial, max = K_sigma_mu_c):
        return pymc.distributions.uniform_like(value, 0, max)

    @pymc.stochastic(observed = True)
    def MM_B_mu_c(value = B_c * np.eye(num_attributes), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_c):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    """
    here, define model for mu_i_c for a single i.  later, will generalize
    define \mu_pop^{c'} to be such that g_{\mu}^c(\mu_pop^{c'}} = \mu_pop^c
    for now, define \mu_i^c = g_{\mu}^a(\mu_pop^{a') + (X_i - X_pop) * B_{\mu}^a). note the lack of noise.
    for now, define c_i = \mu_i_c
    """

    VM_mu_i_c = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = get_model_helper.var_name_pid_to_vid('mu_c', pid))
        def MM_mu_i_c(anchor = mu_pop_c_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_c):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_c(anchor + inside)
            return ans

        VM_mu_i_c[pid] = MM_mu_i_c


    VM_rho_i_c = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('rho_c', pid), observed = True)
        def MM_rho_i_c(value = MM_rho_i_c_initial):
            #assert value > 0
            return pymc.distributions.exponential_like(value, l_c)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_c[pid] = MM_rho_i_c



    VM_c_i = {}

    for pid in pid_iterator:
        @pymc.stochastic(name = get_model_helper.var_name_pid_to_vid('c', pid), observed = False)
        def MM_c_i(value = 0.4, mu = VM_mu_i_c[pid], rho = VM_rho_i_c[pid]):
            
            k, theta = helper.gamma_mu_phi_to_k_theta(mu, rho)
            rate = 1.0 / theta
            return pymc.distributions.gamma_like(value, k, rate)
            return mu

        VM_c_i[pid] = MM_c_i


    ####################
    # create the model #
    ####################    

    prior_variables = [MM_sigma_mu_a, MM_B_mu_a, MM_sigma_epsilon_mu_a, VM_epsilon_i_mu_a, VM_mu_i_a, \
                       VM_rho_i_a, \
                       VM_a_i, \
                       MM_sigma_mu_b, MM_B_mu_b, MM_sigma_epsilon_mu_b, VM_epsilon_i_mu_b, VM_mu_i_b, \
                       VM_rho_i_b, \
                       VM_b_i, \
                       MM_sigma_mu_c, MM_B_mu_c, VM_mu_i_c, \
                       VM_c_i]



    M = pymc.MCMC(prior_variables)

    return M, pid




def get_model_using_variable_manager(M):

    ########################
    # define some variables#
    ########################

    pid_iterator = M.get_pid_iterable()
    num_attributes = M.get_x_len()

    #####################################
    # define functions used in the model#
    #####################################

    """
    define squashing function for \mu_i^a and its inverse
    squashing function is logistic function, and it is scaled to have range(0, r_mu_a)
    """
    r_mu_a = 1.0

    def g_mu_a(x):
        return r_mu_a / (1.0 + math.exp(-1.0 * x))

    def g_mu_a_inv(y):
        c = 1.0 / r_mu_a
        return math.log((c*y)/(1-c*y))

    g_mu_b = g_mu_a
    g_mu_b_inv = g_mu_a_inv

    def g_mu_c(x):
        return math.exp(x)

    def g_mu_c_inv(y):
        return math.log(y)

    """
    define function f that takes in curve parameters, time, and returns the ture value at that time
    at time 0, level is a + (1-b)(1-a).  asymptotic drop is a
    """

    def f(t, s, a, b, c):
        return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*c*t))


    ###################################################
    # Extract some constants from the variable manager#
    ###################################################

    mu_pop_a = M.constants.mu_pop_a
    mu_pop_b = M.constants.mu_pop_b
    mu_pop_c = M.constants.mu_pop_c

    mu_pop_a_prime = g_mu_a_inv(mu_pop_a)
    mu_pop_b_prime = g_mu_b_inv(mu_pop_b)
    mu_pop_c_prime = g_mu_c_inv(mu_pop_c)


    sigma_mu_a = M.constants.sigma_mu_a
    sigma_mu_b = M.constants.sigma_mu_b
    sigma_mu_c = M.constants.sigma_mu_c

    ################################
    # define variables of the model#
    ################################

    ####################
    # model for \mu_i^a#
    ####################

    @pymc.stochastic(name = M.get_variable_name('B_a'), observed = M.get_variable_name('B_a'))
    def MM_B_mu_a(value = M.get_variable_value('B_a'), mu = np.zeros(num_attributes), sigma = sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_i_a = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = M.get_pid_variable_name('mu_a', pid)
        def MM_mu_i_a(anchor = mu_pop_a_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_a):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_a(anchor + inside)
            return ans


        VM_mu_i_a[pid] = MM_mu_i_a




    #####################
    # model for \rho_i^a#
    #####################


    VM_rho_i_a = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = M.get_pid_variable_name('rho_a', pid), observed = M.get_pid_variable_observed('rho_a', pid))
        def MM_rho_i_a(value = M.get_pid_variable_value('rho_a', pid)):
            return helper.truncated_exponential_likelihood(value, M.l_a)
    
        VM_rho_i_a[pid] = MM_rho_i_a
    

    #################
    # model for a_i #
    #################


    VM_a_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = M.get_pid_variable_name('a', pid), observed = M.get_pid_variable_observed('a', pid))
        def MM_a_i(value = M.get_pid_variable_value('a', pid), mu = VM_mu_i_a[pid], rho = VM_rho_i_a[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_a_i[pid] = MM_a_i


    ####################
    # model for \mu_i^b#
    ####################



    @pymc.stochastic(name = M.get_variable_name('B_b'), observed = M.get_variable_observed('B_b'))
    def MM_B_mu_b(value = M.get_pid_variable_value('B_b'), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_a):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_i_b = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = M.get_pid_variable_observed('mu_b', pid))
        def MM_mu_i_b(anchor = mu_pop_b_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_b):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_b(anchor + inside)
            return ans


        VM_mu_i_b[pid] = MM_mu_i_b




    #####################
    # model for \rho_i^b#
    #####################


    VM_rho_i_b = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = M.get_pid_variable_name('rho_b', pid), observed = M.get_pid_variable_observed('rho_b', pid))
        def MM_rho_i_b(value = M.get_pid_variable_value('rho_b', pid)):
            return helper.truncated_exponential_likelihood(value, M.l_b)
    
        VM_rho_i_b[pid] = MM_rho_i_b
    

    #################
    # model for b_i #
    #################

    VM_b_i = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = M.get_pid_variable_name('b', pid), observed = M.get_pid_variable_observed('b', pid))
        def MM_b_i(value = M.get_pid_variable_value('b', pid), mu = VM_mu_i_b[pid], rho = VM_rho_i_b[pid]):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_b_i[pid] = MM_b_i


    #################
    # model for c_i #
    #################


 

    @pymc.stochastic(observed = M.get_variable_observed('B_c'))
    def MM_B_mu_c(value = M.get_variable_value('B_c'), mu = np.zeros(num_attributes), sigma = MM_sigma_mu_c):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_i_c = {}

    for pid in pid_iterator:

        @pymc.deterministic(name = M.get_pid_variable_name('mu_c', pid))
        def MM_mu_i_c(anchor = mu_pop_c_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_c):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_c(anchor + inside)
            return ans

        VM_mu_i_c[pid] = MM_mu_i_c


    VM_rho_i_c = {}

    for pid in pid_iterator:

        @pymc.stochastic(name = M.get_pid_variable_name('rho_c', pid), observed = M.get_pid_variable_observed('rho_c', pid))
        def MM_rho_i_c(value = M.get_variable_value('rho_c', pid)):
            #assert value > 0
            return pymc.distributions.exponential_like(value, M.l_c)
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(0.1, 0.1)
            return pymc.distributions.beta_like(value, alpha, beta)
    
        VM_rho_i_c[pid] = MM_rho_i_c



    VM_c_i = {}

    for pid in pid_iterator:
        @pymc.stochastic(name = M.get_pid_variable_name('c', pid), observed = M.get_pid_variable_observed('rho_c', pid))
        def MM_c_i(value = M.get_pid_variable_value('c', pid), mu = VM_mu_i_c[pid], rho = VM_rho_i_c[pid]):
            
            k, theta = helper.gamma_mu_phi_to_k_theta(mu, rho)
            rate = 1.0 / theta
            return pymc.distributions.gamma_like(value, k, rate)
            return mu

        VM_c_i[pid] = MM_c_i


    ####################
    # create the model #
    ####################    

    prior_variables = [MM_sigma_mu_a, MM_B_mu_a, MM_sigma_epsilon_mu_a, VM_epsilon_i_mu_a, VM_mu_i_a, \
                       VM_rho_i_a, \
                       VM_a_i, \
                       MM_sigma_mu_b, MM_B_mu_b, MM_sigma_epsilon_mu_b, VM_epsilon_i_mu_b, VM_mu_i_b, \
                       VM_rho_i_b, \
                       VM_b_i, \
                       MM_sigma_mu_c, MM_B_mu_c, VM_mu_i_c, \
                       VM_c_i]



    M = pymc.MCMC(prior_variables)

    return M
