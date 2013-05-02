from basic_features import *
import global_stuff

class ucla_treatment_code_f(feature):
    """
    same codes as for mgh data
    """
    surgery, radiation, brachy = 1,2,3

    def _generate(self, pid):
        first = pid[0]
        if first == '1':
            #print ucla_treatment_code_f.brachy
            return ucla_treatment_code_f.brachy
        elif first == '2':
            #print ucla_treatment_code_f.radiation
            return ucla_treatment_code_f.radiation
        elif first == '3':
            #print ucla_treatment_code_f.surgery
            return ucla_treatment_code_f.surgery
        else:
            raise Exception


class ucla_feature(feature):

    age, race, gleason, stage, psa, comorbidity_count = range(6)
    def __init__(self, which_row, **kwargs):
        self.which_row = which_row
        super(ucla_feature, self).__init__(**kwargs)

    def _generate(self, pid):
        import ucla_objects, param
        p = param.param({'pid':pid})
        info = wc.get_stuff(ucla_objects.UCLA_patient_info, p)
        return info[self.which_row]

class black_or_not(indicator_feature):

    def __init__(self, **kwargs):
        indicator_feature.__init__(self, ucla_feature(ucla_feature.race), 1, **kwargs)
