import get_model_new as get_model
import numpy as np
import pandas

def get_model_manager(cov, b_a, b_b, b_c, the_pid, mu_pop_a, mu_pop_b, mu_pop_c):
    """
    creates prior model with 1 sample, no function data_points.  pid of that single sample is specified.  attribute of the sample is assumed to be a numpy array
    covariates of model (x,s) are stored as variable called cov
    Bs are specified.
    """

    M = get_model.variable_manager()


    num_attributes = len(cov.x)
    M.set_num_attributes(num_attributes)

    M.constants.sigma_a_max = 100
    M.constants.mu_pop_a = mu_pop_a
    M.constants.l_a = 10.0

    M.set_variable_value('sigma_a', 100)
    M.set_variable_observed('sigma_a', True)

    M.set_variable_value('B_a', b_a * np.ones(num_attributes))
    M.set_variable_observed('B_a', True)

    M.set_variable_value('rho_a', 0.01)
    M.set_variable_observed('rho_a', False)

    M.set_pid_variable_value_blanket('a', 0.9)
    M.set_pid_variable_observed_blanket('a', False)




    M.constants.sigma_b_max = 100
    M.constants.mu_pop_b = mu_pop_b
    M.constants.l_b = 10.0

    M.set_variable_value('sigma_b', 1)
    M.set_variable_observed('sigma_b', True)

    M.set_variable_value('B_b', b_b * np.ones(num_attributes))
    M.set_variable_observed('B_b', True)

    M.set_variable_value('rho_b', 0.01)
    M.set_variable_observed('rho_b', False)

    M.set_pid_variable_value_blanket('b', 0.5)
    M.set_pid_variable_observed_blanket('b', False)



    M.constants.sigma_c_max = 100
    M.constants.mu_pop_c = mu_pop_c
    M.constants.l_c = 1.0

    M.set_variable_value('sigma_c', 1)
    M.set_variable_observed('sigma_c', True)

    M.set_variable_value('B_c', b_c * np.ones(num_attributes))
    M.set_variable_observed('B_c', True)

    M.set_variable_value('rho_c', 0.01)
    M.set_variable_observed('rho_c', False)

    M.set_pid_variable_value_blanket('c', 2.0)
    M.set_pid_variable_observed_blanket('c', False)


    M.set_variable_value('rho_noise', .01)
    M.set_variable_observed('rho_noise', False)
    M.constants.lambda_noise = 1.0


    M.constants.X_pop = pandas.Series([0 for x in range(num_attributes)])



    M.set_pid_variable_value('x', the_pid, cov.x)
    M.set_pid_variable_value('s', the_pid, cov.s)


    return M
