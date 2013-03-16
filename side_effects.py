import my_exceptions
from match_features import *
import helper
from my_data_types import sv_int, sv_float
import global_stuff
from basic_features import feature

# this is now a feature whose input object is a record
class side_effect_report_feature(feature):


    def __repr__(self):
        pass

    def _generate(self, report):

        """
        have global option to either query, or not query and fail
        """

        # make report text lower case
        report.raw_text = report.raw_text.lower()


        # check if human label is there.  if yes, check for key for this side effect.  if not, depending on a value in side effect, proceed, or just return fail

        import my_exceptions

        if self.use_human_label():
            try:
                ans = side_effect.human_classify(report)
                return ans
            except my_exceptions.NoFxnValueException:
                pass


        if self.only_use_human_label():
            raise my_exceptions.NoFxnValueException


        return self.classify_record(report)


    def classify_record(self, report):
        pass


    def use_human_label(self):
        pass


    def only_use_human_label(self):
        pass





class bowel_urgency_bin(side_effect_report_feature):

    def classify_record(self, report):
        #pdb.set_trace()
        ans = bowel_urgency().classify_record(report)
        #print 'BIN: ', ans.get_value()
        if ans.get_value() in [1,2]:
            return sv_int(0)
        elif ans.get_value() == 0:
            return sv_int(1)


    def use_human_label(self):
        return False

    def only_use_human_label(self):
        return False

    def __repr__(self):
        return 'bowel_urgency'



class urin_incont_bin(side_effect_report_feature):

    def classify_record(self, report):
        #pdb.set_trace()
        ans = urinary_incontinence().classify_record(report)
        #print 'BIN: ', ans.get_value()
        if ans.get_value() in [1,2]:
            return sv_int(0)
        elif ans.get_value() == 0:
            return sv_int(1)


    def use_human_label(self):
        return False

    def only_use_human_label(self):
        return False

    def __repr__(self):
        return 'urinary_incontinence_binary'
    
class classify_by_rule_list(side_effect_report_feature):
    """
    good should be 1.  so if response in question is 1 or 2, put 1
    """


    def use_human_label(self):
        return False

    def only_use_human_label(self):
        return False


    def classify_record(self, report):
        #print 'report date: ', report.date

        report_text = base_fragment(report.raw_text)
        count = 0
        #pdb.set_trace()
        #print report
        #if report.pid == 262152:
        #    pdb.set_trace()
        for rule in self.get_report_decision_rules():
            try:

                ans = rule.generate(report_text)

                #print 'VALUE: ', ans, rule, count, report.pid
                #pdb.set_trace()
                return ans
            except my_exceptions.NoFxnValueException:
                #pdb.set_trace()
                pass
            count += 1
        raise my_exceptions.NoFxnValueException





class bowel_urgency(classify_by_rule_list):

    def __repr__(self):
        return 'bowel_urgency'

    def get_report_decision_rules(self):
        test2 = generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['bowel','bowels','rectal','stool','stools'], ['urgency','incontinence','incontinent']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)


        test6 = decision_rule_filter(generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['bowel','rectal'], ['symptom','symptoms','issue','issues','problem','problems']), clause_negation_detector(global_stuff.negation_words_cls), compound_ignore_detector(ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), ignore_detector(clause_fragment_getter(), ['sounds','sound'])), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0), [sv_int(0)])

        test7 = decision_rule_filter(generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['bowel','bowels'], ['normal','ok','fine']), clause_negation_detector(global_stuff.negation_words_cls), compound_ignore_detector(ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), ignore_detector(clause_fragment_getter(), ['sounds','sound'])), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 1), [sv_int(0)])


        return [test2, test6, test7]





class urinary_frequency_bin(side_effect_report_feature):

    def classify_record(self, report):
        ans = urinary_frequency().classify_record(report)
        if ans.get_value() in [1,2]:
            return sv_int(0)
        elif ans.get_value() == 0:
            return sv_int(1)


    def use_human_label(self):
        return False

    def only_use_human_label(self):
        return False

    def __repr__(self):
        return 'urinary_frequency_bin'
    




class urinary_frequency(classify_by_rule_list):

    def __repr__(self):
        return 'urinary_frequency'

    def get_report_decision_rules(self):
        # ignore if bowel is in same clause or no context words
        main_ignore_detector = compound_ignore_detector(ignore_detector(sentence_fragment_getter(), ['bowel','bowels','stool','stools']), not_ignore_detector(ignore_detector(window_fragment_getter(sentence_fragment_getter(),1,1),['urinary','urination','gu','humaturia','dysuria','hesitancy','urgency','flomax','urine'])), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words))
        main_negation_detector = basic_negation_detector(global_stuff.moderating_words + ['has','had','noted','significant'], global_stuff.negation_words_cls)
        test1 = generic_basic_decision_rule(hard_coded_basic_word_matcher(['frequency']), main_negation_detector, main_ignore_detector, moderating_detector(clause_fragment_getter(),global_stuff.moderating_words),0)
        

        test6 = decision_rule_filter(generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['urinary'], ['symptom','symptoms','issue','issues','problem','problems']), clause_negation_detector(global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0), [sv_int(0)])
        return [test1,test6]




class diarrhea_bin(side_effect_report_feature):

    def classify_record(self, report):
        ans = diarrhea().classify_record(report)
        if ans.get_value() in [1,2]:
            return sv_int(0)
        elif ans.get_value() == 0:
            return sv_int(1)


    def use_human_label(self):
        return False

    def only_use_human_label(self):
        return False

    def __repr__(self):
        return 'diarrhea_bin'
    




class diarrhea(classify_by_rule_list):

    def get_report_decision_rules(self):
        # check for diarrhea
        test1 = generic_basic_decision_rule(hard_coded_basic_word_matcher(['diarrhea']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)
        # loose (bowel/stool)
        test2 = generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['loose'], ['bowel','bowels','stool','stools']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)
        # bowel/bowels normal (ignore if sound)
        test3 = decision_rule_filter(generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['normal','ok','okay'], ['bowel','bowels','stool','stools']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words+['sound','sounds']), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 1), [sv_int(0)])
        # old rule
        test6 = decision_rule_filter(generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['bowel','bowels'], ['symptom','symptoms','issue','issues','problem','problems']), clause_negation_detector(global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0), [sv_int(0)])
        return [test1,test2,test3,test6]


    def __repr__(self):
        return 'diarrhea'


class urinary_incontinence(classify_by_rule_list):

    def __repr__(self):
        return 'urinary_incontinence'

    def get_report_decision_rules(self):



        test1 = generic_basic_decision_rule(hard_coded_basic_word_matcher(['incontinent','incontinence']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), compound_ignore_detector(ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), ignore_detector(clause_fragment_getter(), ['bowel','stool','stools','lymph','lymphatic','valsalva','fecal','rectal'])), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)
        lose_cls = ['lose', 'loses', 'losing','lost','leak', 'leaks', 'leaking', 'leaked','spill', 'spills', 'spilled']
        urine_cls = ['urine']
        test2 = generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), lose_cls, urine_cls), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)
        test3 = generic_basic_decision_rule(hard_coded_basic_word_matcher(['leak','leaks','leakage','dribble','dribbling']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), compound_ignore_detector(ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), ignore_detector(clause_fragment_getter(), ['bowel','stool','lymph','lymphatic','valsalva','fecal','anastomotic','bile','troponin','enzyme','valve','air'])), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)
        test4 = generic_basic_decision_rule(hard_coded_basic_word_matcher(['continent','continence']), basic_negation_detector(global_stuff.moderating_words, global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 1)
        test5 = generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['hold','holds','holding'], ['urine']), clause_negation_detector(global_stuff.negation_words_cls + ['problem','problems','difficulty','difficulties']), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 1)
        #test6 = generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['urinary'], ['symptom','symptoms','issue','issues','problem','problems']), clause_negation_detector(global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0)
        test6 = decision_rule_filter(generic_basic_decision_rule(hard_coded_multiple_word_in_same_fragment_matcher(clause_fragment_getter(), ['urinary'], ['symptom','symptoms','issue','issues','problem','problems']), clause_negation_detector(global_stuff.negation_words_cls), ignore_detector(sentence_fragment_getter(), global_stuff.ignore_words), moderating_detector(sentence_fragment_getter(), global_stuff.moderating_words), 0), [sv_int(0)])
        

        
        return [test1,test2,test3,test4,test5,test6]

        return [urinary_incontinence.incontinence_decision_rule1(), urinary_incontinence.incontinence_decision_rule2(), urinary_incontinence.incontinence_decision_rule3()]


    def get_synonyms(self):
        import pdb

        return ['urinary','urine','urination','incontinence','incontinent','continent','continence','void','voiding','leak','leaking','leaks','leakage','retention','retaining','control']

    def human_classify(self, record):
        import wc
        import param
        p = param.param({'pid':record.pid, 'rec_idx':record.idx})
        stored_qa = wc.get_stuff(side_effect_human_input_report_labels, p)
        import quesions
        the_q = questions.urinary_incontinence
        try:
            ans = stored_qa[the_q]
        except KeyError:
            raise my_exceptions.NoFxnValueException
        else:
            if ans == 0:
                raise my_exceptions.NoFxnValueException
            else:
                if ans in [1,2]:
                    return 1
                elif ans in [3,4]:
                    return 0
                else:
                    pdb.set_trace()
                    raise






    

class side_effect_report_feature_by_excerpt_voting(side_effect_report_feature):


    def get_synonyms(self):
        pass

    def get_display_words(self):
        return self.get_synonyms()


    def classify_record(self, report):
        
        side_effect_excerpts = report.get_excerpts_by_side_effect(self)
        #pdb.set_trace()
        excerpt_scores = side_effect_excerpts.apply_feature(side_effect_excerpt_feature(self), my_data_types.my_list)
        
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






    def get_absolute_good_match_features(self):
        pass

    def get_absolute_bad_match_features(self):
        pass

    def get_semi_good_match_features(self):
        pass

    def get_semi_bad_match_features(self):
        pass

    def get_no_info_match_features(self):
        pass


# this is a pretty bad class.  only exists because of side_effect_by_voting class
class side_effect_excerpt_feature(feature):

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


        for no_info_match in self.parent_report_feature.get_no_info_match_features():
            if no_info_match.generate(excerpt, anchor) == True:
                raise my_exceptions.NoFxnValueException(no_info_match.phrase)

        try:
            ans = my_data_types.sv_int(self.classify_excerpt(excerpt))
        except my_exceptions.NoFxnValueException:
            ans = my_data_types.sv_int(self.basic_classify(excerpt))
        #print excerpt
        #print "label: ", ans
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


    def classify_excerpt(self, excerpt):

        # anchor of excerpt is guaranteed to be the one and only synonym of side effect that is in the excerpt
        anchor = excerpt.anchor

        helper.print_if_verbose('SPECIFIC_CLASSIFY',2)
        absolute_good = False
        for absolute_good_match in self.parent_report_feature.get_absolute_good_match_features():
            if absolute_good_match.generate(excerpt, anchor) == True:
                helper.print_if_verbose('absolute good with phrase:',2) 
                helper.print_if_verbose(str(absolute_good_match.phrase),2)
                absolute_good = True
                break

        absolute_bad = False
        for absolute_bad_match in self.parent_report_feature.get_absolute_bad_match_features():
            if absolute_bad_match.generate(excerpt, anchor) == True:
                helper.print_if_verbose('absolute bad with phrase:',2) 
                helper.print_if_verbose(str(absolute_bad_match.phrase),2)
                absolute_bad = True
                break


        helper.print_if_verbose('absolute_good: ' + str(absolute_good) + ' absolute_bad: ' + str(absolute_bad), 1.5)

        if absolute_good and absolute_bad:
            raise my_exceptions.NoFxnValueException
        
        if absolute_good:
            return sv_int(1)
        
        if absolute_bad:
            return sv_int(0)

        num_semi_good = 0
        for semi_good_match in self.parent_report_feature.get_semi_good_match_features():
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
        for semi_bad_match in self.parent_report_feature.get_semi_bad_match_features():
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
                return sv_int(1)
            else:
                return sv_int(0)



    def __init__(self, parent_report_feature):
        self.parent_report_feature = parent_report_feature






class erection_side_effect(side_effect_report_feature_by_excerpt_voting):


    def __repr__(self):
        return 'ED'



    def human_classify(self, record):
        """
        returns NoFxnValueException if no human label available
        """
        pass
        

    def get_absolute_good_match_features(self):
        try:
            return self.absolute_good_match_features
        except:
            pass
        words = ['excellent']
        self.absolute_good_match_features = [position_phrase_matcher(word, 10, global_stuff.delimiters) for word in words]
        self.absolute_good_match_features.append(position_phrase_matcher('good', 3, global_stuff.delimiters))
        return self.absolute_good_match_features

    def get_absolute_bad_match_features(self):
        try:
            return self.absolute_bad_match_features
        except:
            pass
        words = ['absent','unable','failed','gone','poor','diminished','incomplete', 'no erections']
        self.absolute_bad_match_features = [position_phrase_matcher(word, 10, global_stuff.delimiters) for word in words]
        return self.absolute_bad_match_features

    def get_semi_good_match_features(self):
        try:
            return self.semi_good_match_features
        except:
            pass
        words = ['stable','intact','present','able','achieve','adequate','satisfactory','normal','return','full','reasonable','sustainable','strong','recover','sufficient','has','have','had','having']
        self.semi_good_match_features = [position_phrase_matcher(word, 10, global_stuff.delimiters) for word in words]
        return self.semi_good_match_features

    def get_semi_bad_match_features(self):
        try:
            return self.semi_bad_match_features
        except:
            pass
        words = ['not','denies','difficulty','problem','difficulties','problems']
        self.semi_bad_match_features = [position_phrase_matcher(word, 10, global_stuff.delimiters) for word in words]
        self.semi_bad_match_features.append(position_phrase_matcher('no', 10, global_stuff.delimiters, ['no requirement']))
        return self.semi_bad_match_features


    def get_no_info_match_features(self):
        try:
            return self.no_info_match_features
        except:
            pass
        words = ['possible','possibly','prior','may','expect','can','risk','chance','expect','important','likely','probability','suggested','suggest','discuss','will']
        self.no_info_match_features = [position_phrase_matcher(word, 20, []) for word in words]
        return self.no_info_match_features

    def get_synonyms(self):
        return ['erection', 'erections']


