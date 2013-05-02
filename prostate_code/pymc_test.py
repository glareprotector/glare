import pymc
import basic_features as bf
import ucla_features as uf
from pymc.distributions import *
import numpy as np
from helper import get_branded_version as brand
import helper
import pdb

###########################
# useful container classes#
###########################

class attribute_info(object):

    def __init__(self, attribute_f, name, coefficient_prior_var):
        self.attribute_f, self.name, self.coefficient_prior_var = attribute_f, name, coefficient_prior_var


########################################
# variables to define for this analysis#
########################################

treatment = uf.ucla_treatment_code_f.surgery
treatment_iterator = treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), bf.indicator_feature(uf.ucla_treatment_code_f(), treatment))

attributes = [attribute_info(brand(bf.always_one,'one')(), 'one', 10), \
                attribute_info(brand(uf.ucla_feature,'age')(uf.ucla_feature.age), 'age', 10), \
                attribute_info(brand(uf.ucla_feature,'gleason')(uf.ucla_feature.gleason), 'gleason', 10), \
                attribute_info(brand(uf.ucla_feature,'psa')(uf.ucla_feature.psa), 'psa', 10)]

df = bf.data_frame_feature()(treatment_iterator, [attribute.attribute_f for attribute in attributes])

side_effects = [brand(bf.single_time_processed_time_series,'sexual_func')(bf.processed_exact_time_series_getter(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.sexual_function)), helper.my_timedelta(days=1*30)), \
                   brand(bf.single_time_processed_time_series,'urinary_func')(bf.processed_exact_time_series_getter(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.urinary_function)), helper.my_timedelta(days=1*30))]

####################
# Model Description#
####################
"""
 - focus on 1 treatment, 1 side effect for now
 - side_effect_val = B * X + N(0, sigma)      
 - B_i ~ unif(-100,100)                       
 - sigma ~ unif(-100,100)                     
"""

#################################
# define the variables for model#
#################################
side_effect = side_effects[0]
num_attributes = len(attributes)
raw_Y = bf.feature_applier(side_effect)(treatment_iterator)
temp_df = df
temp_df[str(side_effect)] = raw_Y
temp_df = temp_df.dropna(axis=0)
X = temp_df.loc[:,[attribute.name for attribute in attributes]]
Y = temp_df[str(side_effect)]

sigma = Uniform('sigma_var_prior', -10, 10)
C = np.diag([x.coefficient_prior_var for x in attributes])
B = MvNormalCov('B', np.zeros(num_attributes), C)



@pymc.deterministic
def mu(B=B):
    return np.dot(X,B)

Y = Normal('Y', mu, sigma, value=Y, observed=True)

    
M = pymc.MCMC(set([sigma, B, mu, Y]))




def mean(x):
    sum = 0
    for i in x:
        sum += i
    return sum 

M.sample(iter=200000,burn=1000, thin=10)
import matplotlib.pyplot as plt

for i, name in zip(range(4), ['one','age','gleason','psa']):
    fig=plt.figure()
    ax = fig.add_subplot(111)
    ax.hist([M.trace('B')[k][i] for k in range(M.trace('B').length())])
    fig.suptitle(name)
    plt.savefig(name+'.png')


pdb.set_trace()
