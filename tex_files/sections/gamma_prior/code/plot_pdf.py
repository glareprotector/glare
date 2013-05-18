from log_normal_helper import *
import matplotlib.pyplot as plt
import math
import pdb

file_name = '../files/several_pdfs.png'

fig = plt.figure()

actual_mus = [0.5,1.0, 1.5, 2.0]

mus = [math.log(x) for x in actual_mus]

stds = [.1,.3,.5,.7,.9,1.1,2.1]

for actual_mu, mu, i in zip(actual_mus, mus, range(4)):

    ax = fig.add_subplot(2,2,i+1)
    plot_pdf(ax, mu, stds, lambda std: r'$\tilde{\sigma}^c = %s$' % std)
    ax.set_title(r'$\mu_{pop}^c = %s$' % actual_mu)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$p(x)$')
    ax.set_xlim((0,5))
    ax.minorticks_off()
    ax.axvline(x=actual_mu)

fig.subplots_adjust(hspace = 0.4, wspace = 0.25) 

ax.legend(loc='best', prop={'size':8})


plt.savefig(file_name)

fig.show()

pdb.set_trace()