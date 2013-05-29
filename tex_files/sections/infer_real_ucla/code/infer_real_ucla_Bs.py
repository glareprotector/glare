import get_model_new as get_model
import basic_features as bf
import pdb
import my_exceptions
import ucla_features as uf
import helper
import model_with_data_points
import numpy as np

import plot_helper

mu_pop_a = 0.5
mu_pop_b = 0.5
mu_pop_c = 2.0
B_a_init = np.array([0.0])
B_b_init = np.array([0.0])
B_c_init = np.array([0.0])

raw_series_getter = bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter_panda.sexual_function)
#pid_iterable = bf.all_ucla_pid_iterable()

treatment_indicator_f = bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.surgery)
pid_iterable = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment_indicator_f)

retimed_series_f = bf.retimed_raw_series(raw_series_getter, 1)




initial_level_f = bf.specific_time_value_panda_feature(raw_series_getter, 0)
attribute_fs = [initial_level_f]



abc_f = bf.get_abc_parameters_feature(retimed_series_f, initial_level_f, get_model.real_f)


for pid in pid_iterable:
    print raw_series_getter(pid)
    print abc_f(pid)
    pdb.set_trace()


data = {}

def get_complete_data(attribute_fs, initial_level_f, series_getter_f, pid):

    """
    for the specified pid, returns a complete_data
    """
    initial_level = initial_level_f(pid)
    x = bf.patient_features_feature(attribute_fs)(pid)
    series = series_getter_f(pid)
    the_cov = helper.cov(x, initial_level)
    return helper.complete_data(the_cov, series)


count = 1
for pid in pid_iterable:
    count += 1
    print count
    #print pid
    try:
        data[pid] = get_complete_data(attribute_fs, initial_level_f, retimed_series_f, pid)
    except my_exceptions.NoFxnValueException:
        pass

infer_manager = model_with_data_points.get_model_manager(data, pid_iterable, mu_pop_a, mu_pop_b, mu_pop_c, B_a_init, B_b_init, B_c_init)
infer_model = get_model.get_model_using_variable_manager(infer_manager, 'MCMC')



if False:

    infer_model_map = get_model.get_model_using_variable_manager(infer_manager, 'MAP')
    infer_model_map.fit(verbose=10)
    max_a, max_b = infer_model_map.get_node('B_a').value, infer_model_map.get_node('B_b').value
    print 'MLE values for B_a and B_b: ', max_a, max_b
    print 'MLE likelihood: ', infer_model_map.logp








infer_model.sample(500)

if True:

    plot_helper.plot_Bs_trace('../files/test_Bs_trace.png', infer_model)

pdb.set_trace()
