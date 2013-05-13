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



class data_point(object):

    def __init__(self, time, value):
        self.time, self.value = time, value

    def __repr__(self):
        return str(self.time) + ',' + str(self.value)

class attribute_holder(object):
    pass

class variable_manager(object):
    """
    provides way to set and get *values* and *names* of variables in model.  this can be done before the model is created
    also store values of constants/non
    """

    def __init__(self):
        self.val_cache = {}
        self.val_cache_blanket = {}
        self.observed_cache = {}
        self.observed_cache_blanket = {}
        self.data_observed_cache = {}
        self.x_cache = {}
        self.data_point_cache = {}
        self.constants = attribute_holder

    def get_variable_name(self, seed):
        return seed

    def get_pid_variable_name(self, seed, pid):
        return seed + '_' + pid

    def get_data_name(self, pid, idx):
        return 'f' + '_' + pid + '_' + str(idx)


    def set_variable_value(self, seed, val):
        self.val_cache[self.get_variable_name(seed)] = val

    def get_variable_value(self, seed):
        return self.val_cache[self.get_variable_name(seed)]

    def remove_variable(self, seed):
        del self.val_cache[self.get_variable_name(seed)]



    def set_pid_variable_value(self, seed, pid, val):
        self.val_cache[self.get_pid_variable_name(seed, pid)] = val

    def set_pid_variable_value_blanket(self, seed, val):
        self.val_cache_blanket[self.get_variable_name(seed)] = val

    def get_pid_variable_value(self, seed, pid):
        try:
            return self.val_cache_blanket[self.get_variable_name(seed)]
        except Exception, err:
            print err, seed, pid
            return self.val_cache[self.get_pid_variable_name(seed, pid)]

    def remove_pid_variable(self, seed, pid):
        del self.val_cache[self.get_pid_variable_name(seed, pid)]

    def set_pid_data_points(self, pid, data_points):
        """
        for a single patient, the time points will be stored as a list of time_points, which store the time and value
        """
        self.data_point_cache[pid] = data_points

    def get_pid_data_points(self, pid):
        try:
            return self.data_point_cache[pid]
        except:
            return []






    def get_variable_observed(self, seed):
        return self.observed_cache[self.get_variable_name(seed)]

    def set_variable_observed(self, seed, observed):
        self.observed_cache[self.get_variable_name(seed)] = observed



    def set_pid_variable_observed(self, seed, pid, val):
        self.observed_cache[self.get_pid_variable_name(seed, pid)] = val

    def set_pid_variable_observed_blanket(self, seed, val):
        self.observed_cache_blanket[seed] = val

    def get_pid_variable_observed(self, seed, pid):
        try:
            return self.observed_cache_blanket[self.get_variable_name(seed)]
        except:
            return self.observed_cache[self.get_pid_variable_name(seed, pid)]
    
    def get_pid_data_observed(self, pid):
        try:
            return self.observed_cache_blanket[variable_manager.data_key]
        except:
            return self.data_observed_cache[pid]

    def set_pid_data_observed(self, pid, val):
        self.data_observed_cache[pid] = val

    def set_pid_data_observed_blanket(self, val):
        self.observed_cache_blanket[variable_manager.data_key] = val

    data_key = 42


    def set_pid_x(self, pid, x):
        self.x_cache[pid] = x

    def clear_pid_x(self):
        self.x_cache.clear()

    def get_pid_x(self, pid):
        return self.x_cache[pid]

    def set_pid_x_from_dataframe(self, X):
        for pid in X.index:
            self.set_pid_x(pid, X.loc[pid])

    def get_x_len(self):
        ans =len(iter(self.x_cache.items()).next()[1])
        return ans



    def get_pid_iterable(self):
        return self.x_cache.keys()








def get_abc_given_xs(M, x, s, num_steps):
    """
    with a given model parameter object and an x for that model, returns a sample of abc from that model
    M shouldn't have any x attributes
    should not change M
    """

    assert len(M.get_pid_iterable()) == 0
    temp_pid = '0'
    M.set_pid_x(temp_pid, x)
    M.set_pid_variable_value('s', temp_pid, s)
    M.constants.X_pop = pandas.Series([0])
    model = get_model_using_variable_manager(M)
    model.sample(num_steps)

    a = model.trace(M.get_pid_variable_name('mu_a', temp_pid))[-1]
    b = model.trace(M.get_pid_variable_name('mu_b', temp_pid))[-1]
    c = model.trace(M.get_pid_variable_name('mu_c', temp_pid))[-1]

    M.remove_pid_variable('s', temp_pid)
    M.clear_pid_x()
    return a, b, c



def get_abc_and_data_points_given_xs(M, x, s, rho_noise, num_steps, num_points, max_time):
    """
    given covariate, simulates data.  returns it as a list of data_points
    simulate data, but know s.  so should set s when simulating, and use s when inferring
    for simplicity, s is always set to 1, but this fxn doesn't know about that
    should leave M unchanged
    """
    a, b, c = get_abc_given_xs(M, x, s, num_steps)
    time_points = [random.random()*max_time for i in range(num_points)]
    f_vals = [f(t,s,a,b,c) + np.random.normal(0, rho_noise) for t in time_points]
    f_vals = [f(t,s,a,b,c)  for t in time_points]
    data_points = [data_point(t,v) for t,v in zip(time_points, f_vals)]
    print data_points
    return a,b,c, data_points





def f(t, s, a, b, c):
    return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*t/c))


def get_model_using_variable_manager(M):

    ########################
    # define some variables#
    ########################

    num_attributes = M.get_x_len()
    to_trace = True

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


    ################################
    # define variables of the model#
    ################################

    ####################
    # model for \mu_i^a#
    ####################



    @pymc.stochastic(name = M.get_variable_name('sigma_a'), observed = M.get_variable_observed('sigma_a'), trace = to_trace)
    def MM_sigma_a(value = M.get_variable_value('sigma_a')):
        return pymc.distributions.uniform_like(value, 0, M.constants.sigma_a_max)


    @pymc.stochastic(name = M.get_variable_name('B_a'), observed = M.get_variable_observed('B_a'), trace = to_trace)
    def MM_B_mu_a(value = M.get_variable_value('B_a'), mu = np.zeros(num_attributes), sigma = MM_sigma_a):

        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))



    VM_mu_i_a = {}

    for pid in M.get_pid_iterable():
        
          @pymc.deterministic(name = M.get_pid_variable_name('mu_a', pid))
          def MM_mu_i_a(anchor = mu_pop_a_prime, X_pop = M.constants.X_pop, X_i = M.get_pid_x(pid), B = MM_B_mu_a):
              inside = (X_i - X_pop).dot(B)
              ans = g_mu_a(anchor + inside)
              return ans


          VM_mu_i_a[pid] = MM_mu_i_a




    ###################
    # model for \rho_a#
    ###################


    @pymc.stochastic(name = M.get_variable_name('rho_a'), observed = M.get_variable_observed('rho_a'), trace = to_trace)
    def MM_rho_a(value = M.get_variable_value('rho_a')):
        return helper.truncated_exponential_likelihood(value, M.constants.l_a)





    #################
    # model for a_i #
    #################


    VM_a_i = {}

    for pid in M.get_pid_iterable():

        @pymc.stochastic(name = M.get_pid_variable_name('a', pid), observed = M.get_pid_variable_observed('a', pid), trace = to_trace)
        def MM_a_i(value = M.get_pid_variable_value('a', pid), mu = VM_mu_i_a[pid], rho = MM_rho_a):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_a_i[pid] = MM_a_i


    ####################
    # model for \mu_i^b#
    ####################

    @pymc.stochastic(name = M.get_variable_name('sigma_b'), observed = M.get_variable_observed('sigma_b'), trace = to_trace)
    def MM_sigma_b(value = M.get_variable_value('sigma_b')):
        return pymc.distributions.uniform_like(value, 0, M.constants.sigma_b_max)

    @pymc.stochastic(name = M.get_variable_name('B_b'), observed = M.get_variable_observed('B_b'), trace = to_trace)
    def MM_B_mu_b(value = M.get_variable_value('B_b'), mu = np.zeros(num_attributes), sigma = MM_sigma_b):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_i_b = {}

    for pid in M.get_pid_iterable():

        @pymc.deterministic(name = M.get_pid_variable_name('mu_b', pid))
        def MM_mu_i_b(anchor = mu_pop_b_prime, X_pop = M.constants.X_pop, X_i = M.get_pid_x(pid), B = MM_B_mu_b):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_b(anchor + inside)
            return ans


        VM_mu_i_b[pid] = MM_mu_i_b




    ###################
    # model for \rho_b#
    ###################



    @pymc.stochastic(name = M.get_variable_name('rho_b'), observed = M.get_variable_observed('rho_b'), trace = to_trace)
    def MM_rho_b(value = M.get_variable_value('rho_b')):
        return helper.truncated_exponential_likelihood(value, M.constants.l_b)



    #################
    # model for b_i #
    #################

    VM_b_i = {}

    for pid in M.get_pid_iterable():

        @pymc.stochastic(name = M.get_pid_variable_name('b', pid), observed = M.get_pid_variable_observed('b', pid), trace = to_trace)
        def MM_b_i(value = M.get_pid_variable_value('b', pid), mu = VM_mu_i_b[pid], rho = MM_rho_b):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_b_i[pid] = MM_b_i


    #################
    # model for c_i #
    #################


    @pymc.stochastic(name = M.get_variable_name('sigma_c'), observed = M.get_variable_observed('sigma_c'), trace = to_trace)
    def MM_sigma_c(value = M.get_variable_value('sigma_c')):
        return pymc.distributions.uniform_like(value, 0, M.constants.sigma_c_max)

    @pymc.stochastic(name = M.get_variable_name('B_c'), observed = M.get_variable_observed('B_c'))
    def MM_B_mu_c(value = M.get_variable_value('B_c'), mu = np.zeros(num_attributes), sigma = MM_sigma_c, trace = to_trace):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_i_c = {}

    for pid in M.get_pid_iterable():

        @pymc.deterministic(name = M.get_pid_variable_name('mu_c', pid))
        def MM_mu_i_c(anchor = mu_pop_c_prime, X_pop = M.constants.X_pop, X_i = M.get_pid_x(pid), B = MM_B_mu_c):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_c(anchor + inside)
            return ans

        VM_mu_i_c[pid] = MM_mu_i_c



    @pymc.stochastic(name = M.get_variable_name('rho_c'), observed = M.get_variable_observed('rho_c'), trace = to_trace)
    def MM_rho_c(value = M.get_variable_value('rho_c')):
        return helper.truncated_exponential_likelihood(value, M.constants.l_c)

    VM_c_i = {}

    for pid in M.get_pid_iterable():
        @pymc.stochastic(name = M.get_pid_variable_name('c', pid), observed = M.get_pid_variable_observed('c', pid), trace = to_trace)
        def MM_c_i(value = M.get_pid_variable_value('c', pid), mu = VM_mu_i_c[pid], rho = MM_rho_c):
            
            k, theta = helper.gamma_mu_phi_to_k_theta(mu, rho)
            rate = 1.0 / theta
            return pymc.distributions.gamma_like(value, k, rate)
            return mu

        VM_c_i[pid] = MM_c_i

    #####################
    # add in data points#
    #####################

    
    
    @pymc.stochastic(name = M.get_variable_name('rho_noise'), observed = M.get_variable_observed('rho_noise'))
    def rho_noise(value = M.get_variable_value('rho_noise'), l = M.constants.lambda_noise):
        return pymc.distributions.exponential_like(value, l)

    """
    the data structure will be a dictionary of lists
    name the data point by pid and the 
    """
    VM_f_i = {}
    for pid in M.get_pid_iterable():
        VM_f_i[pid] = []
        this_data_points = M.get_pid_data_points(pid)
        for data_point, idx in zip(this_data_points, range(len(this_data_points))):
            @pymc.stochastic(name = M.get_data_name(pid, idx), observed = M.get_pid_data_observed(pid))
            def f_i_idx(value = data_point.value, time = data_point.time, s = M.get_pid_variable_value('s', pid), a = VM_a_i[pid], b = VM_b_i[pid], c = VM_c_i[pid], eps = rho_noise):
                mean = f(time, s, a, b, c)
                return pymc.distributions.normal_like(value, mean, eps)

            VM_f_i[pid].append(f_i_idx)


    ####################
    # create the model #
    ####################    

    prior_variables = [MM_sigma_a, MM_B_mu_a, VM_mu_i_a, \
                           MM_rho_a, \
                           VM_a_i, \
                           MM_sigma_b, MM_B_mu_b, VM_mu_i_b, \
                           MM_rho_b, \
                           VM_b_i, \
                           MM_sigma_c, MM_B_mu_c, VM_mu_i_c, \
                           MM_rho_c, \
                           VM_c_i]


    data_variables = [rho_noise, VM_f_i]


    model = pymc.MCMC(prior_variables + data_variables)
    #model = pymc.MCMC(prior_variables)

    return model
