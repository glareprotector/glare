import wc
import param
import objects
import helper
import pdb
import features as f
import basic_features as bf
import side_effects
import datetime
import my_data_types
import pickle
import get_info
import global_stuff
import plotters
import numpy
import my_exceptions
import aggregate_features as af
from global_stuff import get_tumor_cls
import helper
import ucla_objects

import matplotlib.pyplot as plt



time_in_months = [0,1,2,4,8,12,18,24,30,36,42,48]
time_in_days = [30*x for x in time_in_months]

intervals = [my_data_types.exact_time(time=helper.my_timedelta(days=days)) for days in time_in_days]



pid_to_use = wc.get_stuff(ucla_objects.UCLA_patient_list, param.param())
pdb.set_trace()

side_effect_instance = side_effects.ucla_side_effect(4, global_stuff.ucla_file, 'urinfunc')
mean_series = bf.aggregate_side_effect_intervals_values_f()(pid_to_use, side_effect_instance, 'treatment', intervals, 'dummy', af.get_bucket_mean_feature(), 'ucla')
print mean_series
