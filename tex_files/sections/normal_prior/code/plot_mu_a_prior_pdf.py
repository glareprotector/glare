import matplotlib.pyplot as plt
from logistic_normal_helper import *


file_name = '../files/mu_a_pdf.png'


actual_mus = [.5,.6,.7,.8]
mus = [logit(x) for x in actual_mus]
#stds = [.1,.2,.3,.4,.5,.6,.7,.8,.9]
#stds = [0.1, .2, .4, .6, .8, 1.0]
stds = [.1,.3,.5,.7,.9,1.1,1.3]
stds= [.1,.4,.7,1.1,2]
fig = plt.figure()

print stds

for actual_mu, mu, i in zip(actual_mus, mus, range(len(mus))):

    ax = fig.add_subplot(2,2,i+1)
    plot_several_pdfs(ax, mu, stds)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$p(x)$')
    ax.set_title(r'$\mu_{pop}^a=$'+str(actual_mu))
    #ax.yaxis.set_ticks([0,0.5,1.0])
    ax.minorticks_off()
    ax.axvline(x=logistic(mu))

fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

ax.legend(loc = 'best')

plt.savefig(file_name)

#plt.show()
