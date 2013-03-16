import wrapper
from wrapper_decorator import dec
import wrapper
import param
import global_stuff
import helper
import pdb
import features
import side_effects
import sys
import basic_features

class PID_to_MRN_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        query = 'select PatientId, MedRecNo from [TR_MASTER.registry].[dbo].[MGH pts]'
        cursor = helper.get_cursor()
        cursor.execute(query)
        PID_to_MRN = {}
        for row in cursor:
            PID_to_MRN[row.PatientId] = row.MedRecNo
        return PID_to_MRN


class PID_with_shared_MRN(wrapper.vect_int_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):

        MRN_to_PID = self.get_var_or_file(MRN_to_PID_dict, params)
        ans = set()
        for MRN in MRN_to_PID:
            if len(MRN_to_PID[MRN]) > 1:
                for PID in MRN_to_PID[MRN]:
                    ans.add(PID)
        return list(ans)

class PID_with_SS_info(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        query = 'select PatientID from [TR_MASTER.registry].[dbo].[mgh_tumor] where PrimarySite=\'C619\' and CS_SSFactor1!=\'\'' + ' and CS_SSFactor1 is not NULL'
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = []
        for row in cursor:
            ans.append(row.PatientID)
        return ans


class prostate_PID(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        query = 'select PatientID, DateDx from [TR_MASTER.registry].[dbo].[mgh_tumor] where PrimarySite=\'C619\''
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = []
        num_ok = 0
        num_total = 0
        for row in cursor:
            try:
                date_dx = helper.my_date.init_from_num(row.DateDx)
                num_ok += 1
                #if date_dx.year < 1995 and date_dx.year >= 1992:
                ans.append(row.PatientID)
            except Exception, e:
                print e
                #pdb.set_trace()
            num_total += 1
            #print num_ok, num_total
        return ans





class MRN_to_PID_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        # 2 different PIDs could have the same MRN, so a MRN could map to 2 PIDs.  ignore the PIDs for which this is the case for now
        query = 'select PatientId, MedRecNo from [TR_MASTER.registry].[dbo].[MGH pts]'
        cursor = helper.get_cursor()
        cursor.execute(query)
        MRN_to_PID = {}
        for row in cursor:
            try:
                MRN_to_PID[row.MedRecNo].append(row.PatientId)
            except:
                MRN_to_PID[row.MedRecNo] = [row.PatientId]
        return MRN_to_PID

class PID_to_TID_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        query = 'select TumorID, PatientID from [TR_MASTER.registry].[dbo].[mgh_tumor]'
        cursor = helper.get_cursor()
        cursor.execute(query)
        PID_to_TID = {}
        for row in cursor:
            try:
                PID_to_TID[row.PatientID].append(row.TumorID)
            except:
                PID_to_TID[row.PatientID] = [row.TumorID]
        return PID_to_TID

class TID_to_PID_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        query = 'select TumorID, PatientID from [TR_MASTER.registry].[dbo].[mgh_tumor]'
        cursor = helper.get_cursor()
        cursor.execute(query)
        TID_to_PID = {}
        for row in cursor:
            TID_to_PID[row.TumorID] = row.PatientID
        return TID_to_PID

class PID_with_multiple_tumors(wrapper.vect_int_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        PID_to_TID = self.get_var_or_file(PID_to_TID_dict, params)
        ans = []
        for PID in PID_to_TID:
            if len(PID_to_TID[PID]) > 1:
                ans.append(PID)
        return ans

class tumor_info(wrapper.obj_wrapper, wrapper.by_pid_wrapper):


    def get_max_cache_size(self):
        return 17000

    def get_to_pickle(self):
        return True

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):

        pid = self.get_param(params, 'pid')
        query = 'select * from [TR_MASTER.registry].[dbo].[mgh_tumor] where PatientID=' + str(pid)
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = cursor.fetchall()

        assert(len(ans) == 1)
        ans = helper.row_to_dict(ans[0])
        return ans

class patient_info(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def get_max_cache_size(self):
        return 17000

    def get_to_pickle(self):
        return True

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pid = self.get_param(params, 'pid')
        import wc
        PID_to_MRN = wc.get_stuff(PID_to_MRN_dict, params)
        mrn = PID_to_MRN[pid]
        query = 'select * from [RPDR].[dbo].[Demographics] where MRN=' + str(mrn)
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = cursor.fetchall()

        assert(len(ans) == 1)
        return helper.row_to_dict(ans[0])

class super_db_info(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def get_max_cache_size(self):
        return 17000

    def get_to_pickle(self):
        return True

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pid = self.get_param(params, 'pid')
        query = 'select * from [SDB].[dbo].[Tum_Core] where PatientID=' + str(pid)
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = cursor.fetchall()

        assert(len(ans) == 1)
        ans = helper.row_to_dict(ans[0])
        return ans


class raw_medical_text(wrapper.vect_string_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pid = self.get_param(params, 'pid')
        map = self.get_var_or_file(PID_to_MRN_dict,params)

        Mrn = map[pid]
        query = 'select Comments from [RPDR].[dbo].[LMRNote] where MRN=' + str(MRN)
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = []
        i = 0
        for row in cursor:
            ans.append(row.Comments)

                
        return ans



class raw_pathology_text(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @classmethod
    def get_to_filelize(cls):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pdb.set_trace()
        pid = self.get_param(params, 'pid')
        ans = helper.record_list()
        MRN = helper.PID_to_MRN(pid)
        query = 'select Report_Date_Time, Report_Text, Report_Desc from [RPDR].[dbo].[PathReport] where MRN=' + str(MRN)
        #query = 'select Report_Date_Time, Report_Text from [RPDR].[dbo].[PathReport] where MRN=' + str(MRN)
        cursor = helper.get_cursor()
        cursor.execute(query)
        idx = 0
        for row in cursor:
            date_str = row.Report_Date_Time.split()[0]
            from helper import my_date
            date = my_date.init_from_str(date_str)
            raw_text = row.Report_Text
            
            temp = helper.report_record(pid, date, raw_text, idx)
            ans.append(temp)
            idx += 1
        ans.sort()
        return ans

class raw_radiology_text(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @classmethod
    def get_to_filelize(cls):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pid = self.get_param(params, 'pid')
        ans = helper.record_list()
        MRN = helper.PID_to_MRN(pid)
        query = 'select Report_Date_Time, Report_Text, Report_Desc from [RPDR].[dbo].[RadiologyReport] where MRN=' + str(MRN)
        #query = 'select Report_Date_Time, Report_Text from [RPDR].[dbo].[PathReport] where MRN=' + str(MRN)
        cursor = helper.get_cursor()
        cursor.execute(query)
        idx = 0
        for row in cursor:
            date_str = row.Report_Date_Time.split()[0]
            from helper import my_date
            date = my_date.init_from_str(date_str)
            raw_text = row.Report_Text
            
            temp = helper.report_record(pid, date, raw_text, idx)
            ans.append(temp)
            idx += 1
        ans.sort()
        return ans

class raw_operative_text(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @classmethod
    def get_to_filelize(cls):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pid = self.get_param(params, 'pid')
        ans = helper.record_list()
        MRN = helper.PID_to_MRN(pid)
        query = 'select Report_Date_Time, Report_Text from [RPDR].[dbo].[OperativeReport] where MRN=' + str(MRN)
        #query = 'select Report_Date_Time, Report_Text from [RPDR].[dbo].[PathReport] where MRN=' + str(MRN)
        cursor = helper.get_cursor()
        cursor.execute(query)
        idx = 0
        for row in cursor:
            date_str = row.Report_Date_Time.split()[0]
            from helper import my_date
            date = my_date.init_from_str(date_str)
            raw_text = row.Report_Text
            
            temp = helper.report_record(pid, date, raw_text, idx)
            ans.append(temp)
            
            idx += 1
        ans.sort()
        return ans





class raw_medical_text_new(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @classmethod
    def get_to_filelize(cls):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pid = self.get_param(params, 'pid')
        ans = helper.record_list()
        MRN = helper.PID_to_MRN(pid)
        query = 'select LMRNote_Date_Time, Comments from [RPDR].[dbo].[LMRNote] where MRN=' + str(MRN)
        #query = 'select Report_Date_Time, Report_Text from [RPDR].[dbo].[PathReport] where MRN=' + str(MRN)
        cursor = helper.get_cursor()
        cursor.execute(query)
        idx = 0
        for row in cursor:
            date_str = row.LMRNote_Date_Time.split()[0]
            from helper import my_date
            date = my_date.init_from_str(date_str)
            raw_text = row.Comments
            
            temp = helper.report_record(pid, date, raw_text, idx)
            ans.append(temp)
            
            idx += 1
        ans.sort()
        return ans

            

# returns raw medical texts but only sentences containing at list one of words in filter_words list
class filtered_sents(wrapper.vect_string_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return True

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['filter_words']) | raw_medical_text.get_all_keys(params, self)

    # compound words joined by +, separate words joined by &
    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):

        coded_words = self.get_param(params, 'filter_words')
        words = helper.coded_words_to_words(coded_words)
        ans = []
        raw_text = self.get_var_or_file(raw_medical_text, params)
        for line in raw_text:
            for sentence in line.split('.'):
                actual = sentence.lstrip().strip().lower()
                ok = False
                for word in words:
                    if word in actual.split(' '):
                        ok = True
                        break
                if ok:
                    ans.append(actual)
        return ans


class negation_counts(wrapper.obj_wrapper, wrapper.by_pid_wrapper):
    """
    for each word, has dictionary for how many times out of how many it is negated
    """

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return (set(['count_words']) | raw_medical_text.get_all_keys(params, self)) - set(['count_words'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        coded_words = self.get_param(params, 'count_words')
        words = helper.coded_words_to_words(coded_words)

        ans = {}
        import negex
        f = open(global_stuff.negex_triggers_file, 'r')
        irules = negex.sortRules(f.readlines())
        for word in words:
            total = 0
            negated = 0
            self.set_param(params, 'filter_words', helper.words_to_coded_words([word]))
            sents = self.get_var_or_file(filtered_sents, params)
            for sent in sents:
                tagger = negex.negTagger(sentence=sent, phrases=[word], rules = irules, negP = False)
                print  tagger.getNegationFlag(), word, sent
                if tagger.getNegationFlag() == 'negated':
                    negated += 1
                total += 1
            ans[word] = [negated, total]
        return ans



class side_effect_human_input_report_labels(wrapper.obj_wrapper, wrapper.by_pid_wrapper):


    @classmethod
    def get_all_keys(cls, params, self=None):
        return raw_medical_text.get_all_keys(params, self) | set(['rec_idx'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):

        # retrieve the record.  need pid and record index
        record_list = self.get_var_or_file(raw_medical_text_new, params)
        report_record = record_list[self.get_param(params, 'rec_idx')]


        # print entire record
        print report_record

        # display relevant excerpts

        for side_effect in global_stuff.get_side_effects_to_display():
            for excerpt in report_record.get_excerpts_to_display_by_side_effect(side_effect):
                print '________________'
                print excerpt
                print '________________'




        ans = {}
        

        # now print and read in response for the questions to query
        for question in global_stuff.get_questions_to_query():
            response = question.get_user_answer()
            ans[question] = response

        return ans
        
class bowel_urgency_time_series(wrapper.obj_wrapper, wrapper.by_pid_wrapper):


    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid', 'reltd'])

    def whether_to_override(self, object_key):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        tt = self.get_var_or_file(tumor_info, params)
        tumor_texts = self.get_var_or_file(raw_medical_text_new, params)
        diagnosis_date = helper.my_date.init_from_num(tt['DateDx'])
        relative_to_diagnosis = self.get_param(params, 'reltd')
        #return features.report_feature_time_course_feature(features.side_effect_report_record_feature(side_effects.erection_side_effect())).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)
        return basic_features.report_feature_time_course_feature(side_effects.bowel_urgency_bin()).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)









class side_effect_time_series(wrapper.obj_wrapper, wrapper.by_pid_wrapper):


    def get_max_cache_size(self):
        return 17000

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid', 'side_effect'])

    def whether_to_override(self, object_key):
        return False


    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):

        tumor_texts = self.get_var_or_file(raw_medical_text_new, params)
        import my_data_types, my_exceptions
        ans = my_data_types.single_ordinal_ordinal_list()
        side_effect_feature = self.get_param(params, 'side_effect')

        count = 0
        for report in tumor_texts:
            #print count
            try:
                temp = side_effect_feature.generate(report)
            except my_exceptions.NoFxnValueException:
                pass
            else:
                ans.append(my_data_types.single_ordinal_single_value_ordered_object(report.date, temp))
            count += 1
            #print ans
        return ans


class BMI_w(wrapper.obj_wrapper, wrapper.by_pid_wrapper):


    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    def whether_to_override(self, object_key):
        return False

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        P_to_M = self.get_var_or_file(PID_to_MRN_dict, params)
        MRN = P_to_M[self.get_param(params,'pid')]
        import my_data_types, my_exceptions
        try:
            tt = self.get_var_or_file(tumor_info, params)
            treatment_date = helper.my_date.init_from_num(tt['DateDx'])
        except Exception, error:

            print error
            return my_data_types.no_value_object()
            
        # find all the height rows corresponding to height and the MRN, keep one closest to diagnosis date
        closest_height_datediff = 9999999
        closest_height = None
        query = 'SELECT MRN, LMR_Vital_Date_Time, Result, Units from [RPDR].[dbo].[LMRVital] where LMR_Text_Type in (\'HEIGHT\',\'HT.\') and MRN=' + '\'' + MRN + '\''
        cursor = helper.get_cursor()
        cursor.execute(query)
        for row in cursor:
            try:
                if row.Units == 'Centimeters':
                    meter_height = float(row.Result) / 100.0
                    #print 'centimeters', row.Result
                elif row.Units == 'Inches':
                    meter_height = float(row.Result) / 39.37
                    #print 'inches', row.Result
                else:
                    raise my_exceptions.NoFxnValueException
            except my_exceptions.NoFxnValueException:
                pass
            except Exception:
                pass
            else:
                try:
                    height_date_str = row.LMR_Vital_Date_Time.split()[0].strip()
                    height_date = helper.my_date.init_from_slash_string(height_date_str)
                    datediff = abs((height_date - treatment_date).days)
                    if datediff < closest_height_datediff:
                        closest_height = meter_height
                        closest_height_datediff = datediff
                except:
                    pass

        # now do the exact same for weight rows.  weights come in Kilograms and Pounds.  need to convert to Kilograms
        closest_weight_datediff = 9999999
        closest_weight = None
        query = 'SELECT MRN, LMR_Vital_Date_Time, Result, Units from [RPDR].[dbo].[LMRVital] where LMR_Text_Type=\'WEIGHT\' and MRN=' + '\'' + MRN + '\''
        cursor = helper.get_cursor()
        cursor.execute(query)
        for row in cursor:
            try:
                if row.Units == 'Kilograms':
                    #print 'kilogram', row.Result
                    kg_weight = float(row.Result)
                elif row.Units == 'Pounds':
                    #print 'pounds', row.Result
                    kg_weight = float(row.Result) / 2.204
                else:
                    raise my_exceptions.NoFxnValueException
            except my_exceptions.NoFxnValueException:
                pass
            except Exception:
                pass
            else:
                try:
                    weight_date_str = row.LMR_Vital_Date_Time.split()[0].strip()
                    weight_date = helper.my_date.init_from_slash_string(weight_date_str)
                    datediff = abs((weight_date - treatment_date).days)
                    if datediff < closest_weight_datediff:
                        closest_weight = kg_weight
                        closest_weight_datediff = datediff
                except:
                    pass

        # do the actual calculation
        if closest_height != None and closest_weight != None:
            try:
                return closest_weight / (closest_height * closest_height)
            except:
                return my_data_types.no_value_object()
        else:
            return my_data_types.no_value_object()




class erection_time_series(wrapper.obj_wrapper, wrapper.by_pid_wrapper):
    

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid', 'reltd'])

    def whether_to_override(self, object_key):
        return False

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        tt = self.get_var_or_file(tumor_info, params)
        tumor_texts = self.get_var_or_file(raw_medical_text_new, params)
        diagnosis_date = helper.my_date.init_from_num(tt['DateDx'])
        relative_to_diagnosis = self.get_param(params, 'reltd')
        #return features.report_feature_time_course_feature(features.side_effect_report_record_feature(side_effects.erection_side_effect())).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)
        return basic_features.report_feature_time_course_feature(side_effects.erection_side_effect()).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)



class incontinence_time_series(wrapper.obj_wrapper, wrapper.by_pid_wrapper):
    

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid', 'reltd'])

    def whether_to_override(self, object_key):
        return False

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        tt = self.get_var_or_file(tumor_info, params)
        tumor_texts = self.get_var_or_file(raw_medical_text_new, params)
        diagnosis_date = helper.my_date.init_from_num(tt['DateDx'])
        relative_to_diagnosis = self.get_param(params, 'reltd')
        #return features.report_feature_time_course_feature(features.side_effect_report_record_feature(side_effects.erection_side_effect())).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)
        ans = features.report_feature_time_course_feature(side_effects.urin_incont_bin()).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)
        return ans


class tumor_w(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid']) | erection_time_series.get_all_keys(params, self)

    def whether_to_override(self, object_key):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        # obtains info related to a tumor.  puts it into a tumor instance and returns it

        tt = self.get_var_or_file(tumor_info, params)
        pt = self.get_var_or_file(patient_info, params)
        sdt = self.get_var_or_file(super_db_info, params)
        texts = self.get_var_or_file(raw_medical_text_new, params)
        #self.set_param(params, 'count_words', helper.words_to_coded_words(['erection','erections','erectile dysfunction']))
        #erection_negation_counts = self.get_var_or_file(negation_counts, params)
        pid = self.get_param(params, 'pid')
        pdb.set_trace()
        #gleason_primary = tt['CS_SSFactor5'][2]
        #gleason_secondary = tt['CS_SSFactor5'][3]
        
        ets = self.get_var_or_file(erection_time_series, params)
        uts = self.get_var_or_file(incontinence_time_series, params)
        buts = self.get_var_or_file(bowel_urgency_time_series, params)

        #ets = None
        #uts = None
        #buts = None


        #print buts

        alive_or_not = sdt['C_Vital']
        date_last_contact = helper.my_date.init_from_hyphen_string(sdt['C_DLC'])
        dob = helper.my_date.init_from_slash_string(sdt['C_DOB'])

        return helper.tumor(_pid = pid, _grade = tt['Grade'], _SEERSummStage = tt['SEERSummStage2000'] , _BestStage = tt['BestStage'], _surgery_code = tt['MstDefSurgPrimSumm'], _radiation_code = tt['MstDefRTSumm'], _date_diagnosed = helper.my_date.init_from_num(tt['DateDx']), _surgery_date = helper.my_date.init_from_num(tt['DtMstDefSurg']), _radiation_date = helper.my_date.init_from_num(tt['MstDefRTDt']), _erection_time_series = ets, _incontinence_time_series = uts, _bowel_urgency_time_series = buts, _DLC = date_last_contact, _alive = alive_or_not, _DOB = dob, _tt = tt, _pt = pt, _sdt = sdt, _texts = texts)



class tumor_lite_w(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid']) | erection_time_series.get_all_keys(params, self)

    def whether_to_override(self, object_key):
        return False

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        # obtains info related to a tumor.  puts it into a tumor instance and returns it
        tt = self.get_var_or_file(tumor_info, params)
        pt = self.get_var_or_file(patient_info, params)
        sdt = self.get_var_or_file(super_db_info, params)
        #self.set_param(params, 'count_words', helper.words_to_coded_words(['erection','erections','erectile dysfunction']))
        #erection_negation_counts = self.get_var_or_file(negation_counts, params)
        pid = self.get_param(params, 'pid')
        #pdb.set_trace()
        #gleason_primary = tt['CS_SSFactor5'][2]
        #gleason_secondary = tt['CS_SSFactor5'][3]
        

        #ets = self.get_var_or_file(erection_time_series, params)
        #uts = self.get_var_or_file(incontinence_time_series, params)

        ets = None
        uts = None
        buts = None

        alive_or_not = sdt['C_Vital']
        date_last_contact = helper.my_date.init_from_hyphen_string(sdt['C_DLC'])
        dob = helper.my_date.init_from_slash_string(sdt['C_DOB'])

        return helper.tumor_lite(_pid = pid, _grade = tt['Grade'], _SEERSummStage = tt['SEERSummStage2000'] , _BestStage = tt['BestStage'], _surgery_code = tt['MstDefSurgPrimSumm'], _radiation_code = tt['MstDefRTSumm'], _date_diagnosed = helper.my_date.init_from_num(tt['DateDx']), _surgery_date = helper.my_date.init_from_num(tt['DtMstDefSurg']), _radiation_date = helper.my_date.init_from_num(tt['MstDefRTDt']), _erection_time_series = ets, _incontinence_time_series = uts, _bowel_urgency_time_series = buts, _DLC = date_last_contact, _alive = alive_or_not, _DOB = dob, _tt = tt, _pt = pt, _sdt = sdt)


class tumor_list(wrapper.obj_wrapper):
    """
    list is identified by name i give it.  not by contents of list
    """


    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['list_name'])

    def whether_to_override(self, object_key):
        return False

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pids_to_use = self.get_param(params, 'pid_list')
        ans = []
        count = 0
        for pid in pids_to_use:
            try:
                self.set_param(params, 'pid', pid)
                helper.print_if_verbose('getting ' + str(pid) + ' ' + str(count), 0.8)
                to_add = self.get_var_or_file(tumor_w, params)
                import features as f
                print f.single_attribute_feature(helper.tumor.alive).generate(to_add)
            except:
                pass
            else:
                ans.append(to_add)
            count += 1
        pdb.set_trace()
        return ans

class tumor_lite_list(wrapper.obj_wrapper):
    """
    list is identified by name i give it.  not by contents of list
    """


    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['list_name'])

    def whether_to_override(self, object_key):
        return True

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        pids_to_use = self.get_param(params, 'pid_list')
        ans = []
        count = 0
        for pid in pids_to_use:
            try:
                self.set_param(params, 'pid', pid)
                helper.print_if_verbose('getting ' + str(pid) + ' ' + str(count), 0.8)
                to_add = self.get_var_or_file(tumor_lite_w, params)
                import features as f
                print f.single_attribute_feature(helper.tumor.alive).generate(to_add)
            except:
                pass
            else:
                ans.append(to_add)
            count += 1
        pdb.set_trace()
        return ans
