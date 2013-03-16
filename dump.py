
    


    class incontinence_decision_rule1(decision_rule):
        """
        returns 2 if the patient is incontinent, 1 if some, 0 if no incontinence
        """

        def _generate(self, text):
            # search for occurrences of incontinent/incontinence.  for each match, search within same sentence for ignore words.
            #pdb.set_trace()
            found = False
            word_matcher = basic_word_matcher()
            clause_getter = clause_fragment_getter()
            sentence_getter = sentence_fragment_getter()
     
            # supply words to neg whose presence means don't look at entire sentence
            negation_detector = basic_negation_detector()
            for incont_match in word_matcher.get_matches(text, ['incontinent', 'incontinence', 'dribbling']):

                ignore_fragment = sentence_getter.get_fragment(text, incont_match.get_abs_start())
                if len(word_matcher.get_matches(ignore_fragment, global_stuff.ignore_words)) > 0:
                    pass
                else:
                    # if negated, return 0.  else, return 1 if a moderating word is found, else 2

                    if negation_detector.is_negated(text, incont_match.get_abs_start()):
                        return sv_int(0)
                    else:
                        moderating_context = clause_getter.get_fragment(text, incont_match.get_abs_start())
                        if len(word_matcher.get_matches(moderating_context, global_stuff.moderating_words)) > 0:
                            return sv_int(1)
                        else:
                            return sv_int(2)
            raise my_exceptions.NoFxnValueException


    class incontinence_decision_rule2(decision_rule):
        """
        searches for {lose, loses, losing, leak, leaks, leaking} and {urine} in same sentence.  if negated, return 0.  if not, search for moderating word
        """
        def _generate(self, text):
            #pdb.set_trace()
            clause_getter = clause_fragment_getter()
            multiple_matcher = multiple_word_in_same_fragment_matcher(clause_getter)
            negator = basic_negation_detector()
            lose_cls = ['lose', 'loses', 'losing','lost','leak', 'leaks', 'leaking', 'leaked','spill', 'spills', 'spilled']
            urine_cls = ['urine']
            matches = multiple_matcher.get_matches(text, lose_cls, urine_cls)
            for m in matches:

                if negator.is_negated(text, m.get_abs_start()):
                    return sv_int(0)
                else:
                    moderating_context = clause_getter.get_fragment(text, incont_match.get_abs_start())
                    if len(word_matcher.get_matches(moderating_context, global_stuff.moderating_words)) > 0:
                        return sv_int(1)
                    else:
                        return sv_int(2)
            raise my_exceptions.NoFxnValueException

    class incontinence_decision_rule3(decision_rule):
        """
        searches for urinary controls: dry
        """
        def _generate(self, text):
            #pdb.set_trace()
            multiple = multiple_word_in_same_fragment_matcher(clause_fragment_getter())
            matches = multiple.get_matches(text, ['urinary','urine'], ['function'])
            word_matcher = basic_word_matcher()
            after_colon_getter = fragment_getter_by_stuff_after_colon()
            for m in matches:

                after_colon = after_colon_getter.get_fragment(text, m.get_abs_start())
                if after_colon != None:
                    pdb.set_trace()
                    if len(word_matcher.get_matches(after_colon, ['normal'])) > 0:
                        return sv_int(0)

            matches = multiple.get_matches(text, ['urinary','urine'], ['control'])
            for m in matches:
                after_colon = after_colon_getter.get_fragment(text, m[0].get_abs_start())
                if after_colon != None:
                    pdb.set_trace()
                    if len(word_matcher.get_matches(after_colon, ['dry'])) > 0:
                        return sv_int(0)

            raise my_exceptions.NoFxnValueException


