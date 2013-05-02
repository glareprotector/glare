import pymc
import math
import matplotlib.pyplot as plt
import helper

"""
define mu, v
define b ~ N(0, v)
define y = f(a + b) where f is logistic function, a = f^{-1}(mu)
define s_0 ~ beta(mu = y, rho = rho)
"""

def f(x):
    return 1.0 / (1.0 + math.exp(-1.0 * x))

def f_inv(y):
    return math.log(y / (1.0 - y))

num_samples = 1000
v = 0.08
mu = 0.8
rho = 0.1

a = f_inv(mu)

@pymc.stochastic
def b(value = 0.0):
    return pymc.distributions.normal_like(value, 0, v)

@pymc.deterministic
def y(value = 0.8, anchor = a, b = b):
    return f(a + b)

@pymc.stochastic
def s_0(value = 0.08, mu = y, rho = rho):
    alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, rho)
    return pymc.distributions.beta_like(value, alpha, beta)


M = pymc.MCMC([y, b, s_0])
M.sample(num_samples)

plt.hist(M.trace('s_0')[:])
plt.show()
