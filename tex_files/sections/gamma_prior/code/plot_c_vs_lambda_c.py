import get_model
import matplotlib.pyplot as plt


file_name = '../files/pdf_vs_lambda_c.png'

stds = [.1, .3, .5, .7]
l_cs = [1,5,10,15,20]

fig = plt.figure()


for std, i in zip(stds, range(4)):
    
    ax = fig.add_subplot(2,2,i+1)
    ax = get_model.plot_c_for_several_l_c(ax, 20000, 0.7, 0.7, 2.0, 0.3, 0.3, std, 10, 10, l_cs)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$p(x)$')
    ax.set_title(r'$\tilde{\sigma}^c=$' + str(std))

ax.legend(loc='best', prop = {'size':6})

fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

plt.savefig(file_name)

fig.show()
