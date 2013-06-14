"""
has function that given a folder containing Rstan output, plots histograms of the 7 parameters (that's all for now)
new plots go in same folder
"""
import pandas
import matplotlib.pyplot as plt
import pdb

def plot_parameters(folder):

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


base_folder = '/Users/glareprotector/Documents/lab/glare/prostate_code/files_for_rstan/'

treatment_strings = ['surgery','radiation','brachytherapy']
side_effect_strings = ['sexual_function','bowel_function','urinary_function']

for se in side_effect_strings:

    for treatment in treatment_strings:

        folder = base_folder + se + '/' + treatment + '/'
        plot_parameters(folder)


