import get_model_new as get_model
import numpy as np
import matplotlib.pyplot as plt
import pandas
import pdb

def get_model_manager(complete_datas, pids, mu_pop_a, mu_pop_b, mu_pop_c, B_a_init, B_b_init, B_c_init):

    """
    later on, these would all be features - 1 feature to get the part of the model that does not repeat
    """

    rho_observed = True


    M = get_model.variable_manager()




    num_attributes = len(iter(complete_datas.items()).next()[1].cov.x)
    assert len(B_a_init) == num_attributes
    M.set_num_attributes(num_attributes)

    M.constants.sigma_a_max = 100
    M.constants.mu_pop_a = mu_pop_a
    M.constants.l_a = 10.0

    M.set_variable_value('sigma_a', 100)
    M.set_variable_observed('sigma_a', True)

    M.set_variable_value('B_a', B_a_init)
    M.set_variable_observed('B_a', False)

    M.set_variable_value('rho_a', 0.01)
    M.set_variable_observed('rho_a', rho_observed)

    #M.set_pid_variable_value_blanket('a', mu_pop_a)
    M.set_pid_variable_observed_blanket('a', False)
    



    M.constants.sigma_b_max = 100
    M.constants.mu_pop_b = mu_pop_b
    M.constants.l_b = 10.0

    M.set_variable_value('sigma_b', 1)
    M.set_variable_observed('sigma_b', True)

    M.set_variable_value('B_b', B_b_init)
    M.set_variable_observed('B_b', False)

    M.set_variable_value('rho_b', 0.01)
    M.set_variable_observed('rho_b', rho_observed)

    #M.set_pid_variable_value_blanket('b', mu_pop_b)
    M.set_pid_variable_observed_blanket('b', False)



    M.constants.sigma_c_max = 100
    M.constants.mu_pop_c = mu_pop_c
    M.constants.l_c = 1.0

    M.set_variable_value('sigma_c', 1)
    M.set_variable_observed('sigma_c', True)

    M.set_variable_value('B_c', B_c_init)
    M.set_variable_observed('B_c', False)

    M.set_variable_value('rho_c', 0.2)
    M.set_variable_observed('rho_c',  rho_observed)

    #M.set_pid_variable_value_blanket('c', mu_pop_c)
    M.set_pid_variable_observed_blanket('c', False)


    M.set_variable_value('rho_noise', 0.3)
    M.set_variable_observed('rho_noise', False)
    M.constants.lambda_noise = 1.0



    ##################################
    # add in the observed data_points#
    # set a_i, b_i, c_i to MLE value #
    ##################################

    for pid, complete_data in complete_datas.items():

        the_cov = complete_data.cov
        M.set_pid_variable_value('x', pid, the_cov.x)
        M.set_pid_variable_value('s', pid, the_cov.s)
        M.set_pid_data_points(pid, complete_data.data_points)

        #M.set_pid_variable_value('a', pid, mu_pop_a)
        #M.set_pid_variable_value('b', pid, mu_pop_b)
        #M.set_pid_variable_value('c', pid, mu_pop_c)

        M.set_pid_variable_value('a', pid, get_model.g_mu_a(get_model.g_mu_a_inv(mu_pop_a) + M.get_variable_value('B_a').dot(the_cov.x)))
        M.set_pid_variable_value('b', pid, get_model.g_mu_b(get_model.g_mu_b_inv(mu_pop_b) + M.get_variable_value('B_b').dot(the_cov.x)))
        M.set_pid_variable_value('c', pid, get_model.g_mu_c(get_model.g_mu_c_inv(mu_pop_c) + M.get_variable_value('B_c').dot(the_cov.x)))

    M.constants.X_pop = pandas.Series([0 for x in range(num_attributes)])
    M.constants.X_pop.index = M.get_pid_variable_value('x', pid).index

    M.set_pid_data_observed_blanket(True)

    return M
