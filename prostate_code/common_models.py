import get_model_new
import numpy as np
import matplotlib.pyplot as plt
import pandas
import pdb

M = get_model_new.variable_manager()

"""
this model has B's fixed, and has no data points
variables of model:
sigma_a B_a mu_a_i rho_a a
constants: sigma_a_max mu_pop_a
"""

################
# set up model #
################

num_data = 30
num_samples_for_inference = 20000
num_attributes = 1


M.constants.sigma_a_max = 100
M.constants.mu_pop_a = 0.7
M.constants.l_a = 10.0

M.set_variable_value('sigma_a', 10)
M.set_variable_observed('sigma_a', True)

M.set_variable_value('B_a', 1.0 * np.ones(num_attributes))
M.set_variable_observed('B_a', True)

M.set_variable_value('rho_a', 0.01)
M.set_variable_observed('rho_a', False)

M.set_pid_variable_value_blanket('a', 0.5)
M.set_pid_variable_observed_blanket('a', False)




M.constants.sigma_b_max = 100
M.constants.mu_pop_b = 0.7
M.constants.l_b = 10.0

M.set_variable_value('sigma_b', 1)
M.set_variable_observed('sigma_b', True)

M.set_variable_value('B_b', 1.0 * np.ones(num_attributes))
M.set_variable_observed('B_b', True)

M.set_variable_value('rho_b', 0.01)
M.set_variable_observed('rho_b', False)

M.set_pid_variable_value_blanket('b', 0.5)
M.set_pid_variable_observed_blanket('b', False)



M.constants.sigma_c_max = 100
M.constants.mu_pop_c = 2.0
M.constants.l_c = 1.0

M.set_variable_value('sigma_c', 1)
M.set_variable_observed('sigma_c', True)

M.set_variable_value('B_c', 1.0 * np.ones(num_attributes))
M.set_variable_observed('B_c', True)

M.set_variable_value('rho_c', 0.01)
M.set_variable_observed('rho_c', False)

M.set_pid_variable_value_blanket('c', 2.0)
M.set_pid_variable_observed_blanket('c', False)


M.set_variable_value('rho_noise', 0.001)
M.set_variable_observed('rho_noise', True)
M.constants.lambda_noise = 1.0


M.constants.X_pop = pandas.Series([0 for x in range(num_attributes)])


