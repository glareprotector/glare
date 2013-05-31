import get_model_new
import numpy as np
import matplotlib.pyplot as plt
import pandas
import pdb

def get_model_manager(abc_datas, pids, mu_pop_a, mu_pop_b, mu_pop_c):

    """
    later on, these would all be features - 1 feature to get the part of the model that does not repeat
    """

    rho_observed = True


    M = get_model_new.variable_manager()


    num_attributes = len(abc_datas[0].cov.x)
    M.set_num_attributes(num_attributes)

    M.constants.sigma_a_max = 100
    M.constants.mu_pop_a = mu_pop_a
    M.constants.l_a = 10.0

    M.set_variable_value('sigma_a', 100)
    M.set_variable_observed('sigma_a', True)

    M.set_variable_value('B_a', 1.0 * np.ones(num_attributes))
    M.set_variable_observed('B_a', False)

    M.set_variable_value('rho_a', 0.01)
    M.set_variable_observed('rho_a', rho_observed)

    M.set_pid_variable_observed_blanket('a', True)




    M.constants.sigma_b_max = 100
    M.constants.mu_pop_b = mu_pop_b
    M.constants.l_b = 10.0

    M.set_variable_value('sigma_b', 1)
    M.set_variable_observed('sigma_b', True)

    M.set_variable_value('B_b', 1.0 * np.ones(num_attributes))
    M.set_variable_observed('B_b', False)

    M.set_variable_value('rho_b', 0.01)
    M.set_variable_observed('rho_b', rho_observed)

    M.set_pid_variable_observed_blanket('b', True)



    M.constants.sigma_c_max = 100
    M.constants.mu_pop_c = mu_pop_c
    M.constants.l_c = 1.0

    M.set_variable_value('sigma_c', 1)
    M.set_variable_observed('sigma_c', True)

    M.set_variable_value('B_c', 1.0 * np.ones(num_attributes))
    M.set_variable_observed('B_c', False)

    M.set_variable_value('rho_c', 0.01)
    M.set_variable_observed('rho_c',  rho_observed)

    M.set_pid_variable_observed_blanket('c', True)


    M.set_variable_value('rho_noise', .1)
    M.set_variable_observed('rho_noise', False)
    M.constants.lambda_noise = 1.0

    M.constants.X_pop = pandas.Series([0 for x in range(num_attributes)])


    ############################
    # add in the observed abc's#
    ############################

    for abc_data, pid in zip(abc_datas, pids):
        the_cov = abc_data.cov
        a, b, c = abc_data.a, abc_data.b, abc_data.c
        M.set_pid_variable_value('x', pid, the_cov.x)
        M.set_pid_variable_value('s', pid, the_cov.s)
        M.set_pid_variable_value('a', pid, a)
        M.set_pid_variable_value('b', pid, b)
        M.set_pid_variable_value('c', pid, c)

    return M
