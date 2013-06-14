import helper
import pymc
import matplotlib.pyplot as plt
import pdb

###################################################
# for 4 fixed phis, for set of modes, plot gamma pdf#
###################################################

if True:

    file_name = '../files/fixed_modes.png'

    four_phis = [.01, .1, .2,.5]
    modes = helper.seq(0,20,10)

    xs = helper.seq(0,100,2000)

    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

    for phi,i in zip(four_phis, range(4)):

        ax = fig.add_subplot(2,2,i+1)
        for m in modes:
            ax.plot(xs,[helper.pgamma_by_mode_phi(x,m,phi) for x in xs])
        ax.set_title(r'$\phi=$'+'%.4f'%phi)

    plt.show()

    pdb.set_trace()
