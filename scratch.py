import wc
import param
import objects
import helper
import pdb
import features as f
import basic_features as bf
import aggregate_features as af
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

import match_features

a = match_features.base_fragment("This is a sentence:  This is a \n sentence also.  There is a lol.")

#m = match_features.sentence_fragment_getter()
m = match_features.fragment_getter_by_stuff_after_colon()
#pdb.set_trace()
print m.get_fragment(a, 10)


#print m.get_match(a, ['asdf'])

#pdb.set_trace()

sosv = bf.single_ordinal_single_value_wrapper_feature


p = global_stuff.get_param()

A = set(wc.get_stuff(objects.PID_with_SS_info, p))
B = set(wc.get_stuff(objects.PID_with_shared_MRN, p))
C = set(wc.get_stuff(objects.PID_with_multiple_tumors, p))
PID_to_use = list(A - B - C)

test_PID_to_use = PID_to_use[2100:2110]

the_data_set = helper.data_set.data_set_from_pid_list(test_PID_to_use, p)






treated_data_set = the_data_set.filter(lambda x: f.treatment_code_f().generate(x) in [1,2])


# try to classify 


incontinence_feature = side_effects.urinary_incontinence()

for tumor in treated_data_set.the_data:
    for record in tumor.get_attribute(get_tumor_cls().texts):
        if record.date < f.treatment_date_f().generate(tumor):
            for excerpt in record.get_excerpts_by_words(['urinary','voiding','urination','leak','leaks','leakage','incontinence','incontinent','continent','continence']):
#        for excerpt in record.get_excerpts_by_words(['leakage']):
            #print excerpt
                print record
                pdb.set_trace()
                print incontinence_feature.generate(record)

                break





interval_boundaries = [-100,0,0.5,1,2,5]
intervals = [my_data_types.ordered_interval(helper.my_timedelta(interval_boundaries[i]*365), helper.my_timedelta(interval_boundaries[i+1]*365)) for i in range(len(interval_boundaries)-1)]


bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(intervals)

count = 0
has_something = 0



has_pre = []


for pid in PID_to_use:
    print count, pid
    p.set_param('pid', pid)
    try:
        tumor = wc.get_stuff(objects.global_stuff.get_tumor_w(), p)
        record_list = tumor.get_attribute(global_stuff.get_tumor_cls().texts)
        diagnosis_date = tumor.get_attribute(global_stuff.get_tumor_cls().date_diagnosed)
        
        
        time_course_f = bf.report_feature_time_course_feature(bf.side_effect_report_record_has_info_feature(side_effects.urinary_incontinence))
        
        series = time_course_f.generate(record_list, 'diagnosis', diagnosis_date)
        
        series_bucket = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(intervals, series)
        
        series_interval_vals = series_bucket.apply_feature(sosv(af.get_bucket_count_nonzero_feature()))
        
        if series_interval_vals[0].get_value() == 1:
            has_something += 1


            for i in range(len(record_list)):
                p.set_param('rec_idx',i)
                wc.get_stuff(objects.side_effect_human_input_report_labels, p)
            





        bl.lay_in_matching_ordinal_list(series_interval_vals)

        count += 1

        


    except:
        pass

    print has_something, count

have_keyword_counts = bl.apply_feature(sosv(af.get_bucket_count_feature()))
pdb.set_trace()

for pid in test_PID_to_use:
    p.set_param('pid', pid)
    record_list = wc.get_stuff(objects.raw_medical_text_new, p)
    for i in range(len(record_list)):
        p.set_param('rec_idx',i)
        wc.get_stuff(objects.side_effect_human_input_report_labels, p)









g = bf.count_of_side_effect_intervals_values_f(side_effects.erection_side_effect)


counts = g.generate(the_data_set, intervals, 'diagnosis')

pdb.set_trace()

"""
for pid in PID_to_use:
    p.set_param('pid', pid)
    reports = wc.get_stuff(objects.raw_pathology_text, p)
    print reports
    pdb.set_trace()
"""




pdb.set_trace()
for tumor in the_data_set.the_data:
    for record in tumor.get_attribute(get_tumor_cls().texts):

        to_look_at = False
        try:
            if record.date < f.treatment_date_f().generate(tumor):
                to_look_at = True
        except:
            pass
        treatment_code = f.treatment_code_f().generate(tumor)
        if treatment_code == 0:
            to_look_at = True
        if to_look_at:
            for excerpt in record.get_excerpts_by_side_effect(side_effects.erection_side_effect):
                print 'TREATMENT: ', treatment_code
                if treatment_code in [1,2]:
                    print 'COMPARISON: ',  record.date, tumor.get_attribute(get_tumor_cls().date_diagnosed), f.treatment_date_f().generate(tumor)
                print excerpt
                try:
                    label = bf.side_effect_excerpt_feature(side_effects.erection_side_effect).generate(excerpt)
                    print 'LABEL: ', label
                except Exception, err:
                    print 'EEEEEEEEEEEEEERRRRRRRRRRRRRRRRROR ', Exception, err
                pdb.set_trace()





print 'afsdfasdfasdfasdf'
pdb.set_trace()






num_no_value, num_0, num_1 = 0,0,0
for tumor in treated_data_set:
    try:
        pre = bf.pre_treatment_side_effect_label(side_effects.erection_side_effect).generate(tumor).get_value()
    except my_exceptions.NoFxnValueException:
        num_no_value += 1
    else:
        if pre == 0:
            num_0 += 1
        elif pre == 1:
            num_1 += 1
    print f.treatment_date_f().generate(tumor) - tumor.get_attribute(get_tumor_cls().date_diagnosed), pre
    
    
print num_no_value, num_0, num_1
raise

treated_data_set = the_data_set.filter(lambda x: f.treatment_code_f().generate(x) in [1,2])







































pdb.set_trace()


feature_list = [f.treatment_code_f(), f.age_at_diagnosis_f(), f.age_at_LC_f(), f.vital_status_f(), f.age_at_LC_f(), f.follow_up_time_f()]

feature_string = the_data_set.get_csv_string(feature_list)
print feature_string

f = open('test_features.csv', 'w')
f.write(feature_string)

raise Exception

deads = filter(lambda x: f.single_attribute_feature(helper.tumor.alive).generate(x) == 0, tumor_list)

# plot age at diagnosis vs number of years lived
ages = [(x.get_attribute(tumor_class.date_diagnosed) - x.get_attribute(tumor_class.DOB)).days/365.0 for x in tumor_list]
post_lived = [(x.get_attribute(tumor_class.DLC) - x.get_attribute(tumor_class.date_diagnosed)).days/365.0 for x in tumor_list]
total_lived = [(x.get_attribute(tumor_class.DLC) - x.get_attribute(tumor_class.DOB)).days/365.0 for x in tumor_list]

print 'mean', sum(ages) / float(len(ages))
pdb.set_trace()


plt.scatter(ages, post_lived, label = 'post_lived', color = 'red')
plt.scatter(ages, total_lived, label = 'total_lived', color = 'blue')

plt.legend()
plt.savefig('years_vs_diagnosis_age.pdf')






pdb.set_trace()






interval_boundaries = numpy.array(range(-4,20)) / 2.0
intervals = [my_data_types.ordered_interval(helper.my_timedelta(interval_boundaries[i]*365), helper.my_timedelta(interval_boundaries[i+1]*365)) for i in range(len(interval_boundaries)-1)]


the_binner = f.treatment_code_categorical_feature()


plotters.plot_time_series_by_bins(tumor_list, the_binner, intervals, helper.tumor.erection_time_series, 'test', 'test.pdf')



raise




































collection_to_bucket = f.single_ordinal_single_value_wrapper_feature_factory.get_feature
sv = f.get_wrapped_single_value_object_feature_factory.get_feature().generate


count = 0

erection_time_series_list = my_data_types.my_list_ordinal_list()
erection_interval_buckets_list = my_data_types.homo_my_list_interval_list()
erection_interval_means = my_data_types.homo_my_list_interval_list()
erection_interval_counts = my_data_types.homo_my_list_interval_list()
erection_interval_nonzeros = my_data_types.homo_my_list_interval_list()
erection_interval_labels = my_data_types.homo_my_list_interval_list()

series_spans = my_data_types.my_list()
series_mins = my_data_types.my_list()
series_maxes = my_data_types.my_list()

interval_boundaries = [-50] + range(-26,26,2) + [50]
intervals = [my_data_types.ordered_interval(helper.my_timedelta(interval_boundaries[i]*365), helper.my_timedelta(interval_boundaries[i+1]*365)) for i in range(len(interval_boundaries)-1)]

span_boundaries = range(0,52,2)
span_intervals = [my_data_types.ordered_interval(helper.my_timedelta(span_boundaries[i]*365), helper.my_timedelta(span_boundaries[i+1]*365)) for i in range(len(span_boundaries)-1)]
min_boundaries = [-50] + range(-26,26,2) + [50]
min_intervals = [my_data_types.ordered_interval(helper.my_timedelta(min_boundaries[i]*365), helper.my_timedelta(min_boundaries[i+1]*365)) for i in range(len(min_boundaries)-1)]
max_boundaries = [-50] + range(-26,26,2) + [50]
max_intervals = [my_data_types.ordered_interval(helper.my_timedelta(max_boundaries[i]*365), helper.my_timedelta(max_boundaries[i+1]*365)) for i in range(len(max_boundaries)-1)]



interval_means_means_f = open('interval_means_means_beam.csv', 'a')
interval_counts_sums_f = open('interval_counts_sums_beam.csv', 'a')
interval_nonzeros_sums_f = open('interval_nonzeros_sums_beam.csv', 'a')
interval_labels_means_f = open('interval_labels_means_beam.csv', 'a')
min_intervals_f = open('min_intervals_beam.csv', 'a')
max_intervals_f = open('max_intervals_beam.csv', 'a')
span_intervals_f = open('span_intervals_beam.csv', 'a')




temp = collection_to_bucket(f.get_bucket_count_feature())

for pid in PID_to_use:

    print 'NUMBER OF TUMORS PROCeSSED: ', count, ' TOTAL: ', len(PID_to_use)


    try:
        p.set_param('pid', pid)
        tumor = wc.get_stuff(objects.tumor_w, p)
        
        if tumor.get_attribute(tumor.radiation_code) == '1':
            
            count += 1

            #get new series
            #series = f.report_feature_time_course_feature_factory.get_feature(f.side_effect_report_record_feature_factory.get_feature(side_effects.erection_side_effect)).generate(tumor, True)
            series = tumor.get_attribute(tumor.erection_time_series)
            helper.print_if_verbose(str(series),1)
            pickle.dump(series, open('temp.pickle','wb'))
            pdb.set_trace()
            # add to time_series_list
            erection_time_series_list.append(series)

            # calculated bucketed time_series 
            bucketed_series = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(intervals, series)

            # from bucketed_series, calculate interval means, counts, labels
            interval_means = bucketed_series.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature()))
            interval_counts = bucketed_series.apply_feature_always_add(collection_to_bucket(f.get_bucket_count_feature()))
            interval_nonzeros = bucketed_series.apply_feature_always_add(collection_to_bucket(f.get_bucket_count_nonzero_feature()))
            interval_labels = bucketed_series.apply_feature_always_add(collection_to_bucket(f.get_bucket_label_feature()))

            # add to storage
            erection_interval_means.append(interval_means)
            erection_interval_counts.append(interval_counts)
            erection_interval_nonzeros.append(interval_nonzeros)
            erection_interval_labels.append(interval_labels)

            def calc_stuff():
                return count % 50 == 0


            if calc_stuff():

                # convert storages to buckets so i can apply functons on those buckets
                erection_interval_means_buckets = erection_interval_means.get_bucket_ordinal_list()
                erection_interval_counts_buckets = erection_interval_counts.get_bucket_ordinal_list()
                erection_interval_nonzeros_buckets = erection_interval_nonzeros.get_bucket_ordinal_list()
                erection_interval_labels_buckets = erection_interval_labels.get_bucket_ordinal_list()                                        
                # apply function to buckets
                erection_interval_means_means = erection_interval_means_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature()))
                erection_interval_counts_sums = erection_interval_counts_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_sum_feature()))
                erection_interval_nonzeros_sums = erection_interval_nonzeros_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_sum_feature()))
                erection_interval_labels_means = erection_interval_labels_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature()))
                # print stuff
                helper.print_if_verbose('interval mean means: ' + str(erection_interval_means_means), 0.5)
                helper.print_if_verbose('interval count sums: ' + str(erection_interval_counts_sums), 0.5)
                helper.print_if_verbose('interval nonzero sums: ' + str(erection_interval_nonzeros_sums), 0.5)
                helper.print_if_verbose('interval label means: ' + str(erection_interval_labels_means), 0.5)
                # write stuff
                interval_means_means_f.write(helper.interval_val_as_string(erection_interval_means_means) + '\n')
                interval_counts_sums_f.write(helper.interval_val_as_string(erection_interval_counts_sums) + '\n')
                interval_nonzeros_sums_f.write(helper.interval_val_as_string(erection_interval_nonzeros_sums) + '\n')
                interval_labels_means_f.write(helper.interval_val_as_string(erection_interval_labels_means) + '\n')
                interval_means_means_f.flush()
                interval_counts_sums_f.flush()
                interval_nonzeros_sums_f.flush()
                interval_labels_means_f.flush()

                # also maintain 3 lists: spans, low_date, high_dates
                # put them into intervals.  have to store as sv's, so that i can use those fxns
                series_min = f.get_bucket_min_feature().generate(series)
                series_mins.append(series_min)
                series_max = f.get_bucket_max_feature().generate(series)
                series_maxes.append(series_max)
                # try adding span, but this won't make sense if either is no_value
                try:
                    series_min.get_value()
                    series_max.get_value()
                except:
                    pass
                else:
                    series_span = my_data_types.single_ordinal_single_value_ordered_object(helper.my_timedelta(series_max.get_ordinal().days - series_min.get_ordinal().days), None)
                    series_spans.append(series_span)
                             

        
                def calc_range_stuff():
                    return count % 50 == 0

                if calc_range_stuff():
                    # turn 3 lists into buckets(of sosv datapoints)
                    series_mins_buckets = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(min_intervals, series_mins)
                    series_maxes_buckets = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(max_intervals, series_maxes)
                    series_spans_buckets = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(max_intervals, series_spans)
                    # calculate totals in those buckets
                    series_mins_interval_counts = series_mins_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_count_feature()))
                    series_maxes_interval_counts = series_maxes_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_count_feature()))
                    series_spans_interval_counts = series_spans_buckets.apply_feature_always_add(collection_to_bucket(f.get_bucket_count_feature()))
                    # print stuff
                    # helper.print_if_verbose('mins: ' + str(series_mins), 0.5)
                    helper.print_if_verbose('interval min counts: ' + str(series_mins_interval_counts), 0.5)
                    # helper.print_if_verbose('maxes: ' + str(series_maxes), 0.5)
                    helper.print_if_verbose('interval max counts: ' + str(series_maxes_interval_counts), 0.5)
                    # helper.print_if_verbose('spans: ' + str(series_spans), 0.5)
                    helper.print_if_verbose('interval span counts: ' + str(series_spans_interval_counts), 0.5)                
                    # write stuff
                    min_intervals_f.write(helper.interval_val_as_string(series_mins_interval_counts) + '\n')
                    max_intervals_f.write(helper.interval_val_as_string(series_maxes_interval_counts) + '\n')            
                    span_intervals_f.write(helper.interval_val_as_string(series_spans_interval_counts) + '\n')
                    min_intervals_f.flush()
                    max_intervals_f.flush()
                    span_intervals_f.flush()




    except Exception, err:
        print err
        import traceback, sys
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            fname, lineno,fn,text = frame
            print "Error in %s on line %d" % (fname, lineno)
        print sys.exc_traceback.tb_lineno

        #helper.print_traceback()
