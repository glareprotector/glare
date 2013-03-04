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



side_effect_name = 'incontinence'


pdb.set_trace()


class mean_interval_vals(bf.feature):

    def _generate(self, data_set):
        # can either assume tumor has the series, or calculate the series using text and report feature/time_course feature. assume the former for now
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(self.intervals)
        labeler = bf.single_ordinal_single_value_wrapper_feature.generate(af.get_bucket_label_feature())
        for tumor in data_set:
            urinary_series = tumor.get_attribute(get_tumor_cls().incontinence_time_series)
            this_bl = my_data_types.init_from_intervals_and_ordinal_list(self.intervals, urinary_series)
            # get the interval labels
            interval_labels = this_bl.apply_feature_always_add(labeler)
            bl.lay_in_matching_ordinal_list(interval_labels)
        meaner = bf.single_ordinal_single_value_wrapper_feature.generate(af.get_bucket_mean_feature())
        bl.apply_feature_always_add(meaner)

    def __init__(self, report_feature, intervals):
        self.report_feature
        self.intervals = intervals

class interval_non_zero_counts(bf.feature):

    def _generate(self, data_set):
        # can either assume tumor has the series, or calculate the series using text and report feature/time_course feature. assume the former for now
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(self.intervals)
        labeler = bf.single_ordinal_single_value_wrapper_feature.generate(af.get_bucket_label_feature())
        for tumor in data_set:
            urinary_series = tumor.get_attribute(get_tumor_cls().incontinence_time_series)
            this_bl = my_data_types.init_from_intervals_and_ordinal_list(self.intervals, urinary_series)
            # get the interval labels
            interval_labels = this_bl.apply_feature_always_add(labeler)
            bl.lay_in_matching_ordinal_list(interval_labels)
        counter = bf.single_ordinal_single_value_wrapper_feature.generate(af.get_bucket_count_nonzero_feature())
        bl.apply_feature_always_add(counter)

    def __init__(self, report_feature, intervals):
        self.report_feature
        self.intervals = intervals



"""

plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: True, 'all', g, intervals))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-trmt, all samples')
plt.savefig('ED_all_series.png')



pdb.set_trace()











plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 1, 'pre-treatment YES', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 0, 'pre-treatment NO', g, intervals))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-trmt, stratified by pre-treatment ED')
plt.savefig('ED_proportion_stratified_by_pre_ED_series.png')





pdb.set_trace()



plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 1, 'pre-treatment YES', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 0, 'pre-treatment NO', g, intervals))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('support of ED post-trmt, stratified by pre-treatment ED')
plt.savefig('support_of_ED_proportion_stratified_by_pre_ED_series.png')
















plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.SEERStage_mine_f.generate(x) == 1 and f.treatment_code_f().generate(x) == 2, 'local stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.SEERStage_mine_f.generate(x) == 1 and f.treatment_code_f().generate(x) == 1, 'local stage, SURG', g, intervals))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-trmt, stratified by (RAD/SURG) for pre-treatment ED YES')
plt.savefig('ED_proportion_stratified_by_treatment_pre_ED_YES_series.png')


pdb.set_trace()

plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.SEERStage_mine_f.generate(x) == 1 and f.treatment_code_f().generate(x) == 2, 'local stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.SEERStage_mine_f.generate(x) == 1 and f.treatment_code_f().generate(x) == 1, 'local stage, SURG', g, intervals))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')

plt.title('support of ED post-trmt, stratified by (RAD/SURG) for pre-treatment ED YES')
plt.savefig('support_of_ED_proportion_stratified_by_treatment_pre_ED_YES_series.png')





pdb.set_trace()








plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 0 and f.treatment_code_f().generate(x) == 2, 'pre-treatment ED NO, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 0 and f.treatment_code_f().generate(x) == 1, 'pre-treatment ED NO, SURG', g, intervals))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-trmt, stratified by (RAD/SURG) for pre-treatment ED NO')
plt.savefig('ED_proportion_stratified_by_treatment_pre_ED_NO_series.png')


pdb.set_trace()

plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 0 and f.treatment_code_f().generate(x) == 2, 'pre-treatment ED NO, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) == 0 and f.treatment_code_f().generate(x) == 1, 'pre-treatment ED NO, SURG', g, intervals))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')

plt.title('support of ED post-trmt, stratified by (RAD/SURG) for pre-treatment ED NO')
plt.savefig('support_of_ED_proportion_stratified_by_treatment_pre_ED_NO_series.png')





pdb.set_trace()


"""
































"""





# comparing treatments first for local stage, then for regional stage





plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, SURG', g, intervals ))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-treatment for local stage patients')
plt.savefig('local_stage_ED_proportion_stratified_by_treatment_aED_series.png')


pdb.set_trace()

plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, SURG', g, intervals ))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('support for ED post-treatment for local stage patients')
plt.savefig('support_of_local_stage_ED_proportion_stratified_by_treatment_aED_series.png')


pdb.set_trace()









plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, SURG', g, intervals ))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-treatment for regional stage patients')
plt.savefig('regional_stage_ED_proportion_stratified_by_treatment_aED_series.png')


pdb.set_trace()

plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, SURG', g, intervals ))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('support for ED post-treatment for regional stage patients')
plt.savefig('support_of_regional_stage_ED_proportion_stratified_by_treatment_aED_series.png')


pdb.set_trace()


"""

"""
# support of the 4 series in previous 2 plots


plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) in [0,1] and f.treatment_code_f().generate(x) == 2 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) in [0,1] and f.treatment_code_f().generate(x) == 1 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, SURG', g, intervals ))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) in [0,1] and f.treatment_code_f().generate(x) == 2 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effects.erection_side_effect).generate(x) in [0,1] and f.treatment_code_f().generate(x) == 1 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, SURG', g, intervals ))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('support for ED stratified by surgery & stage, pre-treatment ED state needed')
plt.savefig('support_ED_proportion_stratified_by_treatment_and_stage_if_pre_ED_needed.png')


pdb.set_trace()
"""



"""


# comparing treatments first for local stage, then for regional stage





plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2 and f.grade_f().generate(x) == 2, 'moderate grade, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1 and f.grade_f().generate(x) == 2, 'moderate grade, SURG', g, intervals ))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-treatment for moderate grade patients')
plt.savefig('moderate_ED_proportion_stratified_by_treatment_aED_series.png')


pdb.set_trace()









plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2 and f.grade_f().generate(x) == 3, 'poor grade, RAD', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1 and f.grade_f().generate(x) == 3, 'poor grade, SURG', g, intervals ))




for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals)


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-treatment for poor grade patients')
plt.savefig('poor_grade_ED_proportion_stratified_by_treatment_aED_series.png')


pdb.set_trace()


"""




# plotting stratified curves for no treatment



plt.figure()
plt.xlabel('years after treatment')
g = bf.mean_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, WW', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, WW', g, intervals ))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.grade_f().generate(x) == 2, 'medium grade, WW', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.grade_f().generate(x) == 3, 'poor grade, WW', g, intervals ))



for plot_struct in plot_structs:
    plotters.plot_time_series(the_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals, 'diagnosis')


                    
plt.legend(loc = 'lower_center')
plt.title('ED post-treatment for WW, stratify by stage & grade')
plt.savefig('WW_stratified_by_grade_and_stage_series.png')





plt.figure()
plt.xlabel('years after treatment')
g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.SEERStage_mine_f().generate(x) == 1, 'local stage, WW', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.SEERStage_mine_f().generate(x) == 2, 'regional stage, WW', g, intervals ))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.grade_f().generate(x) == 2, 'medium grade, WW', g, intervals))
plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 0 and f.grade_f().generate(x) == 3, 'poor grade, WW', g, intervals ))



for plot_struct in plot_structs:
    plotters.plot_time_series(the_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.intervals, 'diagnosis')


                    
plt.legend(loc = 'lower_center')
plt.title('support for ED post-treatment for WW, stratify by stage & grade')
plt.savefig('support_for_WW_stratified_by_grade_and_stage_series.png')
