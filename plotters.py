import objects
import wc
import my_data_types
import features as f
import matplotlib.pyplot as plt
import numpy as np
import my_exceptions
import pdb

collection_to_bucket = f.single_ordinal_single_value_wrapper_feature


class plot_struct(object):

    def __init__(self, filtering_f, label, g, color):
        self.filtering_f = filtering_f
        self.label = label
        self.g = g
        self.color = color



def print_filtered_counts(data_set, filtering_f, label):
    filtered_data_set = data_set.filter(filtering_f)
    print label, len(filtered_data_set.the_data)








def plot_time_series(data_set, filtering_f, label, g, color):
    """
    given dataset, filtering_f for dataset, and g which takes in only a tumor and outputs a interval series, adds the interval series to the plot
    """
    filtered_data_set = data_set.filter(filtering_f)

    series, counts = g.generate(filtered_data_set)
    print series, counts

    x_boundaries = np.zeros(len(series) + 1)
    for i in range(len(series)):
        x_boundaries[i] = series[i].get_ordinal().low.days/365.0
    x_boundaries[-1] = series[-1].get_ordinal().high.days/365.0
    y_values = []
    y_lower = []
    y_upper = []

    for item, count in zip(series, counts):
        try:
            ans = item.get_value()
        except my_exceptions.NoFxnValueException:
            ans = 0.0
            width = 0.0
        else:
            num = count.get_value()
            sd = pow(ans*(1-ans)/float(num), 0.5)
            width = 1.96 * sd
        y_values.append(ans)
        y_upper.append(ans + width)
        y_lower.append(ans - width)
        
    y_values.append(0)
    y_upper.append(0)
    y_lower.append(0)
    line = plt.step(x_boundaries, y_values, label = label, where='post')
    plt.setp(line, ls='-', lw=3, color = color)
    line = plt.step(x_boundaries, y_upper, where='post')
    plt.setp(line, ls='--', lw=1, color = color)
    line = plt.step(x_boundaries, y_lower, where='post')
    plt.setp(line, ls='--', lw=1, color = color)
    #plt.step(x_boundaries, y_values, 'post', {'label':label,'linestyle':'dotted'})
    print label, len(filtered_data_set)


def plot_time_series_CI(data_set, filtering_f, label, g):
    """
    given dataset, filtering_f for dataset, and g which takes in only a tumor and outputs a interval series, adds the interval series to the plot
    """
    filtered_data_set = data_set.filter(filtering_f)
    series = g.generate(filtered_data_set)
    #print series

    x_boundaries = np.zeros(len(series) + 1)
    for i in range(len(series)):
        x_boundaries[i] = series[i].get_ordinal().low.days/365.0
    x_boundaries[-1] = series[-1].get_ordinal().high.days/365.0
    y_values = []
    for item in series:
        try:
            ans = item.get_value()
        except my_exceptions.NoFxnValueException:
            ans = 0.0
        y_values.append(ans)
    y_values.append(-1)
    line = plt.step(x_boundaries, y_values, label = label, where='post')
    plt.setp(line, ls='-', lw=3)
    #plt.step(x_boundaries, y_values, 'post', {'label':label,'linestyle':'dotted'})
    print label, len(filtered_data_set.the_data)





def plot_time_series_by_bins(tumor_list, binner, time_series_intervals, which_attribute, title, file_name):
    """
    binning function needs to be able to assign each tumor to a number, and print out description of each number
    """
    num_intervals = len(time_series_intervals)
    # have 1 bucket list that holds interval means for each bin
    bucket_lists_with_interval_means = [my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(time_series_intervals) for i in range(binner.get_num_categories())]
    count = 0
    for tumor in tumor_list:
        print count
        count += 1
        try:
            which_bin = binner.get_actual_value(tumor)
            series = tumor.get_attribute(which_attribute)
            bucketed_series = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(time_series_intervals, series)
            interval_means = bucketed_series.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature()))
        
            bucket_lists_with_interval_means[which_bin].lay_in_matching_ordinal_list(interval_means)
        except:
            import traceback, sys
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno,fn,text = frame
                print "Error in %s on line %d" % (fname, lineno)
            print sys.exc_traceback.tb_lineno

    list_of_interval_means = [bl.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature())) for bl in bucket_lists_with_interval_means]

    # now, have an single_ordinal_ordinal_list for each bin (intervals, interval means - in get_value).  can then do the actual plotting
    bin_labels = binner.get_category_descriptions()
    # assume intervals are continguous
    x_boundaries = np.zeros(num_intervals + 1)
    for i in range(num_intervals):
        x_boundaries[i] = time_series_intervals[i].low.days/365
    x_boundaries[-1] = time_series_intervals[-1].high.days/365
    for i in range(binner.get_num_categories()):
        y_values = []
        for item in list_of_interval_means[i]:
            try:
                to_add = item.get_value()
            except my_exceptions.NoFxnValueException:
                to_add = -1.0
            y_values.append(to_add)
        y_values.append(-1)
        plt.step(x_boundaries, y_values, label = bin_labels[i], where='post')
    plt.legend()
    plt.title(title)
    plt.savefig(file_name)
