import matplotlib.pyplot as plt
from logistic_normal_helper import *

file_name = '../files/mu_a_mode_vs_sigma.png'

fig = plt.figure()

actual_mus = [.5,.6,.7,.8]
mus = [logit(x) for x in actual_mus]

num_stds = 20

stds = [x / float(num_stds) for x in xrange(1,num_stds)]

for actual_mu, mu, i in zip(actual_mus, mus, range(len(mus))):

    ax = fig.add_subplot(2,2,i+1)
    plot_mean(ax, mu, stds)
    ax.set_xlabel(r'$\tilde{\sigma^a}$')
    ax.set_ylabel(r'$mode of \tilde{\mu^a}|\tilde{\sigma^a}$')
    ax.set_title(r'$\mu_{pop}^a=$'+str(actual_mu))
    #ax.yaxis.set_ticks([0,0.5,1.0])
    ax.minorticks_off()
    ax.axvline(x=logistic(mu))
