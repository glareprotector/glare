import prior_Bs_fixed_model, model_with_data_points
import get_model_new as get_model
import helper
import numpy.random
import numpy as np
import matplotlib.pyplot as plt
import pdb
import pymc

simulate_num = 1
simulate_steps = 100
b_a, b_b, b_c = -1.0, 1.0, 2.0
infer_steps = 20000

simulate_noise_sd = 0.03
simulate_max_time = 2
simulate_num_points = 7

mu_pop_a = 0.5
mu_pop_b = 0.5
mu_pop_c = 0.5

simulate_rho_a = 0.2
simulate_rho_b = 0.2
simulate_rho_c = 0.2


out_file = '../files/Bs_histogram.png'

"""
assume there is only 1 patient attribute, and that s is always = 1.0
draw several patient attributes about 0, simulate, save
"""

####################################################
# simulate the data.  can just do deterministically#
####################################################

#xs = [numpy.random.normal(0,1) for i in range(simulate_num)]
xs = helper.seq(-1, 1, simulate_num)
#xs = [1.0 for x in range(simulate_num)]
pdb.set_trace()
simulated_data = []



time_points = [0.0, 0.01, 0.1, 0.3, 0.6, 2.0,4.0,9.0]
#time_points = [0]
xs = [-1.0, 1.0]
xs = helper.seq(-2, 2, 15)

simulated_as = {}
simulated_bs = {}
simulated_cs = {}

pids = [str(i) for i in range(len(xs))]

for x,pid in zip(xs, pids):

    B_a = np.array([b_a])
    B_b = np.array([b_b])
    B_c = np.array([b_c])
    the_cov = helper.cov(np.array([x]), 1.0)
    a,b,c = get_model.get_deterministic_abc_given_x_and_Bs(the_cov, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
    

    #a,b,c = get_model.get_abc_given_xs_sample(the_cov, simulate_rho_a, simulate_rho_b, simulate_rho_c, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
    data_points = get_model.get_data_points_given_abc(1.0, a, b, c, time_points, simulate_noise_sd)
    the_complete_data = helper.complete_data(the_cov, data_points)
    simulated_data.append(the_complete_data)
    simulated_as[pid] = a
    simulated_bs[pid] = b
    simulated_cs[pid] = c

pdb.set_trace()

####################################################
# get a variable manager with those abc data added #
####################################################



infer_manager = model_with_data_points.get_model_manager(simulated_data, pids, mu_pop_a, mu_pop_b, mu_pop_c, b_a, b_b, b_c)
infer_model = get_model.get_model_using_variable_manager(infer_manager, 'MCMC')

#infer_model.fit()
#max_a, max_b = infer_model.get_node('B_a').value, infer_model.get_node('B_b').value




###############################################
# plot likelihood vs B's to see where peak is #
###############################################
likelihood_plot_file = '../files/likelihood_vs_Bs'
fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
test_vals = helper.seq(-10,10,50)
dot_size = .01

bb_log_ps = []
for try_bb in test_vals:
    infer_model.get_node('B_b').value = try_bb
    logp = infer_model.logp
    bb_log_ps.append(logp)
ax = fig.add_subplot(2,2,2)
ax.scatter(test_vals, bb_log_ps, s = dot_size)
ax.set_xlabel('B_b value')
ax.set_ylabel('logp')
ax.set_title('B_b vs logp')

infer_model.get_node('B_b').value = b_b

ba_log_ps = []
for try_ba in test_vals:
    infer_model.get_node('B_a').value = try_ba
    logp = infer_model.logp
    ba_log_ps.append(logp)
ax = fig.add_subplot(2,2,1)
ax.scatter(test_vals, ba_log_ps, s = dot_size)
ax.set_xlabel('B_a value')
ax.set_ylabel('logp')
ax.set_title('B_a vs logp')

infer_model.get_node('B_a').value = b_a

pdb.set_trace()
"""
###############################
# plot likelihood surface plot#
###############################
pdb.set_trace()
fig=plt.figure()
first, second = np.meshgrid(test_vals, test_vals)
likelihoods = np.ndarray((len(test_vals),len(test_vals)))
for ba,i in zip(test_vals,range(len(test_vals))):
    for bb,j in zip(test_vals,range(len(test_vals))):
        infer_model.get_node('B_a').value = ba
        infer_model.get_node('B_b').value = bb
        likelihoods[i,j] = infer_model.logp

ax = fig.add_subplot(111)
circle = plt.Circle((max_b, max_a),radius=.2)
ax.add_patch(circle)
ax.axhline(b_a, alpha=1, lw=3)
ax.axvline(b_b, alpha=1, lw=3)
CS = ax.contour(first, second, likelihoods, 80)
#plt.clabel(CS)
plt.show()
pdb.set_trace()

bc_log_ps = []
for try_bc in test_vals:
    infer_model.get_node('B_c').value = try_bc
    logp = infer_model.logp
    bc_log_ps.append(logp)
ax = fig.add_subplot(2,2,3)
ax.scatter(test_vals, bc_log_ps, s = dot_size)
ax.set_xlabel('B_c value')
ax.set_ylabel('logp')
ax.set_title('B_c vs logp')

infer_model.get_node('B_c').value = b_c

fig.savefig(likelihood_plot_file)
fig.show()

"""




#######################################
# plot curves for the used covariates #
#######################################
simulated_curves_file = '../files/simulated_curves.png'
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
for x in xs:
    a,b,c = get_model.get_deterministic_abc_given_x_and_Bs(helper.cov(np.array([x]),1.0), B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
    get_model.add_curve(ax, 1.0, a, b, c, 10, time_points)
fig.suptitle('simulated curves')
fig.savefig(simulated_curves_file)
fig.show()
pdb.set_trace()



for var in infer_model.stochastics:
    infer_model.use_step_method(pymc.Metropolis, var, proposal_sd=1., proposal_distribution='Normal')


###########################################
# run infer_model and plot histogram of Bs#
###########################################

pdb.set_trace()
#infer_model.isample(infer_steps, verbose = 0)
#B_a_vals = infer_model.trace(infer_manager.get_variable_name('B_a'))[:]
#B_b_vals = infer_model.trace(infer_manager.get_variable_name('B_b'))[:]
#B_c_vals = infer_model.trace(infer_manager.get_variable_name('B_c'))[:]

B_a_vals, B_b_vals, B_c_vals = [], [], []
a_i_vals, b_i_vals, c_i_vals = {}, {}, {}
for pid in pids:
    a_i_vals[pid] = []
    b_i_vals[pid] = []
    c_i_vals[pid] = []

log_p_vals = []
for i in xrange(1000):
    print i
    infer_model.sample(1,burn=1)
    B_a_vals.append(infer_model.get_node('B_a').value)
    B_b_vals.append(infer_model.get_node('B_b').value)
    B_c_vals.append(infer_model.get_node('B_c').value)
    log_p_vals.append(infer_model.logp)
    for pid in pids:
        a_i_vals[pid].append(infer_model.get_node(infer_manager.get_pid_variable_name('a',pid)).value)
        b_i_vals[pid].append(infer_model.get_node(infer_manager.get_pid_variable_name('b',pid)).value)
        c_i_vals[pid].append(infer_model.get_node(infer_manager.get_pid_variable_name('c',pid)).value)

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


####################################################
# print out simulated abc vs mean of posterior abc #
####################################################

for pid in pids:
    print pid, simulated_as[pid], np.mean(a_i_vals[pid])
    print pid, simulated_bs[pid], np.mean(b_i_vals[pid])
    print pid, simulated_cs[pid], np.mean(c_i_vals[pid])


####################
# plot trace of Bs #
####################

trace_file = '../files/Bs_trace.png'

fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
fig.suptitle('trace of Bs')


ax = fig.add_subplot(4,1,1)
ax.plot(B_a_vals)
ax.set_xlabel('iteration')
ax.set_ylabel('B_a value')

ax = fig.add_subplot(4,1,2)
ax.plot(B_b_vals)
ax.set_xlabel('iteration')
ax.set_ylabel('B_b value')

ax = fig.add_subplot(4,1,3)
ax.plot(B_c_vals)
ax.set_xlabel('iteration')
ax.set_ylabel('B_c value')

ax = fig.add_subplot(4,1,4)
ax.plot(log_p_vals)
ax.set_xlabel('iteration')
ax.set_ylabel('log_p value')

fig.show()
fig.savefig(trace_file)


######################
# plot trace of rhos #
######################
if False:

    rho_a_vals = infer_model.trace(infer_manager.get_variable_name('rho_a'))[:]
    rho_b_vals = infer_model.trace(infer_manager.get_variable_name('rho_b'))[:]
    rho_c_vals = infer_model.trace(infer_manager.get_variable_name('rho_c'))[:]
    rho_noise_vals = infer_model.trace(infer_manager.get_variable_name('rho_noise'))[:]

    rho_trace_file = '../files/rhos_trace.png'

    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    fig.suptitle(r'trace of $\phi$s')


    ax = fig.add_subplot(4,1,1)
    ax.plot(rho_a_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_a$ val')

    ax = fig.add_subplot(4,1,2)
    ax.plot(rho_b_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_b$ val')

    ax = fig.add_subplot(4,1,3)
    ax.plot(rho_c_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_c$ val')

    ax = fig.add_subplot(4,1,4)
    ax.plot(rho_noise_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_{noise}$ val')
    
    fig.show()
    fig.savefig(rho_trace_file)



############################################################################
# plot curves generated using mean posterior parameters and used covariates#
############################################################################

posterior_curves_file = '../files/posterior_curves.png'
mean_posterior_B_a = np.mean(B_a_vals)
mean_posterior_B_b = np.mean(B_b_vals)
mean_posterior_B_c = np.mean(B_c_vals)
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
for x in xs:
    a,b,c = get_model.get_deterministic_abc_given_x_and_Bs(helper.cov(np.array([x]),1.0), mean_posterior_B_a, mean_posterior_B_b, mean_posterior_B_c, mu_pop_a, mu_pop_b, mu_pop_c)
    get_model.add_curve(ax, 1.0, a, b, c, 10, time_points)

fig.savefig(posterior_curves_file)
fig.show()
pdb.set_trace()

pdb.set_trace()
