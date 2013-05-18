from log_normal_helper import *
import matplotlib.pyplot as plt
import math
import pdb
import helper

file_name = '../files/mode_vs_sigma.png'

fig = plt.figure()

actual_mus = [0.5,1.0, 1.5, 2.0]

mus = [math.log(x) for x in actual_mus]

max_std = 3

stds = helper.seq(0,3,30)

for actual_mu, mu, i in zip(actual_mus, mus, range(4)):

    ax = fig.add_subplot(2,2,i+1)
    
    y_vals = [log_normal_mode(mu, std) for std in stds]

    ax.plot(stds, y_vals)

    ax.set_ylabel(r'mode of p(x)')

    ax.set_xlabel(r'$\sigma^c$')

    ax.set_title('$\mu_{pop}^c = %s$' % actual_mu)

fig.subplots_adjust(hspace = 0.4, wspace = 0.25)  

plt.savefig(file_name)


plt.show()
