import wrapper
from wrapper_decorator import dec
import global_stuff
import pdb

class UCLA_patient_list(wrapper.obj_wrapper):
    """
    note that pids are *strings*
    """

    def whether_to_override(self, object_key):
        return True

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

class UCLA_patient_info(wrapper.obj_wrapper, wrapper.by_pid_wrapper):

    def whether_to_override(self, object_key):
        return False

    @classmethod
    def get_all_keys(cls, params, self=None):
        return set('pid')

    @dec
    def constructor(self, params, recalculate, to_pickle, to_filelize = False, always_recalculate = False, old_obj = None):
        f = open(global_stuff.ucla_file, 'r')
        f.next()
        pid == self.get_param('pid')
        for line in f:
            s = line.strip().split(',')
            line_pid = s[0]
            if line_pid == pid:
                ans = [0 for x in range(6)]
                try:
                    ans[0] = int(s[0]) # age
                    ans[1] = int(s[1]) # race (black or not)
                    ans[2] = int(s[2]) # gleason
                    ans[3] = int(s[3]) * tstage
                    ans[4] = float(s[4]) # psa level
                    ans[5] = int(s[5]) # comorbidity count
                except Exception, error:
                    print error
                    pdb.set_trace()
                else:
                    return ans
        raise Exception
