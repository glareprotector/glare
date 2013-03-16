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
AA = set(wc.get_stuff(objects.prostate_PID,p))
#AAA = AA - A
AAA = A
B = set(wc.get_stuff(objects.PID_with_shared_MRN, p))
C = set(wc.get_stuff(objects.PID_with_multiple_tumors, p))
PID_to_use = list(AAA - B - C)
test_PID_to_use = PID_to_use


the_data_set = helper.data_set(test_PID_to_use)
treated_data_set = the_data_set.filter(lambda x: f.treatment_code_f().generate(x) in [1,2])
interval_boundaries = [0,0.5,1,1.5,2,5]
intervals = [my_data_types.ordered_interval(helper.my_timedelta(interval_boundaries[i]*365), helper.my_timedelta(interval_boundaries[i+1]*365)) for i in range(len(interval_boundaries)-1)]

#pdb.set_trace()

side_effect_name = 'urinary_frequency_expanded'
side_effect_instance = side_effects.urinary_frequency_bin()



label_method = 'justone'

path = 'plots/' + label_method + '_'

class mean_interval_vals(bf.feature):

    def _generate(self, data_set):
        # can either assume tumor has the series, or calculate the series using text and report feature/time_course feature. assume the former for now
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(self.intervals)
        count_bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(self.intervals)
        labeler = bf.single_ordinal_single_value_wrapper_feature(af.get_bucket_label_feature_justone())
        non_zeroer = bf.single_ordinal_single_value_wrapper_feature(af.get_bucket_count_nonzero_feature())
        for pid in data_set:
            #urinary_series = tumor.get_attribute(get_tumor_cls().incontinence_time_series)
            #series = tumor.get_attribute(self.series_attribute)
            #rel_to_treatment = bf.adjust_time_series().generate(series, f.treatment_date_f().generate(tumor) - tumor.get_attribute(global_stuff.get_tumor_cls().date_diagnosed))
            try:
                series = bf.report_feature_time_course_feature_relative().generate(pid, self.side_effect, 'treatment')
            except:
                pass
            else:
                this_bl = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(self.intervals, series)
                #print this_bl
                #pdb.set_trace()
                #get the interval labels
                interval_labels = this_bl.apply_feature_always_add(labeler)
                interval_nonzeros = this_bl.apply_feature_always_add(non_zeroer)
                bl.lay_in_matching_ordinal_list(interval_labels)
                count_bl.lay_in_matching_ordinal_list(interval_nonzeros)
        meaner = bf.single_ordinal_single_value_wrapper_feature(af.get_bucket_mean_feature())
        counter = bf.single_ordinal_single_value_wrapper_feature(af.get_bucket_sum_feature())
        return bl.apply_feature_always_add(meaner), count_bl.apply_feature_always_add(counter)

    def __init__(self, side_effect, intervals):
        self.side_effect = side_effect
        self.intervals = intervals

class interval_non_zero_counts(bf.feature):

    def _generate(self, data_set):
        # can either assume tumor has the series, or calculate the series using text and report feature/time_course feature. assume the former for now
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(self.intervals)
        non_zeroer = bf.single_ordinal_single_value_wrapper_feature(af.get_bucket_count_nonzero_feature())
        for pid in data_set:
            try:
                series = bf.report_feature_time_course_feature_relative().generate(pid, self.side_effect, 'treatment')
            except:
                pass
            else:
                series = tumor.get_attribute(self.series_attribute)
                rel_to_treatment = bf.adjust_time_series().generate(series, f.treatment_date_f().generate(tumor) - tumor.get_attribute(global_stuff.get_tumor_cls().date_diagnosed))
                this_bl = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(self.intervals, rel_to_treatment)


                interval_nonzeros = this_bl.apply_feature_always_add(non_zeroer)
                bl.lay_in_matching_ordinal_list(interval_nonzeros)
        counter = bf.single_ordinal_single_value_wrapper_feature(af.get_bucket_sum_feature())

        ans = bl.apply_feature_always_add(counter)

        return ans

    def __init__(self, series_attribute, intervals):
        self.series_attribute = series_attribute
        self.intervals = intervals





# 

























#g = mean_interval_vals(side_effect_instance, intervals)

#print g.generate(the_data_set)

#assert False

# these are the plots that with pre-state fixed, stratify by treatment as well as some patient attribute


overweight_strat_desc = 'overweight'

def overweight_strat_f(pid):
    return f.BMI_f().generate(pid) > 32

high_psa_strat_desc = 'high_psa'

def high_psa_strat_f(pid):
    return f.psa_value_f().generate(pid) > 70

old_age_strat_desc = 'old_age'

def old_age_strat_f(pid):
    return f.age_at_diagnosis_f().generate(pid) > 70

side_effect_instances = [side_effects.erection_side_effect(), side_effects.urin_incont_bin(), side_effects.urinary_frequency_bin(), side_effects.diarrhea_bin()]
strat_fs = [overweight_strat_f, high_psa_strat_f, old_age_strat_f]
strat_descs = [overweight_strat_desc, high_psa_strat_desc, old_age_strat_desc]


for side_effect_instance in side_effect_instances:
    side_effect_name = str(side_effect_instance)
    for strat_f, strat_desc in zip(strat_fs, strat_descs):


        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1 and f.treatment_code_f().generate(x) == 2 and strat_f(x) == True, 'RAD_yes_'+strat_desc, g, 'c'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1 and f.treatment_code_f().generate(x) == 1 and strat_f(x) == True, 'SURG_yes_'+strat_desc, g, 'r'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1 and f.treatment_code_f().generate(x) == 2 and strat_f(x) == False, 'RAD_no_'+strat_desc, g, 'g'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1 and f.treatment_code_f().generate(x) == 1 and strat_f(x) == False, 'SURG_no_'+strat_desc, g, 'b'))


        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated_pre_good_by_treatment_' + strat_desc
        plt.title(title)
        plt.savefig(path+title + '.png')





        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []

        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0 and f.treatment_code_f().generate(x) == 2 and strat_f(x) == True, 'RAD_yes_'+strat_desc, g, 'c'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0 and f.treatment_code_f().generate(x) == 1 and strat_f(x) == True, 'SURG_yes_'+strat_desc, g, 'r'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0 and f.treatment_code_f().generate(x) == 2 and strat_f(x) == False, 'RAD_no_'+strat_desc, g, 'g'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0 and f.treatment_code_f().generate(x) == 1 and strat_f(x) == False, 'SURG_no_'+strat_desc, g, 'b'))


        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated_pre_bad_by_treatment_' + strat_desc
        plt.title(title)
        plt.savefig(path+title + '.png')









        #first 2 plots do not stratify by treatment


        #all treated patients


        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []
        plot_structs.append(plotters.plot_struct(lambda x: True, 'all', g, 'c'))

        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated'
        plt.title(title)
        plt.savefig(path+title + '.png')









        #all treated patients stratified by pre_treatment state


        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1, 'pre_good', g, 'c'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0, 'pre_bad', g, 'r'))


        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated_by_pre_treatment_state'
        plt.title(title)
        plt.savefig(path+title + '.png')














        #all treated patients stratified by treatment






        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []
        plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 2, 'RAD', g, 'c'))
        plot_structs.append(plotters.plot_struct(lambda x: f.treatment_code_f().generate(x) == 1, 'SURG', g, 'r'))

        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated_by_treatment'
        plt.title(title)
        plt.savefig(path+title + '.png')










        #all treated patients stratified by treatment and pre-treatment state
        #will redo these 2 plots (so make 2 more).  plots will have same pre-treatment state, but further stratify on some function





        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1 and f.treatment_code_f().generate(x) == 2, 'RAD', g, 'c'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 1 and f.treatment_code_f().generate(x) == 1, 'SURG', g, 'r'))


        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated_pre_good_by_treatment'
        plt.title(title)
        plt.savefig(path+title + '.png')












        plt.figure()
        plt.xlabel('years after treatment')
        g = mean_interval_vals(side_effect_instance, intervals)
    
        plot_structs = []
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0 and f.treatment_code_f().generate(x) == 2, 'RAD', g, 'c'))
        plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f().generate(x, side_effect_instance) == 0 and f.treatment_code_f().generate(x) == 1, 'SURG', g, 'r'))


        for plot_struct in plot_structs:
            plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g, plot_struct.color)

        plt.legend(loc = 'lower_center')
        title = side_effect_name + '_' + 'all_treated_pre_bad_by_treatment'
        plt.title(title)
        plt.savefig(path+title + '.png')








assert False

#pdb.set_trace()




# STOP HERE







"""

plt.figure()
plt.xlabel('years after treatment')
g = interval_non_zero_counts(side_effect_series_attribute, intervals)
    
plot_structs = []
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effect_instance).generate(x) == 1 and f.treatment_code_f().generate(x) == 2, 'pre-good, RAD', g))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effect_instance).generate(x) == 1 and f.treatment_code_f().generate(x) == 1, 'pre-good, SURG', g))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effect_instance).generate(x) == 0 and f.treatment_code_f().generate(x) == 2, 'pre-bad, RAD', g))
plot_structs.append(plotters.plot_struct(lambda x: f.pre_treatment_side_effect_label_f(side_effect_instance).generate(x) == 0 and f.treatment_code_f().generate(x) == 1, 'pre-bad, SURG', g))



for plot_struct in plot_structs:
    plotters.plot_time_series(treated_data_set, plot_struct.filtering_f, plot_struct.label, plot_struct.g)

plt.legend(loc = 'lower_center')
title = side_effect_name + '_' + 'all_treated_by_treatment_and_pre_treatment_state_support'
plt.title(title)
plt.savefig(title + '.png')



pdb.set_trace()



"""







# can i assume that treatment received is independent of state?

# comparing untreated patients to treated patients - consider plotting fitness after diagnosis for each treatment.  but age is probably a covariate.  separately, plot(or get mean of) age at treatment for each treatment





























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




"""











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
