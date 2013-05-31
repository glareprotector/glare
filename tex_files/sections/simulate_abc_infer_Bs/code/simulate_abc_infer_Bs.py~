import prior_Bs_fixed_model
import get_model_new as get_model
import helper
import numpy.random
import numpy as np
import matplotlib.pyplot as plt

simulate_num = 10
simulate_steps = 100
b_a, b_b, b_c = 1.0, 2.0, 1.5
the_pid = '0'
infer_steps = 5000

out_file = '../files/Bs_histogram.png'

"""
assume there is only 1 patient attribute, and that s is always = 1.0
draw several patient attributes about 0, simulate, save
"""

####################
# simulate the data#
####################

xs = [numpy.random.normal(0,1) for i in range(simulate_num)]
simulated_data = []

for x in xs:

    pa = helper.patient_attributes(np.array([x]), 1.0)
    simulate_manager = prior_Bs_fixed_model.get_model_manager(pa, b_a, b_b, b_c, the_pid)
    simulate_model = get_model.get_model_using_variable_manager(simulate_manager)
    simulate_model.sample(simulate_steps)
    a = simulate_model.trace(simulate_manager.get_pid_variable_name('a', the_pid))[-1]
    b = simulate_model.trace(simulate_manager.get_pid_variable_name('b', the_pid))[-1]
    c = simulate_model.trace(simulate_manager.get_pid_variable_name('c', the_pid))[-1]
    simulated_data.append(helper.abc_data(pa, a, b, c))


####################################################
# get a variable manager with those abc data added #
####################################################

pids = [str(i) for i in range(len(simulate_num))]
assert len(pids) == len(simulated_data)
infer_manager = model_with_abc_data.get_model_manager(simulated_data, pids)
infer_model = get_model.get_model_using_variable_manager(infer_manager)

###########################################
# run infer_model and plot histogram of Bs#
###########################################

B_a_vals = infer_model.get_trace(infer_manager.get_variable_name('B_a'))[:]
B_b_vals = infer_model.get_trace(infer_manager.get_variable_name('B_b'))[:]
B_c_vals = infer_model.get_trace(infer_manager.get_variable_name('B_c'))[:]

fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
fig.set_title('histogram of Bs')
num_bins = 50

ax = fig.add_subplot(2,2,1)
ax.hist(B_a_vals, bins = num_bins)
ax.set_xlabel('B_a value')

ax = fig.add_subplot(2,2,1)
ax.hist(B_b_vals, bins = num_bins)
ax.set_xlabel('B_b value')

ax = fig.add_subplot(2,2,1)
ax.hist(B_c_vals, bins = num_bins)
ax.set_xlabel('B_c value')

fig.savefig(out_file)
fig.show()
