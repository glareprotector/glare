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


"""
class data_point(object):

    def __init__(self, time, value):
        self.time, self.value = time, value

    def __repr__(self):
        return str(self.time) + ',' + str(self.value)
"""

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

        self.data_point_val_cache = {}        
        self.data_observed_cache = {}

        self.constants = attribute_holder


    def get_pid_variable_key(self, seed, pid):
        return (seed, pid)



    """
    getting names
    """

    def get_variable_name(self, seed):
        return seed

    def get_pid_variable_name(self, seed, pid):
        return seed + '_' + pid

    def get_data_name(self, pid, idx):
        return 'f' + '_' + pid + '_' + str(idx)




    """
    setting/getting values
    """

    def set_variable_value(self, seed, val):
        self.val_cache[self.get_variable_name(seed)] = val

    def get_variable_value(self, seed):
        return self.val_cache[self.get_variable_name(seed)]

    def remove_variable(self, seed):
        del self.val_cache[self.get_variable_name(seed)]



    def set_pid_variable_value(self, seed, pid, val):
        self.val_cache[self.get_pid_variable_key(seed, pid)] = val

    def set_pid_variable_value_blanket(self, seed, val):
        self.val_cache_blanket[self.get_variable_name(seed)] = val

    def get_pid_variable_value(self, seed, pid):
        try:
            return self.val_cache[self.get_pid_variable_key(seed, pid)]
        except Exception, err:
            return self.val_cache_blanket[self.get_variable_name(seed)]
            
    def remove_pid_variable(self, seed, pid):
        del self.val_cache[self.get_pid_variable_key(seed, pid)]


    def set_pid_data_points(self, pid, data_points):
        """
        for a single patient, the time points will be stored as a list of time_points, which store the time and value
        """
        self.data_point_val_cache[pid] = data_points

    def get_pid_data_points(self, pid):
        try:
            return self.data_point_val_cache[pid]
        except:
            #return []
            import pandas
            return pandas.Series()





    """
    setting/getting whether observed
    """


    def get_variable_observed(self, seed):
        return self.observed_cache[self.get_variable_name(seed)]

    def set_variable_observed(self, seed, observed):
        self.observed_cache[self.get_variable_name(seed)] = observed



    def set_pid_variable_observed(self, seed, pid, val):
        self.observed_cache[self.get_pid_variable_key(seed, pid)] = val

    def set_pid_variable_observed_blanket(self, seed, val):
        self.observed_cache_blanket[seed] = val

    def get_pid_variable_observed(self, seed, pid):
        try:
            return self.observed_cache_blanket[self.get_variable_name(seed)]
        except:
            return self.observed_cache[self.get_pid_variable_key(seed, pid)]
    
    def get_pid_data_observed(self, pid):
        try:
            return self.data_observed_blanket
        except:
            return self.data_observed_cache[pid]

    def set_pid_data_observed(self, pid, val):
        self.data_observed_cache[pid] = val

    def set_pid_data_observed_blanket(self, val):
        self.data_observed_blanket = val




    """
    other functions
    """

    def set_num_attributes(self, num):
        self.num_attributes = num

    def get_x_len(self):
        return self.num_attributes


    def get_pid_iterable(self):
        """
        define the pids of model to be those for which there is a x variable
        """
        ans = []
        for key in self.val_cache:
            if isinstance(key, tuple):
                seed = key[0]
                pid = key[1]
                if seed == 'x':
                    ans.append(pid)
        return ans
                


def add_curve(ax, s, a, b, c, max_time, time_points):
    num_points = 500
    all_points = [x*float(max_time)/num_points for x in range(num_points)]
    all_f_vals = [f(t,s,a,b,c)  for t in all_points]
    ax.plot(all_points, all_f_vals)
    time_point_f_vals = [f(t,s,a,b,c)  for t in time_points]
    ax.scatter(time_points, time_point_f_vals)

def get_deterministic_abc_given_x_and_Bs(the_cov, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c):
    x = the_cov.x
    a = g_mu_a(g_mu_a_inv(mu_pop_a) + x.dot(B_a))
    b = g_mu_b(g_mu_b_inv(mu_pop_b) + x.dot(B_b))
    c = g_mu_c(g_mu_c_inv(mu_pop_c) + x.dot(B_c))
    return a, b, c

def get_data_points_given_abc(s, a, b, c, time_points, rho_noise):
    """
    have this return a panda series
    """
    if rho_noise != 0:
        f_vals = [f(t,s,a,b,c) + np.random.normal(0, rho_noise) for t in time_points]
    else:
        f_vals = [f(t,s,a,b,c)  for t in time_points]
    ans = pandas.Series(f_vals, index = time_points)
    return ans

"""
ideally there should be a one sample model that would be passed to this.  instead, assume that M is on??????
"""


def get_abc_given_xs_sample(the_cov, rho_a, rho_b, rho_c, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c):
    x = the_cov.x
    import random
    mu_a = g_mu_a(g_mu_a_inv(mu_pop_a) + x.dot(B_a))
    mu_b = g_mu_b(g_mu_b_inv(mu_pop_b) + x.dot(B_b))
    mu_c = g_mu_c(g_mu_c_inv(mu_pop_c) + x.dot(B_c))

    k_c, theta_c = helper.gamma_mu_phi_to_k_theta(mu_c, rho_c)
    alpha_c, beta_c = k_c, 1.0/theta_c
    return helper.get_beta(mu_a,rho_a,'mode'), helper.get_beta(mu_b,rho_b,'mode'), random.gammavariate(alpha_c,beta_c)


def get_simulated_datas_and_abc(xs, pids, mode, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c, time_points, simulate_noise_sd, simulate_rho_a, simulate_rho_b, simulate_rho_c):

    """
    each element of xs should be an array.  
    returns dictionary from pid to data and dictionary from pid to abc's
    """

    simulated_data = {}
    simulated_abcs = {}

    for x,pid in zip(xs, pids):

        the_cov = helper.cov(x, 1.0)

        if mode == 'deterministic':
            a,b,c = get_deterministic_abc_given_x_and_Bs(the_cov, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
        elif mode == 'random':
            a,b,c = get_abc_given_xs_sample(the_cov, simulate_rho_a, simulate_rho_b, simulate_rho_c, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
        else:
            assert False

        data_points = get_data_points_given_abc(1.0, a, b, c, time_points, simulate_noise_sd)
        the_complete_data = helper.complete_data(the_cov, data_points)


        simulated_data[pid] = the_complete_data
        simulated_abcs[pid] = helper.abc_data(the_cov, a, b, c)

    return simulated_abcs, simulated_data


def f(t, s, a, b, c):
    #return a
    """
    initial level = a.  final level = (1.0 - a) * b + a
    """

    #return a + b * t

    #return s * (a + ((1.0 - a) * b) * (1.0 - math.exp(-1.0*t)))
    #return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*t))
    #return s * ( (1.0-a) - (1.0-a)*(b) * (1.0 - math.exp(-1.0*t)))
    return s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*c*t))


def real_f(t, s, a, b, c):

    #return a + b * t

    try:
        ans = s * ( (1.0-a) - (1.0-a)*(b) * math.exp(-1.0*c*t))
    except:
        print t, s, a, b, c
        pdb.set_trace()
    else:
        return ans

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



def get_model_using_variable_manager(M, which_model = 'MCMC', db_file = 'trace.db'):

    ########################
    # define some variables#
    ########################

    num_attributes = M.get_x_len()
    to_trace = True
    all_verbose = False
    trace_rho = False



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

    ############################################################
    # have the covariates/s be deterministic parts of the model#
    ############################################################

    VM_x_i = {}
    for pid in M.get_pid_iterable():

        @pymc.deterministic(name = M.get_pid_variable_name('x',pid))
        def MM_x_i(value = M.get_pid_variable_value('x', pid)):
            return value

        VM_x_i[pid] = MM_x_i


    VM_s_i = {}
    for pid in M.get_pid_iterable():

        @pymc.deterministic(name = M.get_pid_variable_name('s',pid))
        def MM_s_i(value = M.get_pid_variable_value('s', pid)):
            return value

        VM_s_i[pid] = MM_s_i


    ####################
    # model for \mu_i^a#
    ####################



    @pymc.stochastic(name = M.get_variable_name('sigma_a'), observed = M.get_variable_observed('sigma_a'), trace = to_trace, verbose = all_verbose)
    def MM_sigma_a(value = M.get_variable_value('sigma_a')):
        return pymc.distributions.uniform_like(value, 0, M.constants.sigma_a_max)


    @pymc.stochastic(name = M.get_variable_name('B_a'), observed = M.get_variable_observed('B_a'), trace = to_trace, verbose = all_verbose)
    def MM_B_mu_a(value = M.get_variable_value('B_a'), mu = np.zeros(num_attributes), sigma = MM_sigma_a):
        return 1.0
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))



    VM_mu_a_i = {}

    for pid in M.get_pid_iterable():
        
          @pymc.deterministic(name = M.get_pid_variable_name('mu_a', pid))
          def MM_mu_a_i(anchor = mu_pop_a_prime, X_pop = M.constants.X_pop, X_i = VM_x_i[pid], B = MM_B_mu_a):

              inside = (X_i - X_pop).dot(B)
              ans = g_mu_a(anchor + inside)
              return ans


          VM_mu_a_i[pid] = MM_mu_a_i




    ###################
    # model for \rho_a#
    ###################


    @pymc.stochastic(name = M.get_variable_name('rho_a'), observed = M.get_variable_observed('rho_a'), trace = trace_rho, verbose = all_verbose)
    def MM_rho_a(value = M.get_variable_value('rho_a')):
        return helper.truncated_exponential_likelihood(value, M.constants.l_a)





    #################
    # model for a_i #
    #################

    
    VM_a_i = {}

    for pid in M.get_pid_iterable():

        @pymc.stochastic(name = M.get_pid_variable_name('a', pid), observed = M.get_pid_variable_observed('a', pid), trace = to_trace, verbose = all_verbose)
        def MM_a_i(value = M.get_pid_variable_value('a', pid), mu = VM_mu_a_i[pid], rho = MM_rho_a):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_a_i[pid] = MM_a_i
    

    ####################
    # model for \mu_i^b#
    ####################

    @pymc.stochastic(name = M.get_variable_name('sigma_b'), observed = M.get_variable_observed('sigma_b'), trace = to_trace, verbose = all_verbose)
    def MM_sigma_b(value = M.get_variable_value('sigma_b')):
        return pymc.distributions.uniform_like(value, 0, M.constants.sigma_b_max)

    @pymc.stochastic(name = M.get_variable_name('B_b'), observed = M.get_variable_observed('B_b'), trace = to_trace, verbose = all_verbose)
    def MM_B_mu_b(value = M.get_variable_value('B_b'), mu = np.zeros(num_attributes), sigma = MM_sigma_b):
        return 1.0
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_b_i = {}

    for pid in M.get_pid_iterable():

        @pymc.deterministic(name = M.get_pid_variable_name('mu_b', pid))
        def MM_mu_b_i(anchor = mu_pop_b_prime, X_pop = M.constants.X_pop, X_i = VM_x_i[pid], B = MM_B_mu_b):
            inside = (X_i - X_pop).dot(B)
            return g_mu_b(anchor + inside)



        VM_mu_b_i[pid] = MM_mu_b_i




    ###################
    # model for \rho_b#
    ###################



    @pymc.stochastic(name = M.get_variable_name('rho_b'), observed = M.get_variable_observed('rho_b'), trace = trace_rho, verbose = all_verbose)
    def MM_rho_b(value = M.get_variable_value('rho_b')):
        return helper.truncated_exponential_likelihood(value, M.constants.l_b)



    #################
    # model for b_i #
    #################

    VM_b_i = {}

    for pid in M.get_pid_iterable():

        @pymc.stochastic(name = M.get_pid_variable_name('b', pid), observed = M.get_pid_variable_observed('b', pid), trace = to_trace, verbose = all_verbose)
        def MM_b_i(value = M.get_pid_variable_value('b', pid), mu = VM_mu_b_i[pid], rho = MM_rho_b):
            alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
            assert alpha >= 0.0
            assert beta >= 0.0
            return pymc.distributions.beta_like(value, alpha, beta)

        VM_b_i[pid] = MM_b_i


    #################
    # model for c_i #
    #################


    @pymc.stochastic(name = M.get_variable_name('sigma_c'), observed = M.get_variable_observed('sigma_c'), trace = to_trace, verbose = all_verbose)
    def MM_sigma_c(value = M.get_variable_value('sigma_c')):
        return pymc.distributions.uniform_like(value, 0, M.constants.sigma_c_max)

    @pymc.stochastic(name = M.get_variable_name('B_c'), observed = M.get_variable_observed('B_c'))
    def MM_B_mu_c(value = M.get_variable_value('B_c'), mu = np.zeros(num_attributes), sigma = MM_sigma_c, trace = to_trace):
        return pymc.distributions.mv_normal_cov_like(value, mu, pow(sigma, 2) * np.eye(num_attributes))

    VM_mu_c_i = {}

    for pid in M.get_pid_iterable():

        @pymc.deterministic(name = M.get_pid_variable_name('mu_c', pid))
        def MM_mu_c_i(anchor = mu_pop_c_prime, X_pop = M.constants.X_pop, X_i = VM_x_i[pid], B = MM_B_mu_c):
            inside = (X_i - X_pop).dot(B)
            ans = g_mu_c(anchor + inside)
            return ans

        VM_mu_c_i[pid] = MM_mu_c_i



    @pymc.stochastic(name = M.get_variable_name('rho_c'), observed = M.get_variable_observed('rho_c'), trace = trace_rho, verbose = all_verbose)
    def MM_rho_c(value = M.get_variable_value('rho_c')):
        return helper.truncated_exponential_likelihood(value, M.constants.l_c)

    VM_c_i = {}

    for pid in M.get_pid_iterable():
        @pymc.stochastic(name = M.get_pid_variable_name('c', pid), observed = M.get_pid_variable_observed('c', pid), trace = to_trace, verbose = all_verbose)
        def MM_c_i(value = M.get_pid_variable_value('c', pid), mu = VM_mu_c_i[pid], rho = MM_rho_c):
            
            k, theta = helper.gamma_mu_phi_to_k_theta(mu, rho)
            rate = 1.0 / theta
            return pymc.distributions.gamma_like(value, k, rate)

        VM_c_i[pid] = MM_c_i

    #####################
    # add in data points#
    #####################

    
    
    @pymc.stochastic(name = M.get_variable_name('rho_noise'), observed = M.get_variable_observed('rho_noise'), trace = to_trace, verbose = all_verbose)
    def rho_noise(value = M.get_variable_value('rho_noise'), l = M.constants.lambda_noise):
        return pymc.distributions.exponential_like(value, l)

    """
    the data structure will be a dictionary of lists
    data_points is a pandas series
    """
    VM_f_i = {}
    for pid in M.get_pid_iterable():
        VM_f_i[pid] = []
        this_data_points = M.get_pid_data_points(pid)

        for data_point, idx in zip(this_data_points.iteritems(), range(len(this_data_points))):
            @pymc.stochastic(name = M.get_data_name(pid, idx), observed = M.get_pid_data_observed(pid), verbose = all_verbose)
            def f_i_idx(value = data_point[1], time = data_point[0], s = VM_s_i[pid], a = VM_mu_a_i[pid], b = VM_mu_b_i[pid], c = VM_mu_c_i[pid], eps = rho_noise):
                mean = f(time, s, a, b, c)
                return pymc.distributions.normal_like(value, mean, 1.0 / pow(eps,2))

            VM_f_i[pid].append(f_i_idx)


    ####################
    # create the model #
    ####################    
            
    
    prior_variables = [VM_x_i, VM_s_i, \
                           MM_sigma_a, MM_B_mu_a, VM_mu_a_i, \
                           MM_rho_a, \
                           VM_a_i, \
                           MM_sigma_b, MM_B_mu_b, VM_mu_b_i, \
                           MM_rho_b, \
                           VM_b_i, \
                           MM_sigma_c, MM_B_mu_c, VM_mu_c_i, \
                           MM_rho_c, \
                           VM_c_i]
    
    """
    prior_variables = [VM_x_i, \
                           MM_sigma_a, MM_B_mu_a, VM_mu_a_i, \
                           MM_sigma_b, MM_B_mu_b, VM_mu_b_i, \
                           MM_sigma_c, MM_B_mu_c, VM_mu_c_i, \
                           MM_rho_a, VM_a_i \
                           ]
    """


    data_variables = [rho_noise, VM_f_i]

    if which_model == 'MCMC':
        model = pymc.MCMC(prior_variables + data_variables, verbose=True, db = 'pickle', dbname=db_file)
    elif which_model == 'MAP':
        model = pymc.MAP(prior_variables + data_variables, verbose=True)


    #model = pymc.MCMC(prior_variables)

    print 'END'

    return model
