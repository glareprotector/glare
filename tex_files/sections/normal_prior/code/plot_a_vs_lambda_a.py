import get_model
import matplotlib.pyplot as plt


file_name = '../files/pdf_vs_lambda_a.png'

stds = [.1, .3, .5, .7]
l_as = [1,5,10,15,20]

fig = plt.figure()


for std, i in zip(stds, range(4)):
    
    ax = fig.add_subplot(2,2,i+1)
    ax = get_model.plot_a_for_several_l_a(ax, 20000, 0.7, 0.7, 0.7, std, 0.3, 0.3, l_as, 10, 10)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$p(x)$')
    ax.set_title(r'$\tilde{\sigma}^a=$' + str(std))

ax.legend(loc='best', prop = {'size':6})

fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

plt.savefig(file_name)

fig.show()
