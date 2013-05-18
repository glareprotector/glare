import get_model
import matplotlib.pyplot as plt


stds = [.1, .3, .5, .7]

file_name = '../files/curve_priors.png'

fig = plt.figure()

for std,i in zip(stds, range(4)):

    ax = fig.add_subplot(2,2,i+1)

    ax = get_model.plot_curve_prior(ax, 4000, 0.3, 0.3, 2.0, std, std, std, 15, 15, 1)

    ax.set_title(r'$\tilde{\sigma}^a=\tilde{\sigma}^b=\tilde{\sigma}^c=$'+str(std))

fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

plt.savefig(file_name)
