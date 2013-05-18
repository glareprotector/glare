import get_model
import basic_features as bf
from helper import get_branded_version as brand
import sys
import matplotlib.pyplot as plt
import pdb

"""
plots several prior curves for mu_a in one plot, with mu_a fixed and std of B_a varying.  change variances to be used by modifying variances list
usage: num_samples, mu_pop_a, title, out_file
"""
########################
# user input parameters#
########################

num_samples, mu_pop_a, title, out_file = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3], sys.argv[4]


############################
# non-user input parameters#
############################

"""
modify stds to change the variances for which prior curves are plotted
"""
#stds = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
stds = [0.2,0.4,0.6]
num_bins = 100
mu_pop_b, mu_pop_c = 0.5, 0.5
sigma_mu_b, sigma_mu_c = 1.0, 1.0

#######
# body#
#######

attribute_fs = [brand(bf.hard_coded_f,'age')(1)]
num_attributes = len(attribute_fs)
pid_iterator = bf.restricted_pid_iterable(bf.all_ucla_pid_iterable(), 1)
X = bf.data_frame_feature_alternate(attribute_fs)(pid_iterator)
X_pop = bf.dataset_aggregate_f(bf.hard_coded_f(0.0), bf.normalized_data_frame_f(bf.data_frame_feature_alternate(attribute_fs)))(pid_iterator)
the_pid = iter(pid_iterator).next()

plt.figure()

for std in stds:

    M = get_model.get_model(X, X_pop, mu_pop_a, mu_pop_c, mu_pop_c, std, sigma_mu_b, sigma_mu_c)
    M.sample(num_samples)

    """
    only care about the distribution of mu_a
    """
    a_var = 'MM_mu_%s_a' % the_pid
    a_vals = M.trace(a_var)[:]
    
    plt.hist(a_vals, label = r'$\sigma=$'+str(std), bins = num_bins, normed=True)

plt.legend()
plt.show()
