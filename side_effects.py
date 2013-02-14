import my_exceptions
from match_features import *
import helper
from features import sv

# generic side effect classifying functionality will be left to features, but feature specific stuff will be here
class side_effect(object):

    @classmethod
    def get_synonyms(cls):
        pass

    @classmethod
    def classify_excerpt(cls, excerpt):
        raise NotImplementedError


    @classmethod
    def classify_excerpt(cls, excerpt):

        # anchor of excerpt is guaranteed to be the one and only synonym of side effect that is in the excerpt
        anchor = excerpt.anchor

        helper.print_if_verbose('SPECIFIC_CLASSIFY',2)
        absolute_good = False
        for absolute_good_match in cls.get_absolute_good_match_features():
            if absolute_good_match.generate(excerpt, anchor) == True:
                helper.print_if_verbose('absolute good with phrase:',2) 
                helper.print_if_verbose(str(absolute_good_match.phrase),2)
                absolute_good = True
                break

        absolute_bad = False
        for absolute_bad_match in cls.get_absolute_bad_match_features():
            if absolute_bad_match.generate(excerpt, anchor) == True:
                helper.print_if_verbose('absolute bad with phrase:',2) 
                helper.print_if_verbose(str(absolute_bad_match.phrase),2)
                absolute_bad = True
                break


        helper.print_if_verbose('absolute_good: ' + str(absolute_good) + ' absolute_bad: ' + str(absolute_bad), 1.5)

        if absolute_good and absolute_bad:
            raise my_exceptions.NoFxnValueException
        
        if absolute_good:
            return sv(1)
        
        if absolute_bad:
            return sv(0)

        num_semi_good = 0
        for semi_good_match in cls.get_semi_good_match_features():
            try:
                ans = semi_good_match.generate(excerpt, anchor)
                ans.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if ans.get_value():
                    helper.print_if_verbose('semi good with phrase: ' + semi_good_match.phrase, 1.5)
                num_semi_good += ans.get_value()
        
        num_semi_bad = 0
        for semi_bad_match in cls.get_semi_bad_match_features():
            try:
                ans = semi_bad_match.generate(excerpt, anchor)
                ans.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                if ans.get_value():
                    helper.print_if_verbose('semi bad with phrase: ' + semi_bad_match.phrase, 1.5)
                num_semi_bad += ans.get_value()


        helper.print_if_verbose('num_semi_good: ' + str(num_semi_good) + ' num_semi_bad: ' + str(num_semi_bad), 1.5)

        if num_semi_good + num_semi_bad == 0:
            raise my_exceptions.NoFxnValueException
        else:
            if num_semi_bad % 2 == 0:
                return sv(1)
            else:
                return sv(0)


    @classmethod
    def get_absolute_good_match_features(cls):
        pass

    @classmethod
    def get_absolute_bad_match_features(cls):
        pass

    @classmethod
    def get_semi_good_match_features(cls):
        pass

    @classmethod
    def get_semi_bad_match_features(cls):
        pass

    @classmethod
    def get_no_info_match_features(cls):
        pass


class erection_side_effect(side_effect):

    @classmethod
    def get_absolute_good_match_features(cls):
        try:
            return cls.absolute_good_match_features
        except:
            pass
        words = ['excellent']
        cls.absolute_good_match_features = [position_phrase_matcher_factory.get_feature(word, 10) for word in words]
        return cls.absolute_good_match_features

    @classmethod
    def get_absolute_bad_match_features(cls):
        try:
            return cls.absolute_bad_match_features
        except:
            pass
        words = ['absent','unable','failed','gone','poor','diminished','incomplete', 'no erections']
        cls.absolute_bad_match_features = [position_phrase_matcher_factory.get_feature(word, 10) for word in words]
        return cls.absolute_bad_match_features

    @classmethod
    def get_semi_good_match_features(cls):
        try:
            return cls.semi_good_match_features
        except:
            pass
        words = ['stable','intact','present','able','achieve','adequate','good','satisfactory','normal','return','full','reasonable','sustainable','strong','recover','sufficient','has','have','had']
        cls.semi_good_match_features = [position_phrase_matcher_factory.get_feature(word, 10) for word in words]
        return cls.semi_good_match_features

    @classmethod
    def get_semi_bad_match_features(cls):
        try:
            return cls.semi_bad_match_features
        except:
            pass
        words = ['not','denies','difficulty','problem','difficulties','problems']
        cls.semi_bad_match_features = [position_phrase_matcher_factory.get_feature(word, 10) for word in words]
        cls.semi_bad_match_features.append(position_phrase_matcher_factory.get_feature('no', 10, ['no requirement']))
        return cls.semi_bad_match_features

    @classmethod
    def get_no_info_match_features(cls):
        try:
            return cls.no_info_match_features
        except:
            pass
        words = ['possible','possibly','prior','may','expect','can','risk','chance','expect','important','likely','probability','suggested','suggest','discuss','will']
        cls.no_info_match_features = [position_phrase_matcher_factory.get_feature(word, 15) for word in words]
        return cls.no_info_match_features

    @classmethod
    def get_synonyms(cls):
        return ['erection', 'erections']


