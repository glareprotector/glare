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
from global_stuff import get_tumor_cls

import matplotlib.pyplot as plt


p = global_stuff.get_param()

A = set(wc.get_stuff(objects.PID_with_SS_info, p))
B = set(wc.get_stuff(objects.PID_with_shared_MRN, p))
C = set(wc.get_stuff(objects.PID_with_multiple_tumors, p))
PID_to_use = list(A - B - C)
test_PID_to_use = PID_to_use


the_data_set = helper.data_set.data_set_from_pid_list(test_PID_to_use, p)
treated_data_set = the_data_set.filter(lambda x: f.treatment_code_f().generate(x) in [1,2])
interval_boundaries = [0,0.5,1,2,5]
intervals = [my_data_types.ordered_interval(helper.my_timedelta(interval_boundaries[i]*365), helper.my_timedelta(interval_boundaries[i+1]*365)) for i in range(len(interval_boundaries)-1)]




feature_list = [f.treatment_code_f(), f.age_at_diagnosis_f(), f.age_at_LC_f(), f.vital_status_f(), f.age_at_LC_f(), f.follow_up_time_f(), f.grade_f(), f.SEERStage_mine_f(), f.pre_treatment_side_effect_label_f(side_effects.urin_incont_bin()), bf.two_year_erection_f(), bf.five_year_erection_f()]

feature_string = the_data_set.get_csv_string(feature_list)
print feature_string

f = open('test_features.csv', 'w')
f.write(feature_string)
