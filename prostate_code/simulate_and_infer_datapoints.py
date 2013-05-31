import get_model_new
import numpy as np
import matplotlib.pyplot as plt
import pandas
import pdb
import pymc
import common_models

M = common_models.M
num_data = 10
simulate_rho_noise = 0.00001
simulate_num_steps = 5
simulate_num_points = 1
simulate_max_time = 1
num_samples_for_inference = 5000

#####################################################################################
# simulate datapoints.  store datapoints, covariates in M, and sampled abc elsewhere#
#####################################################################################


x_vals = []
a_vals = []
b_vals = []
c_vals = []
s_vals = []

pid_vals = []
x_vals = []
data_points_vals = []

temp_ys = []
temp_xs = []

for i in range(num_data):

    pid = str(i)
    x =pandas.Series([np.random.normal(0,1)])
    import helper
    #x =pandas.Series([helper.seq(-1,1,num_data+1)[i]])
    #x =pandas.Series([1.0])
    s = 1.0
    a,b,c, data_points = get_model_new.get_abc_and_data_points_given_xs(M, x, s, simulate_rho_noise, simulate_num_steps, simulate_num_points, simulate_max_time)
    x_vals.append(x)
    a_vals.append(a)
    b_vals.append(b)
    c_vals.append(c)
    s_vals.append(s)
    pid_vals.append(pid)
    data_points_vals.append(data_points)

    temp_ys += [d.value for d in data_points]
    temp_xs += [x[0] for i in range(simulate_num_points)]

for pid, x, data_points, s in zip(pid_vals, x_vals, data_points_vals, s_vals):
    M.set_pid_x(pid, x)
    M.set_pid_variable_value('s', pid, x)
    M.set_pid_data_points(pid, data_points)
    M.set_pid_data_observed(pid, True)


fig = plt.figure()
ax = fig.add_subplot(1,1,1)

ax.scatter(temp_xs, temp_ys)
fig.show()
pdb.set_trace()

##########################
# plot the simulated abc #
##########################

vectorized_x_vals = [x[0] for x in x_vals]

pdb.set_trace()

fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

ax = fig.add_subplot(2,2,1)
ax.scatter(vectorized_x_vals, a_vals)
ax.set_xlabel('value of the single covariate x')
ax.set_ylabel('value of a')
ax.set_title('a')

ax = fig.add_subplot(2,2,2)
ax.scatter(vectorized_x_vals, b_vals)
ax.set_xlabel('value of the single covariate x')
ax.set_ylabel('value of b')
ax.set_title('b')

ax = fig.add_subplot(2,2,3)
ax.scatter(vectorized_x_vals, c_vals)
ax.set_xlabel('value of the single covariate x')
ax.set_ylabel('value of c')
ax.set_title('c')

fig.show()
fig.savefig('/Users/glareprotector/prostate_git/glare/bin/abc_vs_covariates.png')


######################################################################
# make new model where B's are no longer fixed and the data is added #
######################################################################

M.set_variable_observed('B_a', False)
#M.set_variable_observed('B_b', False)
#M.set_variable_observed('B_c', False)

M.set_pid_variable_observed_blanket('a', False)
M.set_pid_variable_observed_blanket('b', False)
M.set_pid_variable_observed_blanket('c', False)

M.set_pid_data_observed_blanket(True)


M.set_variable_value('B_a', -2.0)

infer_model = get_model_new.get_model_using_variable_manager(M)


##################################################################################
# do inference with new model to get/plot posterior distribution of B_a, B_b, B_c#
##################################################################################



for var in infer_model.stochastics:
    infer_model.use_step_method(pymc.Metropolis, var, proposal_sd=.01, proposal_distribution='Normal', verbose=4)

import helper
aa = []
bb = []
for b in helper.seq(0,5,100):
    infer_model.get_node('B_a').value = b
    aa.append(b)
    bb.append(infer_model.logp)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(aa,bb)
ax.set_xlabel('parameter value')
ax.set_ylabel('log probability')
ax.set_title('log probability vs parameter value')
#plt.show()
pdb.set_trace()

infer_model.get_node('B_a').value = 2.0

ia = []
ip = []
iv = []

for i in range(100):
    infer_model.sample(2, burn=0, thin=1, tune_throughout=False)
    ip.append(infer_model.logp)
    iv.append(infer_model.get_node('B_a').value)
    #print ip[-1], iv[-1]
    #pdb.set_trace()

fig = plt.figure()
ax = fig.add_subplot(2,1,1)
ax.plot(ip)
ax.set_xlabel('iteration')
ax.set_ylabel('log probability')
ax.set_title('model log probability vs iteration #')
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
ax = fig.add_subplot(2,1,2)
ax.plot(iv)
ax.set_xlabel('iteration')
ax.set_ylabel('parameter value')
ax.set_title('parameter value vs iteration #')

fig.show()
print 'ASDF'
pdb.set_trace()
infer_model.sample(num_samples_for_inference)



B_a_vals = infer_model.trace(M.get_variable_name('B_a'))[:]
#B_b_vals = infer_model.trace(M.get_variable_name('B_b'))[:]
#B_c_vals = infer_model.trace(M.get_variable_name('B_c'))[:]

fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)


ax = fig.add_subplot(2,2,1)
ax.hist(B_a_vals, bins = 50)
ax.set_title(r'$B_a$')

"""
ax = fig.add_subplot(2,2,2)
ax.hist(B_b_vals, bins = 50)
ax.set_title(r'$B_b$')


ax = fig.add_subplot(2,2,3)
ax.hist(B_c_vals, bins = 50)
ax.set_title(r'$B_c$')
"""
fig.show()
fig.savefig('/Users/glareprotector/prostate_git/glare/bin/Bs.png')

fig=plt.figure()
ax=fig.add_subplot(111)
ax.plot(infer_model.trace('B_a')[:])
ax.set_xlabel('iteration number')
ax.set_ylabel('parameter value')
ax.set_title('parameter value trace')
plt.show()
print infer_model.logp

pdb.set_trace()



