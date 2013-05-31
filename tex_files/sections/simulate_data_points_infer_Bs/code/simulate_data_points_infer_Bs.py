import prior_Bs_fixed_model, model_with_data_points
import get_model_new as get_model
import helper
import numpy.random
import numpy as np
import matplotlib.pyplot as plt
import pdb
import pymc
import plot_helper
import pandas


out_prefix = 'fixing_abc_'
save_folder = '../files/'

db_file = save_folder + 'trace.db'

As_trace_file = save_folder + 'As_trace'
Bs_trace_file = save_folder + 'Bs_trace'
Cs_trace_file = save_folder + 'Cs_trace'

simulate_num = 1
simulate_steps = 30000
b_a, b_b, b_c = -1.0, 1.0, 2.0
infer_steps = 100000
flush_steps = 2000
twod_num = 25

simulate_noise_sd = 0.3
simulate_max_time = 2
simulate_num_points = 7

mu_pop_a = 0.5
mu_pop_b = 0.5
mu_pop_c = 0.5

simulate_rho_a = 0.02
simulate_rho_b = 0.02
simulate_rho_c = 0.02

simulate_mode = 'deterministic'

raw_xs = helper.seq(-1,1,50)



time_points = [0.0, 0.01, 0.1, 0.3, 0.6, 2.0,4.0,9.0]
#time_points = [0.0,1.0]

#Xs = [np.array([x,x]) for x in raw_xs]
Xs = [pandas.Series([x]) for x in raw_xs]
pids = [str(i) for i in range(len(Xs))]
#B_a, B_b, B_c = np.array([b_a, b_a]), np.array([b_b, b_b]), np.array([b_c, b_c])
B_a, B_b, B_c = np.array([b_a]), np.array([b_b]), np.array([b_c])


def write_nums(file, l):
    f = open(file, 'w')
    for n in l:
        f.write('%.4f' % n)
        f.write('\n')
    f.close()


####################################################
# simulate the data.  can just do deterministically#
####################################################

simulated_abcs, simulated_data = get_model.get_simulated_datas_and_abc(Xs, pids, simulate_mode, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c, time_points, simulate_noise_sd, simulate_rho_a, simulate_rho_b, simulate_rho_c)

pdb.set_trace()

####################################################
# get a variable manager with those abc data added #
####################################################



infer_manager = model_with_data_points.get_model_manager(simulated_data, pids, mu_pop_a, mu_pop_b, mu_pop_c, B_a, B_b, B_c)

import model_with_abc_data
#infer_manager = model_with_abc_data.get_model_manager(simulated_abcs, pids, mu_pop_a, mu_pop_b, mu_pop_c)

infer_model = get_model.get_model_using_variable_manager(infer_manager, 'MCMC', db_file)
print 'initial logp from configuration I defined: ', infer_model.logp




#####################################
# designate the step methods to use #
#####################################

for var in infer_model.stochastics:
    infer_model.use_step_method(pymc.Metropolis, var, proposal_sd=.1, proposal_distribution='Normal')

#####################################
# get the MLE values of B_a and B_b #
#####################################

if False:

    infer_model_map = get_model.get_model_using_variable_manager(infer_manager, 'MAP')
    infer_model_map.fit()
    max_a, max_b = infer_model_map.get_node('B_a').value, infer_model_map.get_node('B_b').value
    print 'MLE values for B_a and B_b: ', max_a, max_b
    print 'MLE likelihood: ', infer_model_map.logp



##############################################################################
# Do some plotting of the likelihood and related functions at various points #
##############################################################################

ba_test_vals = helper.seq(-2,2,twod_num)
bb_test_vals = helper.seq(-2,2,twod_num)
bc_test_vals = helper.seq(-2,2,twod_num)




##################################################
# plot 1d likelihood vs B's to see where peak is #
##################################################

if False:

    likelihood_plot_file = save_folder + out_prefix + 'likelihood_vs_Bs'

    pos = 0

    plot_helper.plot_1d_likelihoods(likelihood_plot_file, ba_test_vals, bb_test_vals, bc_test_vals, infer_model, pos)




###############################
# plot likelihood surface plot#
###############################

if False:

    likelihood_2d_plot_file = save_folder + out_prefix + 'likelihood_2d_vs_Bs'

    contour_ax = plot_helper.plot_contour_2d(likelihood_2d_plot_file, ba_test_vals, bb_test_vals, infer_model, max_a, max_b, pos)






#######################################
# plot curves for the used covariates #
#######################################

if False:

    simulated_curves_file = save_folder + out_prefix + 'simulated_curves.png'

    plot_helper.plot_curves(simulated_curves_file, Xs, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c, time_points, 10)




############################################################################################
# set the starting configuration of infer_model to be of just calculated MLE configuration #
############################################################################################

if False:
    for var in infer_model_map.stochastics:
        infer_model.get_node(var.__name__).value = var.value



#############################################################
# run infer_model and store values of all relevant variables#
#############################################################

if True:

    infer_model.sample(flush_steps, verbose = 0, burn=flush_steps, tune_throughout=False)
    B_a_vals = []
    B_b_vals = []
    B_c_vals = []
    count = 0
    while count < infer_steps:

            

        infer_model.sample(flush_steps, verbose = 0, burn = 0, tune_throughout = False)

        B_a_vals = B_a_vals + [x[0] for x in infer_model.trace('B_a')[:]]
        B_b_vals = B_b_vals + [x[0] for x in infer_model.trace('B_b')[:]]
        B_c_vals = B_c_vals + [x[0] for x in infer_model.trace('B_c')[:]]


        write_nums(As_trace_file, B_a_vals)
        write_nums(Bs_trace_file, B_b_vals)
        write_nums(Cs_trace_file, B_c_vals)


        histogram_file = save_folder + out_prefix + 'Bs_histogram.png'
        plot_helper.plot_Bs_histogram_given_samples(histogram_file, B_a_vals, B_b_vals, B_c_vals)

        trace_file = save_folder + out_prefix + 'Bs_trace.png'

        plot_helper.plot_Bs_trace_given_samples(trace_file, B_a_vals, B_b_vals, B_c_vals)
        count = count + flush_steps
        print 'STEPS: ', count


    B_a_vals = infer_model.trace(infer_manager.get_variable_name('B_a'))[:]
    B_b_vals = infer_model.trace(infer_manager.get_variable_name('B_b'))[:]
    B_c_vals = infer_model.trace(infer_manager.get_variable_name('B_c'))[:]


    a_i_vals, b_i_vals, c_i_vals = {}, {}, {}
    pdb.set_trace()
    #for pid in pids:
    #    a_i_vals[pid] = infer_model.trace(infer_manager.get_pid_variable_name('a',pid))[:]
    #    b_i_vals[pid] = infer_model.trace(infer_manager.get_pid_variable_name('b',pid))[:]
    #    c_i_vals[pid] = infer_model.trace(infer_manager.get_pid_variable_name('c',pid))[:]




########################
# plot histogram of B's#
########################

if True:

    histogram_file = save_folder + out_prefix + 'Bs_histogram.png'

    plot_helper.plot_Bs_histogram(histogram_file, infer_model)





####################################################
# print out simulated abc vs mean of posterior abc #
####################################################

if False:

    for pid in pids:
        print pid, 'a: ', simulated_abcs[pid].a, np.mean(a_i_vals[pid]), 'b: ', simulated_abcs[pid].b, np.mean(b_i_vals[pid]), 'c: ', simulated_abcs[pid].c, np.mean(c_i_vals[pid])
    



####################
# plot trace of Bs #
####################

if True:

    trace_file = save_folder + out_prefix + 'Bs_trace.png'

    plot_helper.plot_Bs_trace(trace_file, infer_model)



######################
# plot trace of logps#
######################

if False:

    log_p_trace_file = save_folder + out_prefix + 'log_p_trace.png'

    plot_helper.plot_logp_trace(log_p_trace_file, infer_model)



######################
# plot trace of rhos #
######################

if False:

    rho_trace_file = save_folder + out_prefix + 'rhos_trace.png'

    plot_helper.plot_rho_trace(rho_trace_file, infer_model)




############################################################################
# plot curves generated using mean posterior parameters and used covariates#
############################################################################

if False:

    posterior_curves_file = save_folder + out_prefix + 'posterior_curves.png'
                                
    mean_posterior_B_a = np.mean(np.ndarray(B_a_vals), axis=0)
    mean_posterior_B_b = np.mean(np.ndarray(B_a_vals), axis=0)
    mean_posterior_B_c = np.mean(np.ndarray(B_a_vals), axis=0)
                                
    plot_helper.plot_curves(postererior_curves_file, Xs, mean_posterior_B_a, mean_posterior_B_b, mean_posterior_B_c, mu_pop_a, mu_pop_b, mu_pop_c, time_points, 10)




###########################
# print out summary stats #
###########################

if True:

    print infer_model.get_node('B_a').summary()
    print infer_model.get_node('B_b').summary()
    print infer_model.get_node('B_c').summary()

pdb.set_trace()
