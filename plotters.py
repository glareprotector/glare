import objects
import wc
import my_data_types
import features as f
import matplotlib.pyplot as plt
import numpy as np
import my_exceptions
import pdb

collection_to_bucket = f.single_ordinal_single_value_wrapper_feature

def plot_time_series_by_bins(tumor_list, binner, time_series_intervals, which_attribute, title, file_name):
    """
    binning function needs to be able to assign each tumor to a number, and print out description of each number
    """
    num_intervals = len(time_series_intervals)
    # put tumors into separate list_lists of bucket means
    bin_list_of_bucket_means = [my_data_types.homo_my_list_interval_list() for i in range(binner.get_num_categories())]
    pdb.set_trace()
    for tumor in tumor_list:
        # add interval means for each series to appropriate bin
        which_bin = binner.get_actual_value(tumor)
        series = tumor.get_attribute(which_attribute)
        bucketed_series = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(time_series_intervals, series)
        interval_means = bucketed_series.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature()))
        bin_list_of_bucket_means[which_bin].append(interval_means)

    # collapse each list of interval means into a single interval means
    pdb.set_trace()
    bin_list_of_bucket_means_buckets = [hlil.get_bucket_ordinal_list() for hlil in bin_list_of_bucket_means]
    bin_list_of_bucket_means_bucket_means = [bl.apply_feature_always_add(collection_to_bucket(f.get_bucket_mean_feature()), ) for bl in bin_list_of_bucket_means_buckets]

    # now, have an single_ordinal_ordinal_list for each bin (intervals, interval means - in get_value).  can then do the actual plotting
    bin_labels = binner.get_bin_descriptions()
    # assume intervals are continguous
    x_boundaries = np.zeros(num_intervals + 1)
    for i in range(num_intervals):
        x_boundaries[i] = time_series_intervals[i].low.days/365
    x_boundaries[-1] = time_series_intervals[-1].high.days/365
    for i in range(binner.get_num_bins()):
        y_values = []
        for item in bin_list_of_bucket_means_bucket_means[i]:
            try:
                to_add = item.get_value()
            except my_exceptions.NoFxnValueException:
                to_add = -1.0
            y_values.append(to_add)
        y_values.append(-1)
        pdb.set_trace()
        plt.step(x_boundaries, y_values, label = bin_labels[i], where='post')
    plt.legend()
    plt.title(title)
    plt.savefig(file_name)
