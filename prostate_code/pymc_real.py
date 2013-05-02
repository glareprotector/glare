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


"""
convention: to denote x_a^b, write x_a_b
variables of model prefaced with MM_
variables that represent observed values preceded with DD_ (this is underspecified)
vectors of observed variables preceded with VD_
vector variables of models prefaced with VM_
need to choose squashing function range so that input to g_{\mu}^a is generally close to 0.
for variables for which there is one for each patient, store in dictionary indexed by pid

List of things to do:
- focus on a_i for just 1 patient.  first just get prior distribution of \mu_i^a
- first make as many variables observed as possible
- define its covariate vector.  
- define avg covariate vector of population.
- need to define average population curve parameters
- define prior over parameters(coefficients) for a_i
- define population avg of function value
- implement model in 0.6.3 with coefficients fixed
- store this info in simple lists
"""


###########################################
# some variables that are used across plot#
###########################################

#attribute_fs = [brand(bf.always_raise,'age')(uf.ucla_feature(uf.ucla_feature.age))]
attribute_fs = [brand(bf.hard_coded_f,'age')(1)]
num_attributes = len(attribute_fs)
pid_iterator = bf.all_ucla_pid_iterable()
which_function = bf.ucla_raw_series_getter_panda.sexual_function


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
MM_sigma_mu_a_initial = 1
MM_rho_i_a_initial = 0.000005
MM_sigma_mu_b_initial = .01
MM_rho_i_b_initial = 0.0005
MM_sigma_mu_c_initial = 1


K_sigma_mu_a = 100
K_sigma_mu_b = 100
K_sigma_mu_c = 100
K_epsilon_mu_a = 20
K_epsilon_mu_b = 20



mu_pop_a = 0.9
mu_pop_b = 0.5
mu_pop_c = 1.0

mu_pop_a_prime = g_mu_a_inv(mu_pop_a)
mu_pop_b_prime = g_mu_b_inv(mu_pop_b)
mu_pop_c_prime = g_mu_c_inv(mu_pop_c)

#avg_curve_parameters = bf.avg_curve_parameters_f()(pid_iterator)
#mu_pop_a = avg_curve_parameters['a']

###########################
# get some observed values#
###########################


asdf = bf.no_exception_pid_iterable(pid_iterator, bf.patient_features_feature(attribute_fs))


#X = bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs))(pid_iterator)
X = bf.data_frame_feature_alternate(attribute_fs)(pid_iterator)

"""
modify pid_iterator to iterate only through the patients for which we have all of the attributes.  and only use 10 of them for now
"""
pid_iterator = bf.restricted_pid_iterable(X.index, 1)
#X = bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs))(pid_iterator)

#X_pop = bf.dataset_aggregate_f(af.get_bucket_mean_feature(), bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs)))(pid_iterator)
X_pop = bf.dataset_aggregate_f(bf.hard_coded_f(0.0), bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs)))(pid_iterator)




"""
VD_f_i_star = bf.data_getter(brand(bf.fake_raw_series_getter, 'age')(X, 1.0, g_mu_a, 0.1, 0.05, 0.05, 3, 0.5))(pid_iterator)

VD_t_i = {}
for pid in pid_iterator:
    VD_t_i[pid] = VD_f_i_star[pid].index

"""


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

    @pymc.stochastic(name = 'MM_epsilon_%s_mu_a' % pid,observed = True)
    def MM_epsilon_i_mu_a(value = 0, sigma = MM_sigma_epsilon_mu_a):
        """
        will eventually make many copies of this
        """
        return pymc.distributions.normal_like(value, 0, 1.0/pow(sigma,2))

    @pymc.deterministic(name = 'MM_mu_%s_a' % pid)
    def MM_mu_i_a(anchor = mu_pop_a_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_a, e = MM_epsilon_i_mu_a):
        inside = (X_i - X_pop).dot(B) + e
        ans = g_mu_a(anchor + inside)
        return ans

    VM_epsilon_i_mu_a[pid] = MM_epsilon_i_mu_a
    VM_mu_i_a[pid] = MM_mu_i_a




####################
# model for \rho_i^a#
####################


"""
here, define model for \rho_i^a.  it will NOT depend on covariates
\rho_i^a will be some diffuse distribution in (0,1).  let's say uniform for now
"""

VM_rho_i_a = {}

for pid in pid_iterator:

    @pymc.stochastic(name = 'MM_rho_%s_a' % pid, observed = False)
    def MM_rho_i_a(value = MM_rho_i_a_initial):
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

    @pymc.stochastic(name = 'MM_a_%s' % pid, observed = False)
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



@pymc.stochastic(observed = True)
def MM_sigma_epsilon_mu_b(value = .08, max = K_epsilon_mu_b):
    return pymc.distributions.uniform_like(value, 0, max)


VM_epsilon_i_mu_b = {}
VM_mu_i_b = {}

for pid in pid_iterator:

    @pymc.stochastic(name = 'MM_epsilon_%s_mu_b' % pid,observed = True)
    def MM_epsilon_i_mu_b(value = 0, sigma = MM_sigma_epsilon_mu_b):
        """
        will eventually make many copies of this
        """
        return pymc.distributions.normal_like(value, 0, 1.0/pow(sigma,2))

    @pymc.deterministic(name = 'MM_mu_%s_b' % pid)
    def MM_mu_i_b(anchor = mu_pop_b_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_b, e = MM_epsilon_i_mu_b):
        inside = (X_i - X_pop).dot(B) + e
        ans = g_mu_b(anchor + inside)
        return ans

    VM_epsilon_i_mu_b[pid] = MM_epsilon_i_mu_b
    VM_mu_i_b[pid] = MM_mu_i_b




####################
# model for \rho_i^b#
####################


"""
here, define model for \rho_i^b.  it will NOT depend on covariates
\rho_i^b will be some diffuse distribution in (0,1).  let's say uniform for now
"""

VM_rho_i_b = {}

for pid in pid_iterator:

    @pymc.stochastic(name = 'MM_rho_%s_b' % pid, observed = True)
    def MM_rho_i_b(value = MM_rho_i_b_initial):
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

    @pymc.stochastic(name = 'MM_b_%s' % pid, observed = False)
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

    @pymc.deterministic(name = 'MM_mu_%s_c' % pid)
    def MM_mu_i_c(anchor = mu_pop_c_prime, X_pop = X_pop, X_i = X.loc[pid], B = MM_B_mu_c):
        inside = (X_i - X_pop).dot(B)
        ans = g_mu_c(anchor + inside)
        return ans

    VM_mu_i_c[pid] = MM_mu_i_c


VM_c_i = {}

for pid in pid_iterator:
    @pymc.deterministic(name = 'MM_c_%s' % pid)
    def MM_c_i(mu = VM_mu_i_c[pid]):
        return mu

    VM_c_i[pid] = MM_c_i
