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
from my_data_types import sv_int, sv_float

import matplotlib.pyplot as plt


p = global_stuff.get_param()

A = set(wc.get_stuff(objects.PID_with_SS_info, p))
AA = set(wc.get_stuff(objects.prostate_PID,p))
#AAA = AA - A
AAA = AA
B = set(wc.get_stuff(objects.PID_with_shared_MRN, p))
C = set(wc.get_stuff(objects.PID_with_multiple_tumors, p))
PID_to_use = list(AAA - B - C)



the_data_set = helper.data_set(PID_to_use)
treated_data_set = the_data_set.filter(lambda x: f.treatment_code_f().generate(x) in [1,2])
interval_boundaries = [0,0.5,1,2.0]
intervals = [my_data_types.ordered_interval(helper.my_timedelta(interval_boundaries[i]*365), helper.my_timedelta(interval_boundaries[i+1]*365)) for i in range(len(interval_boundaries)-1)]
interval_strings = ['0-6 months','6-12 months','1-2 years']




# cycle thru side effects, before have/(havenot), attributes, treatment, time period
# so each plot will have num time periods x 2 plots - hist and cumulative

side_effect_instances = [side_effects.erection_side_effect(), side_effects.urin_incont_bin(), side_effects.urinary_frequency_bin(), side_effects.diarrhea_bin()]  
side_effect_strings = ['ED','urin_incont','urin_freq','diarrhea']

attribute_fs = [lambda x: f.psa_value_f().generate(x), \
                    lambda x: f.BMI_f().generate(x), \
                    lambda x: f.age_at_diagnosis_f().generate(x)]
attribute_f_strings = ['psa','BMI','age']
attribute_maxes = [200,50,100]
attribute_bin_sizes = [25,25,25]


treatment_fs = [lambda x: f.treatment_code_f().generate(x) == 1,\
                    lambda x: f.treatment_code_f().generate(x) == 2, \
                    lambda x: True]
treatment_f_strings = ['SURG', 'RAD', 'ALLTRT']

path = 'hist_plots/'




for side_effect_instance, side_effect_string in zip(side_effect_instances, side_effect_strings):
    for attribute_f, attribute_f_string, attribute_max, attribute_bin_size in zip(attribute_fs, attribute_f_strings, attribute_maxes, attribute_bin_sizes):
        for treatment_f, treatment_f_string in zip(treatment_fs, treatment_f_strings):
            pre_treatment_fs = [lambda x: True,\
                                    lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance).get_value() == sv_int(1), \
                                    lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance).get_value() == sv_int(0)]
            pre_treatment_f_strings = ['pre_all','pre_good','pre_bad']
            for pre_treatment_f, pre_treatment_f_string in zip(pre_treatment_fs, pre_treatment_f_strings):
                fig = plt.figure()
                import string
                title = string.join([side_effect_string, attribute_f_string, treatment_f_string, pre_treatment_f_string],sep='-')
                fig.suptitle(title)
                for interval, interval_string, row_num in zip(intervals, interval_strings, range(len(intervals))):
                    try:
                        data_one_f = lambda x: treatment_f(x) and pre_treatment_f(x) and bf.side_effect_interval_value_f().generate(x, side_effect_instance, 'treatment', interval) == 1
                        data_zero_f = lambda x: treatment_f(x) and pre_treatment_f(x) and bf.side_effect_interval_value_f().generate(x, side_effect_instance, 'treatment', interval) == 0
                        one_data = treated_data_set.filter(data_one_f)
                        zero_data = treated_data_set.filter(data_zero_f)

                        one_attributes = one_data.apply_feature(attribute_f)
                        zero_attributes = zero_data.apply_feature(attribute_f)

                        ax_reg = fig.add_subplot(len(intervals), 2, 2 * row_num + 1)
                        ax_reg.hist(one_attributes, color = 'g', label = side_effect_string + '_good('+str(len(one_attributes))+')', alpha = 0.5, histtype='step', linewidth=3.8, ls='dashed', range=(0,attribute_max), bins=attribute_bin_size, normed=True)
                        ax_reg.hist(zero_attributes, color = 'r', label = side_effect_string + '_bad('+str(len(one_attributes))+')', alpha = 0.5, histtype='step', linewidth=2.5, range=(0,attribute_max), bins=attribute_bin_size, normed=True)

                        ax_reg.set_ylabel(interval_string)

                        ax_reg_cum = fig.add_subplot(len(intervals), 2, 2 * row_num+2)
                        ax_reg_cum.hist(one_attributes, color = 'g', label = side_effect_string + '_good('+str(len(one_attributes))+')', cumulative=True, alpha = 0.6, linewidth=2.0, range=(0,attribute_max), bins=1000, histtype='step', normed=True)
                        ax_reg_cum.hist(zero_attributes, color = 'r', label = side_effect_string + '_bad('+str(len(one_attributes))+')', cumulative=True, alpha = 0.6, linewidth=2.0, range=(0,attribute_max), bins=1000, histtype='step', normed=True)

                        ax_reg_cum.yaxis.set_label_position('right')
                        ax_reg_cum.set_ylabel('YES: '+str(len(one_attributes)) + ' ' + 'NO: '+str(len(zero_attributes)), fontsize=9)
                    except:
                        pass



                plt.savefig(path+title+'.png')



side_effect_instance = side_effects.urin_incont_bin()
attribute_f = lambda x: f.psa_value_f().generate(x)


fig = plt.figure()

ax = fig.add_subplot(1,1,1)


data_zero = treated_data_set.filter(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0)
data_one = treated_data_set.filter(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1)



# get attributes of dataset
zero_attributes = data_zero.apply_feature(attribute_f) 
one_attributes = data_one.apply_feature(attribute_f)

zero_hist = ax.hist(zero_attributes, color = 'r', label = 'zero', alpha = 0.5, normed=True, range=(0,300), cumulative=False, histtype='step', bins = 60)
one_hist = ax.hist(one_attributes, color = 'c', label = 'one', alpha = 0.5, normed=True, range=(0,300), cumulative=False, histtype='step', bins = 60)

plt.legend()

plt.savefig('test_hist.png')
