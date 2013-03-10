import my_exceptions
import my_data_types
import global_stuff
import pdb
from param import param

# import might cause problems
from wc import wc
import objects

from my_data_types import sv_int, sv_float

class feature(object):
    """
    feature is just a class that takes in a tumor or something, and implements callable
    """
    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)

    def generate(self, *args, **kwargs):
        ans = self._generate(*args, **kwargs)
        self.error_check(ans)
        return ans

    def error_check(self, *args):
        pass

    def __len__(self):
        return 1

    def get_name(self):
        return self.__class__.__name__

class range_checked_feature(feature):
    

    def error_check(self, *args, **kwargs):
        pass
        #lower, upper = self.get_valid_range()
        #if self.get_code(tumor) < lower or self.get_code(tumor) > upper:
        #    raise my_exceptions.ScalarFeatureOutOfRange

    def get_valid_range(self):
        return self.low, self.high

    def __init__(self, low, high):
        self.low = low
        self.high = high




class generic_categorical_feature(feature):
    """
    always based on some feature.  specify that, as well as the possible values
    returns a list
    """

    def error_check(self, *args, **kwargs):
        pass
        #if self.backing_feature.generate(tumor) not in self.get_possible_values():
        #    raise Exception

    def _generate(self, *args):
        import helper
        ans = [1 if helper.compare_in(self.backing_feature.generate(*args), val) else 0 for val in self.get_possible_values()]
        return ans

    def get_possible_values(self):
        return self.possible_values

    def __init__(self, possible_values, backing_feature, category_descriptions = None):
        self.possible_values = possible_values
        self.backing_feature = backing_feature
        if category_descriptions == None:
            self.category_descriptions = ['' for i in range(len(self.possible_values))]
        else:
            self.category_descriptions = category_descriptions

    def __len__(self):
        return self.get_num_categories()

    def get_num_categories(self):
        return len(self.get_possible_values())

    def get_category_descriptions(self):
        return self.category_descriptions

    def get_actual_value(self, tumor):
        return self.backing_feature.generate(tumor)






class report_feature_absolute_time_course_feature(feature):

    def _generate(self, pid, side_effect):
        """
        just directly gets absolute side effect/pid specified series from wc
        """
        p = param({'pid':pid, 'side_effect':side_effect})
        ans = wc.get_stuff(objects.side_effect_time_series, p)
        return ans



class report_feature_time_course_feature_relative(feature):
    """
    returns the side effect series.  raises NoFxnValueException if the patient did not get a treatment, and relative to treatment is specified
    """
    def _generate(self, pid, side_effect, relative_option):
        assert relative_option in ['absolute', 'diagnosis', 'treatment']
        import copy, features
        series_copy = copy.deepcopy(report_feature_absolute_time_course_feature().generate(pid, side_effect))
        if relative_option == 'absolute':
            return series_copy
        elif relative_option == 'treatment':
            treatment_date = features.treatment_date_f().generate(pid)
            for item in series_copy:
                item.set_ordinal(item.get_ordinal() - treatment_date)
            return series_copy
        elif relative_option == 'diagnosis':
            date_diagnosed = features.date_diagnosed_f().generate(pid)
            for item in series_copy:
                item.set_ordinal(item.get_ordinal() - date_diagnosed)
            return series_copy
        








class side_effect_intervals_values_f(side_effect_feature):
    """
    should never raise exception.  return list of NA's if necessary
    """
    def _generate(self, pid, side_effect, relative_to_what, intervals):
        series = report_feature_time_course_feature_relative.generate(pid, side_effect, relative_to_what)
        # put the time series into bucket list by intervals
        import my_data_types
        import aggregate_features as af
        bucket_list = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(intervals, series)
        bucket_f = single_ordinal_single_value_wrapper_feature(af.get_bucket_label_feature())
        interval_labels = bucket_list.apply_feature_always_add(bucket_f)
        return interval_labels

# FIX: now, data_set will just be a list of pid's.  intervals and relative_to_what will still be specified, as well as side_effect_feature since there is no longer a side_effect_feature class
class mean_of_side_effect_intervals_values_f(side_effect_feature):

    def _generate(self, pid_list, side_effect, relative_to_what, intervals):
        import my_data_types, aggregate_features
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(intervals)
        for pid in pid_list:
            interval_labels = side_effect_intervals_values_f().generate(pid, side_effect, relative_to_what, intervals)
            bl.lay_in_matching_ordinal_list(interval_labels)
        meaner = single_ordinal_single_value_wrapper_feature(aggregate_features.get_bucket_mean_feature())
        ans = bl.apply_feature_always_add(meaner)
        return ans


# FIX: same as previous
class count_of_side_effect_intervals_values_f(side_effect_feature):

    def _generate(self, pid_list, side_effect, relative_to_what, intervals):

        import my_data_types, aggregate_features
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(intervals)
        for pid in pid_list:
            interval_counts = side_effect_intervals_values_f(self.get_side_effect()).generate(tumor, intervals, relative_to_what)
            bl.lay_in_matching_ordinal_list(interval_counts)
        counter = single_ordinal_single_value_wrapper_feature(aggregate_features.get_bucket_count_feature())
        ans = bl.apply_feature_always_add(counter)
        return ans
            

class side_effect_interval_value_f(side_effect_feature):

    def _generate(self, pid, side_effect, relative_to_what, interval):
        intervals = [interval]
        return side_effect_intervals_values_f().generate(pid, side_effect, relative_to_what, intervals)




class hard_coded_side_effect_interval_value_f(feature):
    """
    returns label value in interval specified in years.  relative to what is also specified
    """
    def __init__(self, side_effect, relative_to_what, interval):
        self.interval = interval
        self.relative_to_what = relative_to_what
        self.side_effect = side_effect

    def _generate(self, pid):
        return side_effect_interval_value_f(self.get_side_effect()).generate(tumor, self.interval, self.relative_to_what).get_value()


class one_year_incontinence_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.urin_incont_bin(), my_data_types.ordered_interval(helper.my_timedelta(0.5*365), helper.my_timedelta(1*365)), 'treatment')



class two_year_erection_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.erection_side_effect(), my_data_types.ordered_interval(helper.my_timedelta(1*365), helper.my_timedelta(2*365)), 'treatment')



class one_year_erection_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.erection_side_effect(), my_data_types.ordered_interval(helper.my_timedelta(0.5*365), helper.my_timedelta(1*365)), 'treatment')



class five_year_erection_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.erection_side_effect(), my_data_types.ordered_interval(helper.my_timedelta(2*365), helper.my_timedelta(5*365)), 'treatment')



class single_ordinal_single_value_wrapper_feature(feature):
    """
    if i have a function that operates on the value part of a single_ordinal_single_value object, this returns a function that will operate on the entire object, and return sosv object with same ordinal
    """
    def __init__(self, f):
        self.f = f

    def _generate(self, x):
        return my_data_types.single_ordinal_single_value_ordered_object(x.get_ordinal(), self.f.generate(x.get_value()))
