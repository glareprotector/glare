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


base_folder = 'files_for_rstan/'

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

def write_x_datapoints_abcs(d, base_folder):
    x_stuff_f = lambda v: v.cov.x
    x_df = helper.dict_of_series_to_dataframe(d, x_stuff_f)

    x_df.to_csv(base_folder + 'xs.csv')

    ss = [v.cov.s for k,v in d.iteritems()]
    pids = [k for k,v in d.iteritems()]
    ss_series = pandas.Series(ss,index=pids)
    ss_series.to_csv(base_folder + 'ss.csv')

    datapoints_folder = base_folder + 'datapoints/'
    make_folder(datapoints_folder)

    datapoints_f = lambda v: v.data_points
    datapoints_file_f = lambda k: datapoints_folder + k
    datapoints_write_f = lambda dp,f: dp.to_csv(f)
    helper.write_dict_stuff_by_folder(d, datapoints_f, datapoints_write_f, datapoints_file_f)
    
    """
    write as,bc,cs to file
    """
    as_d, bs_d, cs_d = {},{},{}

    for k,v in d.iteritems():
        as_d[k] = v.a
        bs_d[k] = v.b
        cs_d[k] = v.c

    a_series = pandas.Series(as_d)
    b_series = pandas.Series(bs_d)
    c_series = pandas.Series(cs_d)

    a_series.to_csv(base_folder + 'as.csv')
    b_series.to_csv(base_folder + 'bs.csv')
    c_series.to_csv(base_folder + 'cs.csv')

############################################################################
# define pid_iterators, different raw_series_getters, different attributes #
############################################################################

def raise_if_too_short(x, l):
    if len(x) < l:
        raise my_exceptions.NoFxnValueException
    return x

raise_len_f = functools.partial(raise_if_too_short, l=7)

all_iterable = bf.all_ucla_pid_iterable()

treatments = [treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.surgery), 'surgery'), \
                  treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.radiation), 'radiation'), \
                  treatment(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.brachy), 'brachytherapy')]

side_effects = [side_effect(bf.compose(raise_len_f,bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.urinary_function)), 'urinary_function'), \
                    side_effect(bf.compose(raise_len_f,bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.bowel_function)), 'bowel_function'), \
                    side_effect(bf.compose(raise_len_f,bf.ucla_raw_series_getter_panda(bf.ucla_raw_series_getter.sexual_function)), 'sexual_function')]

regular_attribute_fs = [brand(bf.always_raise,'age')(uf.ucla_feature(uf.ucla_feature.age))]

                      
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

            folder = base_folder + side_effect.name + '/' + treatment.name + '/'
            make_folder(folder)

            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_f)
            treatment_all_data_dict = all_data_dict_f(treatment_iterator)

            write_x_datapoints_abcs(treatment_all_data_dict, folder)
