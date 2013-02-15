import re
import global_stuff
import my_data_types
import my_exceptions
import pdb
import helper
from my_data_types import sv_int, sv_float


class feature(object):
    """
    feature is just a class that takes in a tumor or something, and implements callable
    """
    def generate(self, *args, **kwargs):
        self.error_check(*args, **kwargs)
        return self._generate(*args, **kwargs)

    def error_check(self, *args):
        pass

class side_effect_feature(feature):

    def get_side_effect(self):
        return self.side_effect

    def __init__(self, side_effect):
        self.side_effect = side_effect

class feature_factory(object):
    """
    features are objects with a generate function.  feature factories generate instances of features
    """
    @classmethod
    def get_feature(cls):
        pass


class side_effect_excerpt_feature(side_effect_feature):

    def get_negex_irules(self):
        import negex
        f = open(global_stuff.negex_triggers_file, 'r')
        irules = negex.sortRules(f.readlines())
        return irules

    
    # returns 1 if positive(the concept is positive)
    def _generate(self, excerpt):
        anchor = excerpt.anchor
        helper.print_if_verbose('\nEXCERPT:', 1.3)
        helper.print_if_verbose(excerpt.raw_text, 1.3)
        helper.print_if_verbose('anchor: ' + anchor, 1.3)
        for no_info_match in self.get_side_effect().get_no_info_match_features():
            if no_info_match.generate(excerpt, anchor) == True:
                raise my_exceptions.NoFxnValueException

        try:
            return helper.sv_int(self.get_side_effect().classify_excerpt(excerpt))
        except my_exceptions.NoFxnValueException:
            return sv_int(self.basic_classify(excerpt))

    def basic_classify(self, excerpt):
        # find out which word is actually in the excerpt
        import negex
        #word, position = helper.get_the_word_and_position(excerpt.raw_text, self.get_side_effect().get_synonyms())
        anchor = excerpt.anchor
        tagger = negex.negTagger(sentence=excerpt.raw_text, phrases=[anchor], rules=self.get_negex_irules(), negP=False)
        helper.print_if_verbose('used NEGEX',1.5)
        if tagger.getNegationFlag() == 'negated':
            return 0
        else:
            return 1


class side_effect_excerpt_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, side_effect):
        return side_effect_excerpt_feature(side_effect)


class side_effect_report_record_feature(side_effect_feature):

    def _generate(self, report):

        side_effect_excerpts = report.get_excerpts_by_side_effect(self.get_side_effect())
        excerpt_scores = side_effect_excerpts.apply_feature(side_effect_excerpt_feature_factory.get_feature(self.get_side_effect()), my_data_types.my_list)
        
        if len(excerpt_scores) == 0:
            raise my_exceptions.NoFxnValueException

        total = sv_float(0.0)
        count = sv_int(0)
        for score in excerpt_scores:
            try:
                total += score
            except:
                pass
            else:
                count += 1

        if total > count / 2.0:
            return sv_int(1)
        else:
            return sv_int(0)


class side_effect_report_record_feature_factory(feature_factory):
    
    @classmethod
    def get_feature(cls, side_effect):
        return side_effect_report_record_feature(side_effect)


class report_feature_time_course_feature(feature):

    def _generate(self, tumor_texts, relative_to_diagnosis, date_diagnosed):
        """
        applies report_feature to tumor's reports
        returns single_ordinal_single_value_ordered_object consisting of time and value
        """

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




class report_feature_time_course_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, report_feature):
        return report_feature_time_course_feature(report_feature)






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


class side_effect_time_course_times_only_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, side_effect):
        return side_effect_time_course_times_only_feature(side_effect)





class apply_feature_to_buckets_from_series_feature(feature):
    """
    specify the ordinal_list feature, specify feature that will act on collections
    """
    def _generate(self, series, intervals, *args):
        #series = self.feature.generate(tumor, args)
        bl = my_data_types.bucketed_ordinal_list.init_from_intervals_and_ordinal_list(intervals, series)
        return bl.apply_feature_always_add(self.bucket_feature)


    def __init__(self, collection_feature):
        """
        takes in collection_feature instance that operates on a collection, not on a bucket
        """
        self.bucket_feature = single_ordinal_single_value_wrapper_feature_factory.get_feature(collection_feature)

        

class generic_apply_feature_to_buckets_from_series_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, collection_feature):
        return generic_apply_feature_to_buckets_from_series_feature(collection_feature)





class get_bucket_mean_feature(feature):
    """
    only assumes that bucket is iterable, and items have implement the base_single_ordinal_single_value_ordered_object
    """
    def _generate(self, bucket):
        total = 0.0
        count = 0
        for item in bucket:
            try:
                total += item.get_value()
                count += 1
            except my_exceptions.NoFxnValueException:
                # if there is no value, get_value will raise exception
                pass
        if count == 0:
            return my_data_types.no_value_object()
        else:
            return sv_float(total / float(count))


class get_bucket_sum_feature(feature):
    """
    only assumes that bucket is iterable, and items have implement the base_single_ordinal_single_value_ordered_object
    """
    def _generate(self, bucket):
        total = 0.0
        for item in bucket:
            try:
                total += item.get_value()
            except my_exceptions.NoFxnValueException:
                # if there is no value, get_value will raise exception
                pass
        return sv_float(total)



class get_bucket_max_feature(feature):

    def _generate(self, bucket):
        max_so_far = None
        ans = my_data_types.no_value_object()
        for item in bucket:
            try:
                val = item.get_ordinal()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if max_so_far == None:
                    max_so_far = val
                    ans = item
                elif val > max_so_far:
                    max_so_far = val
                    ans = item
        return ans


class get_bucket_min_feature(feature):

    def _generate(self, bucket):
        min_so_far = None
        ans = my_data_types.no_value_object()
        for item in bucket:
            try:
                val = item.get_ordinal()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if min_so_far == None:
                    min_so_far = val
                    ans = item
                elif val < min_so_far:
                    min_so_far = val
                    ans = item
        return ans


class get_bucket_count_feature(feature):

    def _generate(self, bucket):
        count = 0

        for item in bucket:
            try:
                item.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                count += 1
        return sv_int(count)




class get_bucket_count_nonzero_feature(feature):

    def _generate(self, bucket):
        count = 0

        for item in bucket:
            try:
                item.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                count += 1
        if count > 0:
            return sv_int(1)
        else:
            return sv_int(0)



class get_bucket_label_feature(feature):

    def _generate(self, bucket):
        num_0 = 0
        num_1 = 0
        for item in bucket:
            try:
                val = item.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if val == 0:
                    num_0 += 1
                else:
                    num_1 += 1
        if num_0 + num_1 == 0:
            return my_data_types.no_value_object()
        if num_1 > num_0:
            return sv_int(1)
        else:
            return sv_int(0)






class single_ordinal_single_value_wrapper_feature(feature):
    """
    if i have a function that operates on the value part of a single_ordinal_single_value object, this returns a function that will operate on the entire object, and return sosv object with same ordinal
    """
    def __init__(self, f):
        self.f = f

    def _generate(self, x):
        return my_data_types.single_ordinal_single_value_ordered_object(x.get_ordinal(), self.f.generate(x.get_value()))


class single_ordinal_single_value_wrapper_feature_factory(feature_factory):
    """
    takes in feature instance
    """
    @classmethod
    def get_feature(cls, f):
        return single_ordinal_single_value_wrapper_feature(f)





# takes in tumor instances, and returns a vector corresponding to the feature.  may be longer than 1 for categorical features
class single_attribute_feature(feature):

    def get_which_attribute(self):
        return self.which_attribute

class scalar_feature(single_attribute_feature):

    def error_check(self, tumor):
        lower, upper = self.get_valid_range()
        if self.get_code(tumor) < lower or self.get_code(tumor) > upper:
            raise my_exceptions.ScalarFeatureOutOfRange

    def _generate(self, tumor):
        return [tumor.get_attribute(self.get_which_attribute())]

    def get_valid_range(self):
        return self.low, self.high

    def __init__(self, which_attribute, low, high):
        self.which_attribute = which_attribute
        self.low = low
        self.high = high

class scalar_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, which_attribute, low, high):
        return scalar_feature(which_attribute, low, high)

class hard_coded_scalar_feature_factory(scalar_feature_factory):

    @classmethod
    def get_which_attribute(cls):
        pass

    @classmethod
    def get_valid_range(cls):
        pass

    @classmethod
    def get_feature(cls):
        low, high = cls.get_valid_range()
        return scalar_feature(cls.get_which_attribute(), low, high)



    


class complex_categorical_feature(feature):

    def error_check(self, tumor):
        if self.get_code(tumor) not in self.get_possible_values():
            raise Exception

    def get_code(self, tumor):
        return (self.get_code_f)(tumor)

    def _generate(self, tumor):
        ans = [1 if helper.compare_in(self.get_code(tumor), val) else 0 for val in self.get_possible_values()]
        return ans

    def get_possible_values(self):
        return self.possible_values

    def __init__(self, possible_values, get_code_f):
        self.possible_values = possible_values
        self.get_code_f = get_code_f

class complex_categorical_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, possible_values, get_code_f):
        return complex_categorical_feature(possible_values, get_code_f)



class hard_coded_complex_categorical_feature_factory(feature_factory):

    @classmethod
    def get_which_attribute(cls):
        pass

    @classmethod
    def get_possible_values(cls):
        pass

    @classmethod
    def get_feature(cls):
        return complex_categorical_feature_factory.get_feature(cls.get_possible_values(), cls.get_code_f)


class treatment_code_feature_factory(hard_coded_complex_categorical_feature_factory):

    @staticmethod
    def get_code_f(tumor):
        """
        notes: for surgery, 0 means none, 50 means radical prostectomy.  for radiation, 0 means none, 1 means beam, 2 means brachy
        0 for no treatment
        1 for radical prostectomy
        2 for beam
        3 for brachy
        """
        surgery_code = tumor.get_attribute(tumor.surgery_code)
        radiation_code = tumor.get_attribute(tumor.radiation_code)
        if surgery_code == '00' and radiation_code == '0':
            return 0
        elif surgery_code == '50':
            return 1
        elif radiation_code == '1':
            return 2
        elif radiation_code == '2':
            return 3
        else:
            return 4
    
    @classmethod
    def get_possible_values(cls):
        return [[0],[1],[2],[3],[4]]

class categorical_feature(complex_categorical_feature):

    def get_which_attribute(self):
        return self.which_attribute

    def get_code(tumor):
        return tumor.get_attribute(self.get_which_attribute())

    def __init__(self, which_attribute, possible_values):
        self.which_attribute = which_attribute
        complex_categorical_feature.__init__(possible_values, categorical_feature.get_code)

class binner(object):

    def get_bin_number(self, tumor):
        pass

    def get_bin_descriptions(self):
        pass

    def get_num_bins(self):
        pass

class binner_factory(object):

    pass


class categorical_feature_binner(binner):

    def get_bin_number(self, tumor):
        feat = self.feature.generate(tumor)
        i = 0
        for i in range(len(feat)):
            if i != 0:
                return i
        raise 

    def get_bin_descriptions(self):
        return self.bin_descriptions

    def get_num_bins(self):
        return len(self.feature.get_possible_values())

    def __init__(self, feature, bin_descriptions):
        self.bin_descriptions = bin_descriptions
        self.feature = feature

class scalar_feature_binner(binner):

    def get_bin_intervals(self):
        return self.bin_intervals

    def get_num_bins(self):
        return len(self.get_bin_intervals())

    def get_bin_number(self, tumor):
        feat = self.feature.generate(tumor)
        for i in range(self.get_num_bins()):
            interval = self.get_bin_intervals()[i]
            if interval.contains(feat):
                return i
        raise

    def get_bin_descriptions(self):
        return self.bin_descriptions

    def __init__(self, feature, bin_intervals, bin_descriptions):
        self.feature = feature
        self.bin_intervals = bin_intervals
        self.bin_descriptions = bin_descriptions


class scalar_feature_binner_factory(binner_factory):

    @classmethod
    def get_binner(cls, feature, bin_intervals, bin_descriptions):
        return scalar_feature_binner(feature, bin_intervals, bin_descriptions)



class categorical_feature_binner_factory(feature_factory):

    @classmethod
    def get_binner(cls, feature, bin_descriptions):
        return categorical_feature_binner(feature, bin_descriptions)



class categorical_feature_factory(feature_factory):

    @classmethod
    def get_feature(cls, which_attribute, possible_values):
        return categorical_feature(which_attribute, possible_values)


class text_label(feature):

    def get_words_to_search_for(self):
        return self.which_words

    def _generate(self, tumor):
        texts = tumor.get_attribute(tumor.texts)
        assert len(texts) > 0
        present = False
        for text in texts:
            for word in self.get_words_to_search_for():
                if word.lower() in text.lower():
                    present = True
        
        if present:
            return [1]
        else:
            return [0]


class erectile_text_label_f(feature):
    """
    1 means you have erectile dysfunction
    """
    def _generate(self, tumor):
        counts = tumor.get_attribute(tumor.erection_negation_counts)
        erection = counts['erection']
        erections = counts['erections']
        eds = counts['erectile dysfunction']
        support = erection[0] + erections[0] + (eds[1]-eds[0])
        against = (erection[1]-erection[0]) + (erections[1]-erections[0]) + eds[0]
        if support + against == 0:
            raise Exception
        return [int(support > against)]

class hard_coded_categorical_feature_factory(feature_factory):

    @classmethod
    def get_which_attribute(cls):
        pass

    @classmethod
    def get_possible_values(cls):
        pass

    @classmethod
    def get_feature(cls):
        return categorical_feature_factory.get_feature(self.get_which_attribute(), self.get_possible_values())


class gleason_primary_feature_factory(hard_coded_categorical_feature_factory):
    """
    primary and secondary come from CS_SSFactor5, which codes both primary and secondary gleason scores
    might be the same as grade_f, not sure
    """

    @classmethod
    def get_which_attribute(cls):
        return tumor.gleason_primary

    @classmethod
    def get_possible_values(cls):
        return [['3'],['4'],['5'],['8','9']]


class gleason_secondary(hard_coded_categorical_feature_factory):

    @classmethod
    def get_which_attribute(cls):
        return tumor.gleason_secondary

    @classmethod
    def get_possible_values(cls):
        return [['3'],['4'],['5'],['8','9']]

class prev_psa_level_f(hard_coded_categorical_feature_factory):

    @classmethod
    def get_which_attribute(cls):
        return tumor.prev_psa_level

    @classmethod
    def get_possible_values(cls):
        return [['000'], ['010'], ['030'], ['999']]

class psa_value_feature_factory(hard_coded_scalar_feature_factory):
    """
    field name: CS_SSFactor1
    psa level
    goes from 1 to 999 in units of 0.1 ng/mL
    """

    @classmethod
    def get_which_attribute(cls):
        return tumor.psa_level

    @classmethod
    def get_valid_range(cls):
        return 1, 989


class grade_f(categorical_feature_factory):
    """
    field name: Grade
    http://www.upmccancercenter.com/cancer/prostate/gradingsystems.html 
    refers to physical appearance
    1:21, 2:2305, 3:2225, 4:11, 9:103
    """

    @classmethod
    def get_possible_values(cls):
        return [['1'],['2'],['3'],['4'],['9']]

    @classmethod
    def get_which_attribute(cls):
        return tumor.grade

class SEERStage_f(categorical_feature_factory):
    """
    field name: SEERSummStage2000
    how far the cancer has spread
    http://seer.cancer.gov/tools/ssm/malegen.pdf
    same terminology for every site, but terms like regional and distant vary depending on the site
    """
    @classmethod
    def get_possible_values(cls):
        return [['1'],['2'],['3'],['4'],['9']]

    @classmethod
    def get_which_attribute(cls):
        return tumor.SEERSummStage2000

class BestStage_f(categorical_feature_factory):
    """
    BestStage
    ???
    """
    @classmethod
    def get_possible_values(cls):
        return [['1'],['2'],['2A'],['2B'],['3'],['4']]

    @classmethod
    def get_which_attribute(cls):
        return tumor.SEERSummStage2000

class psa_series_feature_factor(feature):

    def _generate(self, tumor):
        raw_records = tumor.get_attribute(tumor.texts)
        psa_filtered_records = raw_records.filter_excerpt_by_word('psa')
        import re
        #num_searcher = re.compile('\s\d{1,2}(\.\d+)+\s')
        num_searcher = re.compile('\s\d{1,2}(\.\d+)*')

        psa_searcher = re.compile('psa')
        ans = []
        seen_dates = set()
        for record in psa_filtered_records:
            raw_text = record.raw_text.lower()
            psa_positions = [m.start() for m in psa_searcher.finditer(raw_text)]
            closest = None
            best_val = None
            window_size = 30
            for psa_pos in psa_positions:
                right_matches = [m for m in num_searcher.finditer(raw_text, psa_pos, min(psa_pos + window_size, len(raw_text)))]
               
                if len(right_matches) > 0:
                    dist = right_matches[0].start() - psa_pos
                    if closest == None or dist < closest:
                        try:
                            best_val = float(right_matches[0].group())
                        except:
                            pass
                        else:
                            closest = dist
                        
                left_matches = [m for m in num_searcher.finditer(raw_text, max(psa_pos - window_size, 0), psa_pos)]
                if len(left_matches) > 0:
                    dist = psa_pos = left_matches[-1].start()
                    if closest == None or dist < closest:
                        try:
                            best_val = float(left_matches[-1].group())
                        except:
                            pass
                        else:
                            closest = dist

            if best_val != None:
                if record.date not in seen_dates:
                    ans.append([record.date, best_val])
                    seen_dates.add(record.date)
        ans.sort(key = lambda x: x[0])
        return ans
