import wrapper
from wrapper_decorator import dec
import global_stuff
import pdb
import my_data_types

class UCLA_patient_list(wrapper.obj_wrapper):
    """
    note that pids are *strings*
    """

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        f = open(global_stuff.ucla_file, 'r')
        pdb.set_trace()
        f.next()
        ans = set()
        for line in f:
            s = line.strip().split(',')
            line_pid = s[0]
            ans.add(line_pid)
        return list(ans)


class UCLA_raw_series_dict(wrapper.obj_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set()

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):

        import pdb
        pdb.set_trace()

        def get_raw_series(pid, column):
            import helper
            ans = my_data_types.timed_list()
            f = open(global_stuff.ucla_file, 'r')
            f.next()
            for line in f:
                s = line.strip().split(',')
                line_pid = s[0]
                if line_pid == pid:
                    line_time = helper.my_timedelta(days=int(s[1])*30)
                    try:
                        line_val = float(s[column])
                    except ValueError:
                        ans.append(my_data_types.timed_no_value_object(time=line_time))
                    else:
                        ans.append(my_data_types.timed_float(line_val, time=line_time))
            return ans

        ans = {}

        from basic_features import ucla_raw_series_getter as g
        for pid in self.get_var_or_file(UCLA_patient_list, params):
            for column in [g.physical_condition, g.mental_condition, g.urinary_function, g.urinary_bother, g.bowel_function, g.bowel_bother, g.sexual_function, g.sexual_bother]:
                ans[(pid, column)] = get_raw_series(pid, column)
        

        return ans





class UCLA_patient_info(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set(['pid'])

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        f = open(global_stuff.ucla_file, 'r')
        f.next()
        pid = self.get_param(params, 'pid')
        for line in f:
            s = line.strip().split(',')
            line_pid = s[0]
            if line_pid == pid:
                ans = [0 for x in range(6)]
                try:
                    ans[0] = int(s[10]) # age
                except:
                    ans[0] = my_data_types.no_value_object()
                try:
                    ans[1] = int(s[11]) # race (black or not)
                except:
                    ans[0] = my_data_types.no_value_object()
                try:
                    ans[2] = int(s[12]) # gleason
                except:
                    ans[0] = my_data_types.no_value_object()
                try:
                    ans[3] = int(s[13]) # tstage
                except:
                    ans[0] = my_data_types.no_value_object()
                try:
                    ans[4] = float(s[14]) # psa level
                except:
                    ans[0] = my_data_types.no_value_object()
                try:
                    ans[5] = int(s[15]) # comorbidity count
                except:
                    ans[0] = my_data_types.no_value_object()     
                return ans
        raise Exception
