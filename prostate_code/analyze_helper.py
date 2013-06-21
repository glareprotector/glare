import pandas



"""
consists of methods that take in folders
"""

def plot_parameters(folder):
    """
    given results folder, plots in the same folder, histograms of the 7 parameters
    """
    fig = plt.figure()

    

    ax = fig.add_subplot(2,2,1)
    B_a = pandas.read_csv(folder + 'out_B_a.csv',header=None,index_col=False)
    alphas = [1,0.5]
    colors = ['r','g']
    for i,alpha,color in zip(range(B_a.shape[1]),alphas,colors):
        ax.hist(B_a[i], bins=40,histtype='stepfilled',color=color,alpha=alpha)
    ax.set_title('B_a')

    ax = fig.add_subplot(2,2,2)
    B_b = pandas.read_csv(folder + 'out_B_b.csv',header=None)
    alphas = [1,0.5]
    colors = ['r','g']
    for i,alpha,color in zip(range(B_b.shape[1]),alphas,colors):
        ax.hist(B_b[i], bins=40,histtype='stepfilled',color=color,alpha=alpha)
    ax.set_title('B_b')

    ax = fig.add_subplot(2,2,3)
    B_c = pandas.read_csv(folder + 'out_B_c.csv',header=None)
    alphas = [1,0.5]
    colors = ['r','g']
    for i,alpha,color in zip(range(B_c.shape[1]),alphas,colors):
        ax.hist(B_c[i], bins=40,histtype='stepfilled',color=color,alpha=alpha)
    ax.set_title('B_c')

    abc_file = folder + 'B_abc_hist.png'
    fig.savefig(abc_file)



    fig = plt.figure()

    

    ax = fig.add_subplot(2,2,1)
    phi_a = pandas.read_csv(folder + 'out_phi_a.csv',header=None,index_col=False)
    ax.hist([phi_a[i] for i in range(phi_a.shape[1])], bins=40)
    ax.set_title(r'$\phi^a$')

    ax = fig.add_subplot(2,2,2)
    phi_b = pandas.read_csv(folder + 'out_phi_b.csv',header=None)
    ax.hist([phi_b[i] for i in range(phi_b.shape[1])], bins=40)
    ax.set_title(r'$\phi^b$')

    ax = fig.add_subplot(2,2,3)
    phi_c = pandas.read_csv(folder + 'out_phi_c.csv',header=None)
    ax.hist([phi_c[i] for i in range(phi_c.shape[1])], bins=40)
    ax.set_title(r'$\phi^c$')

    ax = fig.add_subplot(2,2,4)
    phi_m = pandas.read_csv(folder + 'out_phi_m.csv',header=None)
    ax.hist([phi_m[i] for i in range(phi_m.shape[1])], bins=40)
    ax.set_title(r'$\phi^b$')

    phi_file = folder + 'B_phi_hist.png'
    fig.savefig(phi_file)



def read_posterior_parameters(folder):

    




def get_posterior_predictive(train_folder, test_folder):
    """
    given a folder with posterior_parameters folder, and data folder, uses posterior parameters to get distribution of data 

    different kinds of data items: data, parameters
    can: write data using python, read data using R, write parameters using R
    still need to: read parameters using python,  
    when doing this analysis,  will iterate
    need to be able to go from sideeffect/treatment/fold to folder which has train
    """
