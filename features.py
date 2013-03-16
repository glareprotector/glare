import re
import global_stuff
import my_data_types
import my_exceptions
import pdb
import helper

# these imports may have problems
import wc
import objects
from param import param


from global_stuff import get_tumor_cls

from my_data_types import sv_int, sv_float

from basic_features import *


class surgery_code_f(feature):

    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        return tt['MstDefSurgPrimSumm']


class radiation_code_f(feature):

    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        return tt['MstDefRTSumm']

# now, all of these tumor features should just take in pid.  get the database row directly.
class treatment_code_f(feature):

    def _generate(self, pid):
        """
        notes: for surgery, 0 means none, 50 means radical prostectomy.  for radiation, 0 means none, 1 means beam, 2 means brachy
        0 for no treatment
        1 for radical prostectomy
        2 for beam
        3 for brachy
        4 for other
        """

        surgery_code = surgery_code_f().generate(pid)
        radiation_code = radiation_code_f().generate(pid)
        if surgery_code == '00' and radiation_code == '0':
            ans = 0
        elif surgery_code == '50':
            ans = 1
        elif radiation_code == '1':
            ans = 2
        elif radiation_code == '2':
            ans = 3
        else:
            ans = 4
        return ans

class treatment_code_cat_f(generic_categorical_feature):

    def __init__(self):
        possible_values = [[0],[1],[2],[3],[4]]
        backing_feature = treatment_code_f()
        category_descriptions = ['ww','rp','beam','brachy', 'other']
        generic_categorical_feature.__init__(self, possible_values, backing_feature, category_descriptions)

        


class date_diagnosed_f(feature):

    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        return helper.my_date.init_from_num(tt['DateDx'])

class DOB_f(feature):

    def _generate(self, pid):
        sdt = wc.get_stuff(objects.super_db_info, param({'pid':pid}))
        return helper.my_date.init_from_slash_string(sdt['C_DOB'])


class age_at_diagnosis_f(range_checked_feature):
    """
    returns age at diagnosis in years
    """

    def _generate(self, pid):
        ans = (date_diagnosed_f().generate(pid) - DOB_f().generate(pid)).days / 365.0
        if ans < 20:
            import my_data_types
            return my_data_types.no_value_object()
        else:
            return ans

    def __init__(self):
        range_checked_feature.__init__(self, 0.0, 120.0)


class BMI_f(range_checked_feature):
    """
    BMI.  range checked to account for recording error
    """
    def _generate(self, pid):
        p = param({'pid':pid})
        BMI = wc.get_stuff(objects.BMI_w, p)
        return BMI

    def __init__(self):
        range_checked_feature.__init__(self, 1.0, 500.0)

class DLC_f(feature):

    def _generate(self, pid):
        sdt = wc.get_stuff(objects.super_db_info, param({'pid':pid}))
        return helper.my_date.init_from_hyphen_string(sdt['C_DLC'])


# HARDCODED
class age_at_LC_f(range_checked_feature):
    """
    returns age at date of last contact in years
    """
    def _generate(self, pid):
        return (DLC_f().generate(pid) - DOB_f().generate(pid)).days / 365.0

    def __init__(self):
        range_checked_feature.__init__(self, 0.0, 120.0)


# FIX - no more tumor class.  work with extracted row directly
class vital_status_f(feature):
    """
    1 if patient is alive, 0 is dead
    """
    def _generate(self, pid):
        sdt = wc.get_stuff(objects.super_db_info, param({'pid':pid}))
        return sdt['C_Vital']



# refers to other features.  that is fine
class follow_up_time_f(feature):
    """
    a person is followed until end of study or death.  if vital status is 0(dead), then this is DLC - diagnosis date
    if vital status is 1(alive), this is the listed vital status
    returns in units of years
    """
    def _generate(self, pid):
        DLC = DLC_f().generate(pid)
        date_diagnosed = date_diagnosed_f().generate(pid)
        return (DLC - date_diagnosed).days / 365.0

# ideally, when i try to do anything with no value object, it either raises exception or returns no value object
# ideally, no value object you can't do any operations with it
# what is the benefit of having a no_value_object? so that i know 
class surgery_date_f(feature):
    
    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        return helper.my_date.init_from_num(tt['DtMstDefSurg'])

class radiation_date_f(feature):
    
    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        return helper.my_date.init_from_num(tt['MstDefRTDt'])


# now, raise exception instead of returning no_value_object
class treatment_date_f(feature):
    """
    if patient has undergone treatment, this is treatment date.  value is no_value_object otherwise
    does not return a date for brachytherapy - ignoring that for now
    """
    def _generate(self, pid):
        treatment_code = treatment_code_f().generate(pid)
        if treatment_code in [0,4]:
            raise my_exceptions.NoFxnValueException
        elif treatment_code == 1:
            return surgery_date_f().generate(pid)
        elif treatment_code == 2:
            return radiation_date_f().generate(pid)
            

class psa_value_f(range_checked_feature):
    """
    field name: CS_SSFactor1
    psa level
    goes from 1 to 999 in units of 0.1 ng/mL
    available for 3/4 of the 4297
    """
    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        import my_data_types
        try:
            ans = int(tt['CS_SSFactor1'])
        except:
            
            import my_data_types
            ans = my_data_types.no_value_object()
            return ans
        if ans > 970:
            return my_data_types.no_value_object()
        return ans


    def __init__(self):
        range_checked_feature.__init__(self, -0.001, 977.0)












# FIX after i fix basic side effect time course feature
class pre_treatment_side_effect_label_f(feature):
    """
    returns no_value_object if there is no treatment, int otherwise
    """

    def _generate(self, pid, side_effect):
        import helper, my_data_types
        interval = my_data_types.ordered_interval(helper.my_timedelta(-99999), helper.my_timedelta(0))
        import basic_features

        try:
            interval_label = basic_features.side_effect_interval_value_f().generate(pid, side_effect, 'treatment', interval)
        except Exception, e:
            print e
            
        else:
            return interval_label

        """

        try:
            pdb.set_trace()
            interval_label = basic_features.side_effect_interval_value_f().generate(pid, side_effect, 'treatment', interval)
            
        except my_exceptions.NoFxnValueException:


            return my_data_types.no_value_object()

        try:
            ans = interval_label.get_value()
        except my_exceptions.NoFxnValueException:
            return my_data_types.no_value_object()
        else:
            return ans
        """


class grade_f(feature):
    """
    distribution: 1:577(well), 2:7766(moderate), 3:4893(poor)
    """
    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        raw = tt['Grade']
        if raw == '1':
            return 1
        elif raw == '2':
            return 2
        elif raw == '3':
            return 3
        else:
            return my_data_types.no_value_object()


class higher_coverage_stage(feature):
    """
    distribution: 1:1240, 2: ~9000, 3: 2164, 4:1160
    1 and 2 are localized
    http://medical-dictionary.thefreedictionary.com/Prostate+cancer+stages
    """

    def _generate(self, pid):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        raw = tt['BestStage']
        if raw[0] == '1':
            return 1
        elif raw[0] == '2':
            return 2
        elif raw[0] == '3':
            return 3
        elif raw[0] == '4':
            return 4
        else:
            return my_data_types.no_value_object()














# FIX: PSA levels from pathology reports.  didn't work.  might need to extract PSA's eventually though

class psa_series_feature_factor(feature):

    def _generate(self, tumor):
        raw_records = tumor.get_attribute(get_tumor_cls().texts)
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


# FIX: various grade/stages.  figure them out later 

class gleason_primary_f(feature):
    """
    value of 3 4 5 or 9 for NA
    most values are either 3 or 4 (3:1 ratio) but only ~20% of values are known
    """

    def _generate(self, tumor):
        tt = wc.get_stuff(objects.tumor_info, param({'pid':pid}))
        raw = tt['CS_SSFactor5'][2]
        if raw == '3':
            return 3
        elif raw == '4':
            return 4
        elif raw == '5':
            return 5
        else:
            return 9
            



class simple_grade_cat_f(generic_categorical_feature):

    def __init__(self):
        generic_categorical_feature.__init__(self, [[2],[3]], grade_f())


"""
class grade_cat_f(generic_categorical_feature):

    field name: Grade
    http://www.upmccancercenter.com/cancer/prostate/gradingsystems.html 
    refers to physical appearance
    1:21, 2:2305, 3:2225, 4:11, 9:103


    def __init__(self):
        possible_values = [['1'],['2'],['3'],['4'],['9']]
        which_attribute = get_tumor_cls().grade
        attribute_categorical_feature.__init__(self, possible_values, which_attribute)
"""

class SEERStage_mine_f(feature):
    """
    1,2,3,4 for local, regional, distant, NA
    """
    def _generate(self, tumor):
        raw_stage = tumor.get_attribute(get_tumor_cls().SEERSummStage2000)
        #print 'raw_stage', raw_stage
        if raw_stage == '1':
            return 1
        elif raw_stage in ['2','3','4']:
            return 2
        elif raw_stage == '7':
            return 3
        else:
            return 4


class SEERStage_mine_cat_f(generic_categorical_feature):

    def __init__(self):
        generic_categorical_feature.__init__(self, [[1],[2]], SEERStage_mine_f())
        
"""
class SEERStage_f(attribute_categorical_feature):

    field name: SEERSummStage2000
    how far the cancer has spread
    this is a system SEER created themselves, so has less resolution.  more info in TNM staging.
    http://seer.cancer.gov/tools/ssm/malegen.pdf
    same terminology for every site, but terms like regional and distant vary depending on the site

    def __init__(self):
        possible_values = [['1'],['2'],['3'],['4'],['9']]
        which_attribute = get_tumor_cls().SEERSummStage2000
        attribute_categorical_feature.__init__(posible_values, which_attribute)
"""
"""
class BestStage_f(attribute_categorical_feature):
    
    BestStage
    ???
    
    def __init__(self):
        possible_values = [['1'],['2'],['2A'],['2B'],['3'],['4']]
        which_attribute = get_tumor_cls().SEERSummStage2000
        attribute_categorical_feature.__init__(posible_values, which_attribute)

"""
