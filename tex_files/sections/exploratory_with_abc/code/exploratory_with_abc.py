import get_model_new as get_model
import basic_features as bf
import pdb
import my_exceptions
import ucla_features as uf
import helper
import model_with_data_points
import numpy as np
from helper import get_branded_version as brand
import plot_helper
import os
import matplotlib.pyplot as plt


base_folder = '../files/'

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

regular_attributes = [attribute(brand(bf.always_raise,'age')(uf.ucla_feature(uf.ucla_feature.age)), 'age')]

                      
#######################################################################################################################################
# purpose: show that treatment affects the 4 parameters                                                                               #
# for each side effect, for each of 4 parameters, histogram of the parameter, stratified by treatment#
#######################################################################################################################################


if True:

    folder = base_folder + 'parameters_vs_treatment/'
    make_folder(folder)

    num_bins = 20

    for side_effect in side_effects:

        file_name = side_effect.name
        out_file = folder + file_name

        raw_series_getter = side_effect.raw_series_getter
        initial_f = bf.specific_time_value_panda_feature(raw_series_getter, 0)
        curve_getter = bf.retimed_raw_series(raw_series_getter, 1)
        abc_dict_f = bf.apply_return_as_dict_f(bf.get_abc_parameters_feature(curve_getter, initial_f, get_model.real_f))

        """
        set up figures/titles
        """
        fig = plt.figure()
        fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
        a_ax = fig.add_subplot(2,2,1)
        b_ax = fig.add_subplot(2,2,2)
        c_ax = fig.add_subplot(2,2,3)
        drop_ax = fig.add_subplot(2,2,4)

        a_ax.set_title('a')
        b_ax.set_title('b')
        c_ax.set_title('c')
        drop_ax.set_title('drop')

        a_labels = []
        b_labels = []
        c_labels = []
        drop_labels = []

        a_values = []
        b_values = []
        c_values = []
        drop_values = []
        weights = []


        for treatment in treatments:
            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_f)
            #treatment_iterator = ['10049']
            treatment_abc_dict = abc_dict_f(treatment_iterator)
            a_s = [abc[0] for pid, abc in treatment_abc_dict.iteritems()]
            b_s = [abc[1] for pid, abc in treatment_abc_dict.iteritems()]
            c_s = [abc[2] for pid, abc in treatment_abc_dict.iteritems()]
            drop_s = [a+(1-a)*b for a,b in zip(a_s,b_s)]
            
            a_values.append(a_s)
            b_values.append(b_s)
            c_values.append(c_s)
            drop_values.append(drop_s)

            a_labels.append(treatment.name + r' $\mu=$' + '%.2f'%np.mean(a_s))
            b_labels.append(treatment.name + r' $\mu=$' + '%.2f'%np.mean(b_s))
            c_labels.append(treatment.name + r' $\mu=$' + '%.2f'%np.mean(c_s))
            drop_labels.append(treatment.name + r' $\mu=$' + '%.2f'%np.mean(drop_s))
            weights.append(1.0)


        num_bins = 20

        pdb.set_trace()

        a_ax.hist(a_values, label = a_labels, normed=True, alpha=0.5, histtype='bar')
        b_ax.hist(b_values, label = b_labels, normed=True, alpha=0.5, histtype='bar')
        c_ax.hist(c_values, label = c_labels, normed=True, alpha=0.5, histtype='bar',bins=helper.seq(0,100,20))
        drop_ax.hist(drop_values, label = drop_labels, normed=True, alpha=0.5, histtype='bar')

        font_size = 6
        a_ax.legend(prop={'size':font_size})
        b_ax.legend(prop={'size':font_size})
        c_ax.legend(prop={'size':font_size})
        drop_ax.legend(prop={'size':font_size})

        fig.savefig(out_file)


###############################################################################################################
# purpose: side_effect, treatment, attribute, show trend between attribute and the 4 parameter values         #
# for each side_effect, treatment, attribute combination, make scatter of attribute vs 4 parameter values     #
###############################################################################################################

if True:

    folder = base_folder + 'attribute_vs_curve_parameters/'
    make_folder(folder)

    for side_effect in side_effects:
        brand(bf.always_raise,'age')
        initial_level_attribute = attribute(brand(bf.always_raise, 'initial_level')(bf.specific_time_value_panda_feature(side_effect.raw_series_getter,0)), 'initial_level')
        attributes = regular_attributes + [initial_level_attribute]
        raw_series_getter = side_effect.raw_series_getter
        initial_f = bf.specific_time_value_panda_feature(raw_series_getter, 0)
        curve_getter = bf.retimed_raw_series(raw_series_getter, 1)
        for treatment in treatments:
            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_f)
            for a_attribute in attributes:

                file_name = side_effect.name + '_' + treatment.name + '_' + a_attribute.name
                out_file = folder + file_name

                fig = plt.figure()
                fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
                fig.suptitle(side_effect.name + ' ' + treatment.name + ' ' + a_attribute.name)

                abc_data_dict_f = bf.apply_return_as_dict_f(bf.get_abc_data_feature([a_attribute.f], curve_getter, initial_f, get_model.real_f))
                abc_data_dict = abc_data_dict_f(treatment_iterator)

                x_s = [abc_data.cov.x[0] for pid,abc_data in abc_data_dict.iteritems()]
                a_s = [abc_data.a for pid,abc_data in abc_data_dict.iteritems()]
                b_s = [abc_data.b for pid,abc_data in abc_data_dict.iteritems()]
                c_s = [abc_data.c for pid,abc_data in abc_data_dict.iteritems()]
                drop_s = [a+(1-a)*b for a,b in zip(a_s,b_s)]

                a_ax = fig.add_subplot(2,2,1)
                b_ax = fig.add_subplot(2,2,2)
                c_ax = fig.add_subplot(2,2,3)
                drop_ax = fig.add_subplot(2,2,4)

                a_ax.scatter(x_s, a_s)
                b_ax.scatter(x_s, b_s)
                c_ax.scatter(x_s, c_s)
                drop_ax.scatter(x_s, drop_s)

                a_ax.set_xlabel(a_attribute.name)
                b_ax.set_xlabel(a_attribute.name)
                c_ax.set_xlabel(a_attribute.name)
                drop_ax.set_xlabel(a_attribute.name)

                a_ax.set_ylabel('a')
                b_ax.set_ylabel('b')
                c_ax.set_ylabel('c')
                drop_ax.set_ylabel('drop')

                plt.savefig(out_file)



