import prior_Bs_fixed_model, model_with_abc_data
import get_model_new as get_model
import helper
import numpy.random
import numpy as np
import matplotlib.pyplot as plt
import pdb

simulate_num = 4
simulate_steps = 100
b_a, b_b, b_c = 1.0, 2.0, 1.5

infer_steps = 180000

mu_pop_a = 0.5
mu_pop_b = 0.5
mu_pop_c = 0.5

out_file = '../files/Bs_histogram.png'

"""
assume there is only 1 patient attribute, and that s is always = 1.0
draw several patient attributes about 0, simulate, save
"""

####################################################
# simulate the data.  can just do deterministically#
####################################################

#xs = [numpy.random.normal(0,1) for i in range(simulate_num)]
xs = helper.seq(-2, 2, simulate_num)
pdb.set_trace()
simulated_data = []

for x in xs:

    B_a = np.array([b_a])
    B_b = np.array([b_b])
    B_c = np.array([b_c])
    the_cov = helper.cov(np.array([x]), 1.0)
    a,b,c = get_model.get_deterministic_abc_given_x_and_Bs(the_cov, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
    simulated_data.append(helper.abc_data(the_cov, a, b, c))

    """
    the_cov = helper.cov(np.array([x]), 1.0)
    simulate_manager = prior_Bs_fixed_model.get_model_manager(the_cov, b_a, b_b, b_c, the_pid)
    simulate_model = get_model.get_model_using_variable_manager(simulate_manager)
    simulate_model.sample(simulate_steps)
    a = simulate_model.trace(simulate_manager.get_pid_variable_name('mu_a', the_pid))[-1]
    b = simulate_model.trace(simulate_manager.get_pid_variable_name('mu_b', the_pid))[-1]
    c = simulate_model.trace(simulate_manager.get_pid_variable_name('mu_c', the_pid))[-1]
    simulated_data.append(helper.abc_data(the_cov, a, b, c))
    """

pdb.set_trace()

####################################################
# get a variable manager with those abc data added #
####################################################

pids = [str(i) for i in range(simulate_num)]
assert len(pids) == len(simulated_data)
infer_manager = model_with_abc_data.get_model_manager(simulated_data, pids, mu_pop_a, mu_pop_b, mu_pop_c)
infer_model = get_model.get_model_using_variable_manager(infer_manager)

###########################################
# run infer_model and plot histogram of Bs#
###########################################

pdb.set_trace()
infer_model.sample(infer_steps, verbose = 0)
B_a_vals = infer_model.trace(infer_manager.get_variable_name('B_a'))[:]
B_b_vals = infer_model.trace(infer_manager.get_variable_name('B_b'))[:]
B_c_vals = infer_model.trace(infer_manager.get_variable_name('B_c'))[:]

fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
fig.suptitle('histogram of Bs')
num_bins = 50

ax = fig.add_subplot(2,2,1)
ax.hist(B_a_vals, bins = num_bins)
ax.set_xlabel('B_a value')

ax = fig.add_subplot(2,2,2)
ax.hist(B_b_vals, bins = num_bins)
ax.set_xlabel('B_b value')

ax = fig.add_subplot(2,2,3)
ax.hist(B_c_vals, bins = num_bins)
ax.set_xlabel('B_c value')

fig.savefig(out_file)
fig.show()

pdb.set_trace()
