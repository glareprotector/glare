import pandas
import basic_features as bf
import pdb
import my_exceptions
import ucla_features as uf
import helper
import numpy as np
from helper import get_branded_version as brand
import functools

class treatment(object):
    def __init__(self, indicator_f, name):
        self.indicator_f, self.name = indicator_f, name

class side_effect(object):
    def __init__(self, raw_series_getter, name):
        self.raw_series_getter, self.name = raw_series_getter, name

class attribute(object):
    def __init__(self, f, name):
        self.f, self.name = f, name

class model(object):
    def __init__(self, train_script, name):
        self.train_script, self.name = train_script, name

def raise_if_too_short(x, l):
    if len(x) < l:
        raise my_exceptions.NoFxnValueException
    return x

raise_len_f = functools.partial(raise_if_too_short, l=7)

treatment_brachytherapy = treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.brachy), 'brachytherapy')
treatment_surgery = treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.surgery), 'surgery')
treatment_radiation = treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.radiation), 'radiation')

side_effect_urinary_function = side_effect(bf.compose(raise_len_f,bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.urinary_function)), 'urinary_function')
side_effect_bowel_function = side_effect(bf.compose(raise_len_f,bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.bowel_function)), 'bowel_function')
side_effect_sexual_function = side_effect(bf.compose(raise_len_f,bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.sexual_function)), 'sexual_function')

attribute_age = brand(bf.always_raise,'age')(uf.ucla_feature(uf.ucla_feature.age))

model_full = model('Rscript /Users/glareprotector/prostate_git/glare/prostate_code/train_full_model.r', 'full')


def se_treatment_fold_to_training_folder(base_folder, se, treatment, fold_i, fold_k):
    """
    used to figure out where the training data is
    """
    return base_folder + se.name + '/' + treatment.name + '/fold_' + str(fold_i) + '_' + str(fold_k) + '/train/'


def se_treatment_fold_to_testing_folder(base_folder, se, treatment, fold_i, fold_k):
    """
    used to figure out where the training data is
    """
    return base_folder + se.name + '/' + treatment.name + '/fold_' + str(fold_i) + '_' + str(fold_k) + '/test/'


def se_treatment_fold_model_to_posterior_folder(base_folder, se, treatment, fold_i, fold_k, model):
    """
    used to figure out where to store the results of inference
    """
    return base_folder + se.name + '/' + treatment.name + '/fold_' + str(fold_i) + '_' + str(fold_k) + '/train/posterior_parameters/' + model.name + '/'


def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


"""
consists of methods that take in folders
"""

def write_x_datapoints_abcs(d, base_folder):


    make_folder(base_folder)

    x_stuff_f = lambda v: v.cov.x
    x_df = helper.dict_of_series_to_dataframe(d, x_stuff_f)

    x_df.to_csv(base_folder + 'xs.csv')

    ss = [v.cov.s for k,v in d.iteritems()]
    pids = [k for k,v in d.iteritems()]
    ss_series = pandas.Series(ss,index=pids)
    ss_series.to_csv(base_folder + 'ss.csv')

    datapoints_folder = base_folder + 'datapoints/'
    make_folder(datapoints_folder)

    datapoints_f = lambda v: v.data_points
    datapoints_file_f = lambda k: datapoints_folder + k
    datapoints_write_f = lambda dp,f: dp.to_csv(f)
    helper.write_dict_stuff_by_folder(d, datapoints_f, datapoints_write_f, datapoints_file_f)
    
    """
    write as,bc,cs to file
    """
    as_d, bs_d, cs_d = {},{},{}

    for k,v in d.iteritems():
        as_d[k] = v.a
        bs_d[k] = v.b
        cs_d[k] = v.c

    a_series = pandas.Series(as_d)
    b_series = pandas.Series(bs_d)
    c_series = pandas.Series(cs_d)

    a_series.to_csv(base_folder + 'as.csv')
    b_series.to_csv(base_folder + 'bs.csv')
    c_series.to_csv(base_folder + 'cs.csv')

def read_data_from_folder(folder):



    a_s = pandas.read_csv(folder + 'as.csv', index_col=0, header=None, squeeze=True)
    b_s = pandas.read_csv(folder + 'bs.csv', index_col=0, header=None, squeeze=True)
    c_s = pandas.read_csv(folder + 'cs.csv', index_col=0, header=None, squeeze=True)
    s_s = pandas.read_csv(folder + 'ss.csv', index_col=0, header=None, squeeze=True)

    xs = pandas.read_csv(folder + 'xs.csv', header=0, index_col=0)

    def read_datapoints_file(pid):
        path = folder + 'datapoints/' + str(pid)
        return pandas.read_csv(path, index_col=0,header=None)

    pids = s_s.index

    import helper

    d = {}

    for pid in pids:
        d[str(pid)] = helper.all_data(helper.cov(xs.loc[pid],s_s[pid]), a_s[pid], b_s[pid], c_s[pid])

    return d


def all_data


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
    """
    assumes folder is a posterior_parameters folder.  reads in each of the 7 parameters
    """
    B_a_trace = pandas.read_csv(folder+'out_B_a.csv', header=None,)
    B_b_trace = pandas.read_csv(folder+'out_B_b.csv', header=None)
    B_c_trace = pandas.read_csv(folder+'out_B_c.csv', header=None)



def get_posterior_predictive(train_folder, test_folder):
    """
    given a folder with posterior_parameters folder, and data folder, uses posterior parameters to get distribution of data 

    different kinds of data items: data, parameters
    can: write data using python, read data using R, write parameters using R
    still need to: read parameters using python,  
    when doing this analysis,  will iterate
    need to be able to go from sideeffect/treatment/fold to folder which has train
    """
