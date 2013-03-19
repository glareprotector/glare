import my_exceptions
import my_data_types
import global_stuff
import pdb
from param import param

# import might cause problems
import wc
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
        #x = args[0]
        #if x < lower or x
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
        #if self.backing_feature(tumor) not in self.get_possible_values():
        #    raise Exception

    def _generate(self, *args):
        import helper
        ans = [1 if helper.compare_in(self.backing_feature(*args), val) else 0 for val in self.get_possible_values()]
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
        return self.backing_feature(tumor)

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
        series_copy = copy.deepcopy(report_feature_absolute_time_course_feature()(pid, side_effect))
        if relative_option == 'absolute':
            return series_copy
        elif relative_option == 'treatment':
            treatment_date = features.treatment_date_f()(pid)
            for item in series_copy:
                item.set_ordinal(item.get_ordinal() - treatment_date)
            return series_copy
        elif relative_option == 'diagnosis':
            date_diagnosed = features.date_diagnosed_f()(pid)
            for item in series_copy:
                item.set_ordinal(item.get_ordinal() - date_diagnosed)
            return series_copy
        
class side_effect_intervals_values_f(feature):
    """
    should never raise exception.  return list of NA's if necessary
    label_feature should be undecorated, but i don't think this actually matters
    """
    def _generate(self, pid, side_effect, relative_to_what, intervals, label_feature):
        series = report_feature_time_course_feature_relative()(pid, side_effect, relative_to_what)
        import my_data_types, aggregate_features as af
        bucket_list = my_data_types.bucket_timed_list.init_from_time_intervals_and_timed_list(intervals, series)
        interval_labels = bucket_list.apply_feature_always_add(label_feature)
        return interval_labels

class aggregate_side_effect_intervals_values_f(feature):
    """
    should never raise exception
    """
    def _generate(self, pid_list, side_effect, relative_to_what, intervals, label_feature, aggregate_feature):
        import my_data_types, aggregate_features
        bl = my_data_types.bucket_timed_list.init_empty_bucket_timed_list_with_specified_times(intervals)
        for pid in pid_list:
            interval_labels = side_effect_intervals_values_f()(pid, side_effect, relative_to_what, intervals, label_feature)
            bl.lay_in_matching_ordinal_list(interval_labels)
        meaner = aggregate_features.get_bucket_mean_f()
        ans = bl.apply_feature_always_add(aggregate_feature)
        return ans


class side_effect_interval_value_f(feature):
    """
    should never raise exception
    returns a int or a no_value_object
    """
    def _generate(self, pid, side_effect, relative_to_what, interval, label_feature):
        intervals = [interval]
        ans = side_effect_intervals_values_f()(pid, side_effect, relative_to_what, intervals, label_feature)
        return ans[0]




