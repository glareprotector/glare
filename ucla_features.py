from basic_features import *
import global_stuff

class ucla_treatment_code_f(feature):
    """
    same codes as for mgh data
    """
    def _generate(self, pid):
        first = pid[0]
        if first == '1':
            return 3
        elif first == '2':
            return 2
        elif first == '3':
            return 1
        else:
            raise Exception

class ucla_age_f(feature):

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[0]

class ucla_black_or_not_f(feature):

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[1]

class ucla_gleason_f(feature):

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[2]

class ucla_stage_f(feature):

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[3]

class ucla_psa_f(feature):

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[4]

class ucla_comorbidity_count_f(feature):

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[5]
