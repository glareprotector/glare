import sys
sys.path.insert(0,'/Library/Python/2.7/site-packages')

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
from helper import get_branded_version as brand
import helper
import ucla_objects, ucla_features as uf
import matplotlib.pyplot as plt
import os
import pandas

###################################################
# some initialization procedures that must be run #
###################################################
pandas.Series.plot = my_data_types.plot
pandas.Series.plot_hist = my_data_types.plot_hist
pandas.Series.plot_best_fit = my_data_types.plot_best_fit



########################################
# some basic helper fxns and containers#
########################################

def get_file_name(save_path, title):
    return save_path + '/' + title + '.png'

def set_tick_label_size(axis, size):
    for tick in axis.get_major_ticks():
        tick.label.set_fontsize(8)

def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

class se_info(object):
    def __init__(self, se_series_getter, color, name, idx, zero_split):
        self.se_series_getter, self.color, self.name, self.idx, self.zero_split = se_series_getter, color, name, idx, zero_split

class treatment_info(object):
    def __init__(self, indicator_feature, color, name, idx):
        self.indicator_feature, self.color, self.name, self.idx = indicator_feature, color, name, idx

class attribute_info(object):
    def __init__(self, attribute_f, bin_specifier, split_val, color, name, idx, valid_range):
        self.attribute_f, self.bin_specifier, self.split_val, self.color, self.name, self.idx, self.valid_range = attribute_f, bin_specifier, split_val, color, name, idx, valid_range


###########################################
# some variables that are used across plot#
###########################################

base_path = 'ucla_plots/'

treatments = [treatment_info(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.surgery), 'r', 'surgery', 0), \
                  treatment_info(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.radiation), 'g', 'radiation', 1), \
                  treatment_info(bf.indicator_feature(uf.ucla_treatment_code_f(), uf.ucla_treatment_code_f.brachy), 'b', 'brachy', 2)]

side_effects = [se_info(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.physical_condition), 'b', 'physical_condition', 0, 57), \
                    se_info(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.mental_condition), 'g', 'mental_condition', 1, 52), \
                    se_info(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.urinary_function), 'r', 'urin_func', 2, 89), \
                    se_info(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.bowel_function), 'c', 'bowel_func', 3, 88), \
                    se_info(bf.ucla_raw_series_getter(bf.ucla_raw_series_getter.sexual_function), 'm', 'sexual_func', 4, 61)]

attributes = [attribute_info(brand(bf.always_raise,'age')(uf.ucla_feature(uf.ucla_feature.age)), bf.int_bin_specifier_feature(), 70, 'b', 'age', 0, (0,100)), \
                  attribute_info(brand(bf.always_raise,'gleason')(uf.ucla_feature(uf.ucla_feature.gleason)), bf.int_bin_specifier_feature(), 6, 'g', 'gleason', 1, (2,12)), \
                  attribute_info(brand(bf.always_raise,'stage')(uf.ucla_feature(uf.ucla_feature.stage)), bf.int_bin_specifier_feature(), 2, 'r', 'stage', 2, (0,10)), \
                  attribute_info(brand(bf.always_raise,'psa')(uf.ucla_feature(uf.ucla_feature.psa)), bf.int_bin_specifier_feature(max_val=50), 8, 'c', 'psa', 3, (-1,15)), \
                  attribute_info(brand(bf.always_raise,'comorbidity')(uf.ucla_feature(uf.ucla_feature.comorbidity_count)), bf.int_bin_specifier_feature(), 1, 'm', 'comorbidity', 4, (-1,6)), \
                  attribute_info(brand(bf.always_raise,'black')(uf.black_or_not()), bf.int_bin_specifier_feature(), 0.5, 'k', 'black', 5, (-1,2))]

times = [helper.my_timedelta(days=days*30) for days in [0,1,2,4,8,12,18,24,30,36,42,48]]





########################################################################################################
# generate dataframe whose columns are the attributes as well as the side effect values at time 1 month#
# then for each side effect, do cross validation and print results                                     #
########################################################################################################

if False:
    import sklearn.linear_model
    import sklearn.cross_validation
    import sklearn.metrics
    attribute_fs = [attribute.attribute_f for attribute in attributes]
    side_effect_fs = [brand(bf.single_time_processed_time_series,side_effect.name)(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=1*30)) for side_effect in side_effects]
    df = bf.data_frame_feature()(bf.all_ucla_pid_iterable(), attribute_fs + side_effect_fs)
    attributes_df = df.loc[:,[attribute.name for attribute in attributes]]
    for side_effect in side_effects:
        print side_effect.name
        temp = attributes_df
        temp[side_effect.name] = df[side_effect.name]
        temp = temp.dropna(axis=0)
        print bf.run_CV()(sklearn.linear_model.LinearRegression(), temp.loc[:,[attribute.name for attribute in attributes]], temp[side_effect.name], sklearn.cross_validation.KFold(temp.shape[0], n_folds=5), sklearn.metrics.mean_absolute_error)

    











################################################################################################################################
# for each side effect, for each treatment, plot side effect value at month 0 and 1 to see correlation between before and after#
################################################################################################################################

if False:

    plt_string = 'before_vs_after'

    save_path = base_path + plt_string
    make_folder(save_path)

    for side_effect in side_effects:
        fig = plt.figure()
        description = side_effect.name
        title = plt_string + ' ' + description
        fig.suptitle(title)
        num_treatments = len(treatments)
        for treatment in treatments:
            x_feature = bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=0*30))
            y_feature = bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=1*30))
            tuple_feature = bf.cross_feature(x_feature, y_feature)
            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_feature)
            tuples = bf.feature_applier(tuple_feature)(treatment_iterator)
            ax = fig.add_subplot(2, 2, treatment.idx+1)
            tuples.plot_best_fit(ax,color = side_effect.color, linestyle='-', lw=2, alpha=0.4)
            tuples.plot(ax, color = side_effect.color)
            ax.set_title(treatment.name)
            ax.set_xlim([0,100])
            ax.set_ylim([0,100])
        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name



# combine side effects onto 1 page
###################################################################
# for each side effect, plot the average time series over all time#
###################################################################

if False:

    plt_string = 'all_patients_avg_time_series'
    
    save_path = base_path + plt_string
    make_folder(save_path)

    for side_effect in side_effects:
        series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(bf.all_ucla_pid_iterable(), times)
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        description = side_effect.name
        title = plt_string + ' ' + description
        ax.set_title(title)
        ax.set_xlim([-.5,4])
        ax.set_ylim([0,100])
        ax.legend()
        series.plot(ax, color='r', label='all')
        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name




########################################################################################
# for each side effect, plot average time series over all time, stratified by treatment#
########################################################################################

if False:

    plt_string = 'avg_time_series_by_treatment'

    save_path = base_path + plt_string
    make_folder(save_path)

    for side_effect in side_effects:
        fig = plt.figure()
        description = side_effect.name
        title = plt_string + ' ' + description
        fig.suptitle(title)
        for treatment in treatments:
            ax = fig.add_subplot(len(treatments), 1, treatment.idx+1)
            ax.set_xlim([-.5,4])
            ax.set_ylim([0,100]) 
            treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_feature)
            series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(treatment_iterator, times)
            series.plot(ax, color=treatment.color, label=treatment.name)
            ax.legend()
        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name

#combine by side effect
###################################
# plot histogram of each attribute#
###################################

if False:

    plt_string = 'attribute_histograms'

    save_path = base_path + plt_string
    make_folder(save_path)

    for attribute in attributes:
        fig = plt.figure()
        description = attribute.name
        title = plt_string + ' ' + description
        fig.suptitle(title)
        ax = fig.add_subplot(1,1,1)
        attribute_vals = bf.feature_applier(attribute.attribute_f)(bf.all_ucla_pid_iterable())
        attribute_vals.plot_hist(ax, attribute.bin_specifier, alpha = 0.5, histtype='bar', linewidth=1.8, color = attribute.color)
        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name


############################################################################
# plot time series by side_effect.  stratify by pre-treatment feature value#
############################################################################

if False:

    plt_string = 'avg_time_series_strat_by_pre_state'

    save_path = base_path + plt_string
    make_folder(save_path)

    for side_effect in side_effects:
        fig = plt.figure()
        description = side_effect.name
        title = plt_string + ' ' + description
        fig.suptitle(title)
        ax = fig.add_subplot(1,1,1)
        ax.set_xlim([-.5,4])
        ax.set_ylim([0,100]) 
        low_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), bf.range_indicator_feature(bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=0*30)), low=0, high = side_effect.zero_split))
        low_series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(low_iterator, times)
        low_series.plot(ax, color = side_effect.color, label = side_effect.name)
        high_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), bf.range_indicator_feature(bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=0*30)), low = side_effect.zero_split, high=100))
        high_series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(high_iterator, times)
        high_series.plot(ax, color = side_effect.color, label = side_effect.name)
        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name


##########################################################
# plot time series by side_effect.  stratify by attribute#
##########################################################

if False:

    plt_string = 'avg_time_series_strat_by_attribute'

    save_path = base_path + plt_string
    make_folder(save_path)

    for side_effect in side_effects:
        fig = plt.figure()
        description = side_effect.name
        title = plt_string + ' ' + description
        fig.suptitle(title)
        for attribute in attributes:
            ax = fig.add_subplot(2,3,attribute.idx+1)
            ax.set_xlim([-.5,4])
            ax.set_ylim([0,100]) 
            ax.set_title(attribute.name)
            set_tick_label_size(ax.xaxis,9)
            set_tick_label_size(ax.yaxis,9)

            low_feature = bf.range_indicator_feature(attribute.attribute_f, low = -1, high = attribute.split_val)
            low_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), low_feature)
            low_series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(low_iterator, times)
            low_series.plot(ax, color = 'g', label = attribute.name)
            
            high_feature = bf.range_indicator_feature(attribute.attribute_f, low = attribute.split_val, high = 1000)
            high_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), high_feature)
            high_series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(high_iterator, times)
            high_series.plot(ax, color = 'r', label = attribute.name)


        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name



##########################################
# plot side effect pre-state vs attribute#
##########################################


if False:

    plt_string = 'pre_state_vs_attribute'

    save_path = base_path + plt_string
    make_folder(save_path)

    for side_effect in side_effects:
        fig = plt.figure()
        description = side_effect.name
        title = plt_string + ' ' + description
        fig.suptitle(title)
        for attribute in attributes:
            ax = fig.add_subplot(2,3,attribute.idx+1)
            #ax.set_title(attribute.name, fontsize=9)
            ax.set_xlabel(attribute.name, fontsize=9)
            #ax.set_ylabel(attribute.name, fontsize=9)
            ax.text(0, 0.5, side_effect.name + ' pre-treatment', rotation='vertical',fontsize=9, transform = ax.transAxes, va='center', ha='left')
            set_tick_label_size(ax.xaxis,9)
            set_tick_label_size(ax.yaxis,9)
        
            before_feature = bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=0*30))
            attribute_feature = attribute.attribute_f

            tuple_feature = bf.cross_feature(attribute_feature, before_feature)

            
            tuples = bf.feature_applier(tuple_feature)(uf.all_ucla_pid_iterable())
            tuples.plot(ax, color = attribute.color)
            tuples.plot_best_fit(ax, color = attribute.color, linestyle='-', lw=2, alpha = 0.4)

        file_name = get_file_name(save_path, description)
        plt.savefig(file_name)
        print file_name


############################################################################
# for each treatment, plot time series by side effect stratify by attribute#
############################################################################

if False:

    plt_string = 'avg_time_series_by_treatment_strat_by_attribute'

    save_path = base_path + plt_string
    make_folder(save_path)

    for treatment in treatments:
        treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_feature)
        for side_effect in side_effects:
            fig = plt.figure()
            description = side_effect.name + '_' + treatment.name
            title = plt_string + ' ' + description
            fig.suptitle(title)
            for attribute in attributes:
                ax = fig.add_subplot(2,3,attribute.idx+1)
                ax.set_xlim([-.5,4])
                ax.set_ylim([0,100]) 
                ax.set_title(attribute.name)
                set_tick_label_size(ax.xaxis,9)
                set_tick_label_size(ax.yaxis,9)

                treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_feature)            

                low_feature = bf.range_indicator_feature(attribute.attribute_f, low = -1, high = attribute.split_val)
                low_iterator = bf.filtered_pid_iterable(treatment_iterator, low_feature)
                low_series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(low_iterator, times)
                low_series.plot(ax, color = 'g', label = attribute.name)
            
                high_feature = bf.range_indicator_feature(attribute.attribute_f, low = attribute.split_val, high = 1000)
                high_iterator = bf.filtered_pid_iterable(treatment_iterator, high_feature)
                high_series = helper.cast_result(bf.aggregate_processed_series_getter(bf.processed_exact_time_series_getter(side_effect.se_series_getter), af.get_uncertainty_point_feature()), my_data_types.timed_uncertainty_list)(high_iterator, times)
                high_series.plot(ax, color = 'r', label = attribute.name)


            file_name = get_file_name(save_path, description)
            plt.savefig(file_name)
            print file_name



##############################################################
# for each treatment, plot side effect pre-state vs attribute#
##############################################################


if False:

    plt_string = 'pre_state_vs_attribute_by_treatment'

    save_path = base_path + plt_string
    make_folder(save_path)

    for treatment in treatments:
        for side_effect in side_effects:
            fig = plt.figure()
            description = side_effect.name + '_' + treatment.name
            title = plt_string + ' ' + description
            fig.suptitle(title)
            for attribute in attributes:
                ax = fig.add_subplot(2,3,attribute.idx+1)
                ax.set_xlabel(attribute.name, fontsize=9)
                ax.text(0, 0.5, side_effect.name + ' pre-treatment', rotation='vertical',fontsize=9, transform = ax.transAxes, va='center', ha='left')
                set_tick_label_size(ax.xaxis,9)
                set_tick_label_size(ax.yaxis,9)
        
                before_feature = bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=0*30))
                attribute_feature = attribute.attribute_f

                tuple_feature = bf.cross_feature(attribute_feature, before_feature)
                treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_feature)            
                tuples = bf.feature_applier(tuple_feature)(treatment_iterator)
                tuples.plot(ax, color = attribute.color)
                tuples.plot_best_fit(ax, color = attribute.color, linestyle='-', lw=2, alpha=0.4)

            file_name = get_file_name(save_path, description)
            plt.savefig(file_name)
            print file_name




############################################################################
# for each treatment, plot side effect chance from time 0 to 1 vs attribute#
############################################################################


if True:

    plt_string = 'change_in_state_vs_attribute_by_treatment'

    save_path = base_path + plt_string
    make_folder(save_path)

    for treatment in treatments[0:1]:
        for side_effect in side_effects[4:5]:
            fig = plt.figure()
            description = side_effect.name + '_' + treatment.name
            title = plt_string + ' ' + description
            fig.suptitle(title)
            for attribute in attributes:
                ax = fig.add_subplot(2,3,attribute.idx+1)
                ax.set_xlabel(attribute.name, fontsize=9)
                ax.text(0, 0.5, side_effect.name + ' change', rotation='vertical',fontsize=9, transform = ax.transAxes, va='center', ha='left')
                set_tick_label_size(ax.xaxis,9)
                set_tick_label_size(ax.yaxis,9)
                
                valid_low = attribute.valid_range[0]
                valid_high = attribute.valid_range[1]

                before_feature = bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=0*30))
                after_feature = bf.single_time_processed_time_series(bf.processed_exact_time_series_getter(side_effect.se_series_getter), helper.my_timedelta(days=1*30))
                change_feature = bf.function_feature(lambda x,y: y-x, before_feature, after_feature)
                
                attribute_feature = bf.filter_by_explicit_cutoff_f(valid_low, valid_high, attribute.attribute_f)

                tuple_feature = bf.cross_feature(attribute_feature, change_feature)
                treatment_iterator = bf.filtered_pid_iterable(bf.all_ucla_pid_iterable(), treatment.indicator_feature)            
                
                ans = bf.feature_applier(change_feature)(treatment_iterator)
                pdb.set_trace()

                tuples = bf.feature_applier(tuple_feature)(treatment_iterator)
                tuples.plot(ax, color = attribute.color)
                tuples.plot_best_fit(ax, color = attribute.color, linestyle='-', lw=2, alpha=0.4)

            file_name = get_file_name(save_path, description)
            plt.savefig(file_name)
            print file_name




assert False


