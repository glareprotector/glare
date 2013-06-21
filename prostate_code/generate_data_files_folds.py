"""
have function that takes in pid_iterator, feature_list, curve_getter_f, initial_level_f, and returns dictionary of pids to complete data objects.
functions will raise exceptions via post processing
this dictionary will then be used to write out covariate, curve files.  will normalize curve by initial value, so that don't need to pass initial level to R
"""

import get_model_new as get_model
import basic_features as bf
import pdb
import my_exceptions
import ucla_features as uf
import helper
import numpy as np
from helper import get_branded_version as brand
import plot_helper
import os
import matplotlib.pyplot as plt
import pandas
import functools
import cross_validate

from analyze_helper import *

experiment_folder = 'files_for_rstan/'
experiment_name = 'full_model_3_fold'
run_folder = experiment_folder + experiment_name + '/'






############################################################################
# define pid_iterators, different raw_series_getters, different attributes #
############################################################################

def raise_if_too_short(x, l):
    if len(x) < l:
        raise my_exceptions.NoFxnValueException
    return x

raise_len_f = functools.partial(raise_if_too_short, l=7)

all_iterable = bf.all_ucla_pid_iterable()

treatments = [treatment_brachytherapy, treatment_surgery, treatment_radiation]
side_effects = [side_effect_urinary_function, side_effect_bowel_function, side_effect_sexual_function]
regular_attribute_fs = [attribute_age]

num_folds = 3

                      
#######################################################################################################################################
# generate data files for each side_effect/treatment combo
#######################################################################################################################################


if True:


    for side_effect in side_effects:


        raw_series_getter = side_effect.raw_series_getter


        initial_f = brand(bf.always_raise, 'initial_level')(bf.specific_time_value_panda_feature(raw_series_getter,0))

        

        attribute_fs = regular_attribute_fs + [initial_f]

        curve_getter = bf.retimed_raw_series(raw_series_getter, 1)


        all_data_dict_f = bf.normalize_data_dict(bf.apply_return_as_dict_f(bf.get_all_data_feature(attribute_fs, curve_getter, initial_f, get_model.real_f)))
        
        for treatment in treatments:

            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_f)
            treatment_all_data_dict = all_data_dict_f(treatment_iterator)
            pdb.set_trace()
            for fold in cross_validate.k_fold_getter(num_folds, treatment_all_data_dict):
                
                fold_name = 'fold' + '_' + str(fold.i) + '_' + str(fold.k)
                folder = run_folder + side_effect.name + '/' + treatment.name + '/' + fold_name + '/'
                print folder
                train_folder = folder + 'train/'
                test_folder = folder + 'test/'
                import analyze_helper
                train_folder = analyze_helper.se_treatment_fold_to_training_folder(run_folder, side_effect, treatment, fold.i, fold.k)
                test_folder = analyze_helper.se_treatment_fold_to_testing_folder(run_folder, side_effect, treatment, fold.i, fold.k)

                write_x_datapoints_abcs(fold.train_data, train_folder)
                write_x_datapoints_abcs(fold.test_data, test_folder)
