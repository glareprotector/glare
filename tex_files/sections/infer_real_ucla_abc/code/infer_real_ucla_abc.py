import get_model_new as get_model
import basic_features as bf
import pdb
import my_exceptions
import ucla_features as uf
import helper
import model_with_abc_data
import numpy as np
from helper import get_branded_version as brand
import plot_helper
import os
import matplotlib.pyplot as plt


base_folder = '../files/'

infer_steps = 500

#######################################################################################
# define useful data structures to keep track of treatments, side effects, attributes #
#######################################################################################

class treatment(object):
    def __init__(self, indicator_f, name):
        self.indicator_f, self.name = indicator_f, name

class side_effect(object):
    def __init__(self, raw_series_getter, name):
        self.raw_series_getter, self.name = raw_series_getter, name

class attribute(object):
    def __init__(self, f, name):
        self.f, self.name = f, name

def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

############################################################################
# define pid_iterators, different raw_series_getters, different attributes #
############################################################################

all_iterable = bf.all_ucla_pid_iterable()

treatments = [treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.surgery), 'surgery'), \
                  treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.radiation), 'radiation'), \
                  treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.brachy), 'brachytherapy')]

side_effects = [side_effect(bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.urinary_function), 'urinary_function'), \
                    side_effect(bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.bowel_function), 'bowel_function'), \
                    side_effect(bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.sexual_function), 'sexual_function')]

regular_attribute_fs = [brand(bf.always_raise,'age')(uf.ucla_feature(uf.ucla_feature.age))]

                      
#######################################################################################################################################
# purpose: show that treatment affects the 4 parameters                                                                               #
# for each side effect, for each of 4 parameters, histogram of the parameter, stratified by treatment#
#######################################################################################################################################


if True:


    for side_effect in side_effects:


        raw_series_getter = side_effect.raw_series_getter


        initial_f = brand(bf.always_raise, 'initial_level')(bf.specific_time_value_panda_feature(raw_series_getter,0))

        

        attribute_fs = regular_attribute_fs + [initial_f]

        curve_getter = bf.retimed_raw_series(raw_series_getter, 1)


        abc_data_dict_f = bf.normalize_data_dict(bf.apply_return_as_dict_f(bf.get_abc_data_feature(attribute_fs, curve_getter, initial_f, get_model.real_f)))



        for treatment in treatments:

            folder = base_folder + side_effect.name + '/' + treatment.name + '/'
            make_folder(folder)

            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_f)
            treatment_abc_data_dict = abc_data_dict_f(treatment_iterator)

            """
            get mu_pop_a, mu_pop_b, mu_pop_c
            """
            a_s = [abc_data.a for pid,abc_data in treatment_abc_data_dict.iteritems()]
            b_s = [abc_data.b for pid,abc_data in treatment_abc_data_dict.iteritems()]
            c_s = [abc_data.c for pid,abc_data in treatment_abc_data_dict.iteritems()]



            mu_pop_a = np.mean(a_s)
            mu_pop_b = np.mean(b_s)
            mu_pop_c = np.mean(c_s)

            pids = treatment_abc_data_dict.keys()

            infer_manager = model_with_abc_data.get_model_manager(treatment_abc_data_dict, pids, mu_pop_a, mu_pop_b, mu_pop_c)

            infer_model = get_model.get_model_using_variable_manager(infer_manager)
            map_model = get_model.get_model_using_variable_manager(infer_manager, 'MAP')
            map_model.fit()
            for var in map_model.stochastics:
                print var.__name__, var.value
                infer_model.get_node(var.__name__).value = var.value
            infer_model.sample(infer_steps)

            if True:

                Bs_trace_file = folder + 'Bs_trace.png'
                plot_helper.plot_Bs_trace(Bs_trace_file, infer_model)

            if True:

                Bs_hist_file = folder + 'Bs_hist.png'
                plot_helper.plot_Bs_histogram(Bs_hist_file, infer_model)

            if True:
                logp_file = folder + 'logp_trace.png'
                plot_helper.plot_logp_trace(logp_file, infer_model)
            
            pdb.set_trace()
