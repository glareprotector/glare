import my_exceptions
import my_data_types
import global_stuff

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

    def _generate(self, tumor):
        import helper
        ans = [1 if helper.compare_in(self.backing_feature.generate(tumor), val) else 0 for val in self.get_possible_values()]
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

class single_attribute_feature(feature):
    """
    just returns the specified attribute
    """
    def __init__(self, which_attribute):
        self.which_attribute = which_attribute

    def _generate(self, tumor):
        return tumor.get_attribute(self.which_attribute)


class attribute_categorical_feature(generic_categorical_feature):
    """
    like generic_categorical_feature, except the backing_feature is assumed to just be a single_attribute_feature, so only attribute is specified
    """

    def __init__(self, possible_values, which_attribute, category_descriptions = None):
        backing_feature = single_attribute_feature(which_attribute)
        generic_categorical_feature.__init__(self, possible_values, backing_feature, category_descriptions)



class side_effect_feature(feature):
    """
    has side_effect attribute
    """
    def get_side_effect(self):
        return self.side_effect

    def __init__(self, side_effect):
        self.side_effect = side_effect



class side_effect_excerpt_feature(side_effect_feature):

    def get_negex_irules(self):
        import negex
        f = open(global_stuff.negex_triggers_file, 'r')
        irules = negex.sortRules(f.readlines())
        return irules

    
    # returns 1 if positive(the concept is positive)
    def _generate(self, excerpt):
        anchor = excerpt.anchor
        import helper
        helper.print_if_verbose('\nEXCERPT:', 1.3)
        helper.print_if_verbose(excerpt.raw_text, 1.3)
        helper.print_if_verbose('anchor: ' + anchor, 1.3)


        # check if human input labels are there.  if yes, check for key for this side effect.  if not, depending on value in side effect, 


        for no_info_match in self.get_side_effect().get_no_info_match_features():
            if no_info_match.generate(excerpt, anchor) == True:
                raise my_exceptions.NoFxnValueException(no_info_match.phrase)

        try:
            ans = my_data_types.sv_int(self.get_side_effect().classify_excerpt(excerpt))
        except my_exceptions.NoFxnValueException:
            ans = my_data_types.sv_int(self.basic_classify(excerpt))
        print excerpt
        print "label: ", ans
        import sys
        sys.stdout.flush()
        return ans
        

    def basic_classify(self, excerpt):
        # find out which word is actually in the excerpt
        import negex, helper
        #word, position = helper.get_the_word_and_position(excerpt.raw_text, self.get_side_effect().get_synonyms())
        anchor = excerpt.anchor
        tagger = negex.negTagger(sentence=excerpt.raw_text, phrases=[anchor], rules=self.get_negex_irules(), negP=False)
        helper.print_if_verbose('used NEGEX',1.5)
        if tagger.getNegationFlag() == 'negated':
            return 0
        else:
            return 1





class side_effect_report_record_has_info_feature(side_effect_feature):
    
    def _generate(self, report):
        import my_exceptions
        excerpts = report.get_excerpts_by_side_effect(self.get_side_effect())
        if len(excerpts) == 0:
            return sv_int(0)
        else:
            return sv_int(1)






class report_feature_time_course_feature(feature):

    def _generate(self, tumor_texts, relative_to_diagnosis, date_diagnosed):
        """
        applies report_feature to tumor's reports
        returns single_ordinal_single_value_ordered_object consisting of time and value
        """
        import helper
        ans = my_data_types.single_ordinal_ordinal_list()
        #report_feature = side_effect_report_record_feature_factory.get_feature(self.get_side_effect())
        for report in tumor_texts:
            try:
                temp = self.report_feature.generate(report)
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if relative_to_diagnosis:
                    ans.append(my_data_types.single_ordinal_single_value_ordered_object(helper.my_timedelta((report.date - date_diagnosed).days), temp))
                else:
                    ans.append(my_data_types.single_ordinal_single_value_ordered_object(report.date, temp))
        return ans

    def __init__(self, report_feature):
        self.report_feature = report_feature





class side_effect_time_course_times_only_feature(side_effect_feature):

    def _generate(self, tumor, relative_to_diagnosis):
        """
        returns ordinal_list of times of relevant excerpts
        """
        excerpts = tumor.get_attribute(tumor.texts).get_excerpts_by_side_effect(self.get_side_effect())
        if relative_to_diagnosis == False:
            return excerpts.get_ordinals()
        else:
            return my_data_types.ordinal_list([helper.my_timedelta( (x - tumor.get_attribute(tumor.date_diagnosed)).days) for x in excerpts.get_ordinals()])




class side_effect_intervals_values_f(side_effect_feature):
    """
    given a list of intervals, returns the label of the side effect in that interval as determined by majority, or a NoFxnValueException if no counts there.  return object is a ordinal_list.  refers to side_effect time series of tumor, so have to hard code in the name
    assuming that series stored in tumor are relative to diagnosis, so if want absolute date, have to add in diagnosis date.  if want dates relative to treatment, have to add in treatment_date - diagnosis_date.
    if there was no treatment, return no_value_object for each interval
    """
    def _generate(self, tumor, intervals, relative_to_what):
        import side_effects, global_stuff, features, my_exceptions, my_data_types
        import pdb
        if self.get_side_effect() == side_effects.erection_side_effect:
            series = tumor.get_attribute(global_stuff.get_tumor_cls().erection_time_series)

        import copy
        series_copy = copy.deepcopy(series)
        if relative_to_what == 'absolute':
            for item in series_copy:
                item.set_ordinal(item.get_ordinal() + tumor.get_attribute(global_stuff.get_tumor_cls().date_diagnosed))
        elif relative_to_what == 'diagnosed':
            pass
        elif relative_to_what == 'treatment':
            # if no treatment_date, return sosv list with no_value for all of the values
            treatment_date = features.treatment_date_f().generate(tumor)
            if treatment_date == my_exceptions.NoFxnValueException:
                series = my_data_types.my_list()
            else:
                for item in series_copy:

                    date_diagnosed = tumor.get_attribute(global_stuff.get_tumor_cls().date_diagnosed)
                    treatment_date = features.treatment_date_f().generate(tumor)
                    item_val = item.get_ordinal()
                    #print item_val, treatment_date, date_diagnosed
                    item.set_ordinal(item_val - (treatment_date - date_diagnosed))
        # put the time series into bucket list by intervals
        import my_data_types
        import aggregate_features as af
        bucket_list = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(intervals, series_copy)
        bucket_f = single_ordinal_single_value_wrapper_feature(af.get_bucket_label_feature())
        interval_means = bucket_list.apply_feature_always_add(bucket_f)
        return interval_means

class mean_of_side_effect_intervals_values_f(side_effect_feature):

    def _generate(self, data_set, intervals, relative_to_what):
        import my_data_types, aggregate_features
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(intervals)
        for tumor in data_set:
            interval_labels = side_effect_intervals_values_f(self.get_side_effect()).generate(tumor, intervals, relative_to_what)
            bl.lay_in_matching_ordinal_list(interval_labels)
        meaner = single_ordinal_single_value_wrapper_feature(aggregate_features.get_bucket_mean_feature())
        ans = bl.apply_feature_always_add(meaner)
        return ans


class count_of_side_effect_intervals_values_f(side_effect_feature):

    def _generate(self, data_set, intervals, relative_to_what):

        import my_data_types, aggregate_features
        bl = my_data_types.bucketed_ordinal_list.init_empty_bucket_list_with_specified_ordinals(intervals)
        for tumor in data_set:
            interval_counts = side_effect_intervals_values_f(self.get_side_effect()).generate(tumor, intervals, relative_to_what)
            bl.lay_in_matching_ordinal_list(interval_counts)
        counter = single_ordinal_single_value_wrapper_feature(aggregate_features.get_bucket_count_feature())
        ans = bl.apply_feature_always_add(counter)
        return ans
            

class side_effect_interval_value_f(side_effect_feature):

    def _generate(self, tumor, interval, relative_to_what):
        intervals = [interval]
        return side_effect_intervals_values_f(self.get_side_effect()).generate(tumor, intervals, relative_to_what)[0]




class hard_coded_side_effect_interval_value_f(side_effect_feature):
    """
    returns label value in interval specified in years.  relative to what is also specified
    """
    def __init__(self, side_effect, interval, relative_to_what):
        self.interval = interval
        self.relative_to_what = relative_to_what
        side_effect_feature.__init__(self, side_effect)

    def _generate(self, tumor):
        try:
            return side_effect_interval_value_f(self.get_side_effect()).generate(tumor, self.interval, self.relative_to_what).get_value()
        except my_exceptions.NoFxnValueException:
            return my_data_types.no_value_object()

class two_year_erection_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.erection_side_effect, my_data_types.ordered_interval(helper.my_timedelta(1*365), helper.my_timedelta(2*365)), 'treatment')



class one_year_erection_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.erection_side_effect, my_data_types.ordered_interval(helper.my_timedelta(0.5*365), helper.my_timedelta(1*365)), 'treatment')



class five_year_erection_f(hard_coded_side_effect_interval_value_f):

    def __init__(self):
        import side_effects, helper
        hard_coded_side_effect_interval_value_f.__init__(self, side_effects.erection_side_effect, my_data_types.ordered_interval(helper.my_timedelta(2*365), helper.my_timedelta(5*365)), 'treatment')



class single_ordinal_single_value_wrapper_feature(feature):
    """
    if i have a function that operates on the value part of a single_ordinal_single_value object, this returns a function that will operate on the entire object, and return sosv object with same ordinal
    """
    def __init__(self, f):
        self.f = f

    def _generate(self, x):
        return my_data_types.single_ordinal_single_value_ordered_object(x.get_ordinal(), self.f.generate(x.get_value()))
