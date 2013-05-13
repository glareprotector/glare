import matplotlib.pyplot as plt
import math
import scipy.optimize
import scipy.integrate
import numpy.random

def logit(x):
    return math.log(x/(1.0-x))

def logistic(x):
    return 1.0 / (1.0 + math.exp(-1.0 * x))

def logit_normal_pdf(x, mu, sigma):

    return math.exp(-1.0 * (pow(logit(x)-mu,2) / (2*pow(sigma,2)))) / (x*(1-x)*2*pow(2*math.pi,0.5))

    import scipy.stats
    import helper
    alpha, beta = helper.beta_mu_rho_to_alpha_beta(mu, sigma)

    return scipy.stats.beta.pdf(x, alpha, beta)



def plot_pdf(ax, mu, sigmas):

    num_points = 1000
    x_vals = [x / float(num_points) for x in xrange(1,num_points)]

    for sigma in sigmas:
        y_vals = [logit_normal_pdf(x, mu, sigma) for x in x_vals]
        ax.plot(x_vals, y_vals, label = r'$\sigma=$'+str(sigma))

def logit_normal_mode(mu, sigma):

    def root_eq(x):
        #return pow(sigma,2) * (2.0*x - 1) + mu - logit(x)
        return pow(sigma,2) * (2.0*logistic(x) - 1) + mu - x
    ans = logistic(scipy.optimize.broyden1(root_eq, 0.5))

    return ans
    #scipy.optimize.broyden1(root_eq, logistic(mu))

def logit_normal_mean(mu, sigma):

    print mu, sigma

    def f(x):
        return x * logit_normal_pdf(x, mu, sigma)

    ans = scipy.integrate.quad(f, 0, 1)
    print ans
    return ans
        
    return ev

def logit_normal_mean_sampling(mu, sigma):

    num_samples = 10000

    samples = [logistic(numpy.random.normal(mu, sigma)) for x in xrange(num_samples)]

    ans = numpy.sum(samples) / num_samples

    print ans

    return ans

def plot_mode(ax, mu, stds):
    modes = [logit_normal_mode(mu, std) for std in stds]
    ax.plot(stds, modes)
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])

def plot_mean(ax, mu, stds):
    print mu
    means = [logit_normal_mean_sampling(mu, std) for std in stds]
    ax.plot(stds, means)
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])

def plot_several_pdfs(ax, mu, stds):
    plot_pdf(ax, mu, stds)

