import wrapper
from wrapper_decorator import dec
import wrapper
import param
import global_stuff
import helper
import pdb
import features
import side_effects

class PID_to_MRN_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return True

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

class MRN_to_PID_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return True

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
        return True

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

        MRN = map[pid]
        query = 'select Comments from [RPDR].[dbo].[LMRNote] where MRN=' + str(MRN)
        cursor = helper.get_cursor()
        cursor.execute(query)
        ans = []
        i = 0
        for row in cursor:
            ans.append(row.Comments)

                
        return ans



class raw_medical_text_new(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return True

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
        for row in cursor:
            date_str = row.LMRNote_Date_Time.split()[0]
            from helper import my_date
            date = my_date.init_from_str(date_str)
            raw_text = row.Comments
            
            temp = helper.report_record(pid, date, raw_text)
            ans.append(temp)
            #asdf = temp.filter_excerpt_by_word('psa')
            #if len(asdf) > 0:
                #print 'ORIGINAL'
                #print temp
                #print '\nFILTERED'
                #print asdf
            #    ans.append(asdf)
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




class erection_time_series(wrapper.obj_wrapper, wrapper.by_pid_wrapper):
    

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
        return features.report_feature_time_course_feature_factory.get_feature(features.side_effect_report_record_feature_factory.get_feature(side_effects.erection_side_effect)).generate(tumor_texts, relative_to_diagnosis, diagnosis_date)
        

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
        texts = self.get_var_or_file(raw_medical_text_new, params)
        #self.set_param(params, 'count_words', helper.words_to_coded_words(['erection','erections','erectile dysfunction']))
        #erection_negation_counts = self.get_var_or_file(negation_counts, params)
        pid = self.get_param(params, 'pid')
        #pdb.set_trace()
        #gleason_primary = tt['CS_SSFactor5'][2]
        #gleason_secondary = tt['CS_SSFactor5'][3]
        ets = self.get_var_or_file(erection_time_series, params)


        return helper.tumor(_pid = pid, _grade = tt['Grade'], _SEERSummStage = tt['SEERSummStage2000'] ,_texts = texts, _surgery_code = tt['MstDefSurgPrimSumm'], _radiation_code = tt['MstDefRTSumm'], _date_diagnosed = helper.my_date.init_from_num(tt['DateDx']), _surgery_date = helper.my_date.init_from_num(tt['DtMstDefSurg']), _radiation_date = helper.my_date.init_from_num(tt['MstDefRTDt']), _erection_time_series = ets)


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
            except:
                pass
            else:
                ans.append(to_add)
            count += 1
        pdb.set_trace()
        return ans