import get_model_new
import numpy as np
import matplotlib.pyplot as plt
import pandas
import pdb

import common_models

M = common_models.M

num_data = 10
num_samples_for_inference = 20000

############################################
# store the samples in temp data structure #
############################################




pidxabc_records = []
for i in range(num_data):
    s = 1.0
    x =pandas.Series([np.random.normal(0,1)])
    a,b,c = get_model_new.get_abc_given_xs(M, x, s, 50)
    pidxabc_records.append([i,x,s,a,b,c])



for record in pidxabc_records:
    pid, x, s, a, b, c = record
    pid = str(pid)

    M.set_pid_x(pid, x)
    M.set_pid_variable_value('s', pid, s)
    M.set_pid_variable_value('a', pid, a)
    M.set_pid_variable_value('b', pid, b)
    M.set_pid_variable_value('c', pid, c)


print pidxabc_records

###########################
# plot the simulated data #
###########################

x_vals = [temp[1] for temp in pidxabc_records]
a_vals = [temp[3] for temp in pidxabc_records]
b_vals = [temp[4] for temp in pidxabc_records]
c_vals = [temp[5] for temp in pidxabc_records]



fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

ax = fig.add_subplot(2,2,1)
ax.scatter(x_vals, a_vals)
ax.set_xlabel('value of the single covariate x')
ax.set_ylabel('value of a')
ax.set_title('a')

ax = fig.add_subplot(2,2,2)
ax.scatter(x_vals, b_vals)
ax.set_xlabel('value of the single covariate x')
ax.set_ylabel('value of b')
ax.set_title('b')

ax = fig.add_subplot(2,2,3)
ax.scatter(x_vals, c_vals)
ax.set_xlabel('value of the single covariate x')
ax.set_ylabel('value of c')
ax.set_title('c')

fig.show()
fig.savefig('/Users/glareprotector/prostate_git/glare/bin/abc_vs_covariates.png')


######################################################################
# make new model where B's are no longer fixed and the data is added #
######################################################################

M.set_variable_observed('B_a', False)
M.set_variable_observed('B_b', False)
M.set_variable_observed('B_c', False)

M.set_pid_variable_observed_blanket('a', True)
M.set_pid_variable_observed_blanket('b', True)
M.set_pid_variable_observed_blanket('c', True)

pdb.set_trace()
infer_model = get_model_new.get_model_using_variable_manager(M)

pdb.set_trace()

##################################################################################
# do inference with new model to get/plot posterior distribution of B_a, B_b, B_c#
##################################################################################


infer_model.sample(num_samples_for_inference)



B_a_vals = infer_model.trace(M.get_variable_name('B_a'))[:]
B_b_vals = infer_model.trace(M.get_variable_name('B_b'))[:]
B_c_vals = infer_model.trace(M.get_variable_name('B_c'))[:]

fig = plt.figure()
fig.subplots_adjust(hspace = 0.4, wspace = 0.25)


ax = fig.add_subplot(2,2,1)
ax.hist(B_a_vals, bins = 50)
ax.set_title(r'$B_a$')


ax = fig.add_subplot(2,2,2)
ax.hist(B_b_vals, bins = 50)
ax.set_title(r'$B_b$')


ax = fig.add_subplot(2,2,3)
ax.hist(B_c_vals, bins = 50)
ax.set_title(r'$B_c$')

fig.show()
fig.savefig('/Users/glareprotector/prostate_git/glare/bin/Bs.png')

pdb.set_trace()