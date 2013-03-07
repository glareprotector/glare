from features import *
import helper
from my_data_types import sv_int, sv_float
import re
import string
import global_stuff
import my_exceptions

#sv = get_wrapped_single_value_object_feature_factory.get_feature().generate






class decision_rule(feature):

    pass




class phrase_matcher(feature):
    """
    matches word if present and no ignore phrases appear
    """

    def _generate(self, excerpt):


        for ignore_phrase in self.ignore_phrases:
            if helper.match_phrase(excerpt, ignore_phrase):
                return sv_int(0)

        if helper.match_phrase(excerpt, self.phrase):
            return sv_int(1)
        else:
            return sv_int(0)



    def __init__(self, phrase, ignore_phrases = []):
        self.phrase = phrase
        self.ignore_phrases = ignore_phrases



class position_phrase_matcher(phrase_matcher):
    """
    matches words in a certain window of the unique anchor of the phrase.  window specified by min of window size and any delimiter
    phrases have not been processed yet
    """

    def get_word_window(self, excerpt, anchor):


        import helper
        cleaned_text = helper.clean_text(excerpt.raw_text, self.delimiters)


        anchor = excerpt.anchor
        words = cleaned_text.split()
        idx = words.index(anchor)
        low_idx = max(idx - self.word_window, 0)
        high_idx = min(len(words), idx + self.word_window)

        


        raw_text = excerpt.raw_text[:]



            
        


        sentence_positions = [i for i in range(len(words)) if words[i] == 'gsw']
        highest_low = None
        lowest_high = None
        for pos in sentence_positions:
            if pos < idx:
                if highest_low == None:
                    highest_low = pos
                elif pos > highest_low:
                    highest_low = pos
            if pos > idx:
                if lowest_high == None:
                    lowest_high = pos
                elif pos < lowest_high:
                    lowest_high = pos
        if highest_low != None:
            low_idx = max(low_idx, highest_low)
        if lowest_high != None:
            high_idx = min(high_idx, lowest_high)


        import string
        return string.join(words[low_idx:high_idx], ' ')

    def _generate(self, excerpt, anchor):
        shortened_excerpt = self.get_word_window(excerpt, anchor)
        helper.print_if_verbose('SHORTENED: ' + shortened_excerpt, 2)
        return phrase_matcher(self.phrase).generate(shortened_excerpt)

    def __init__(self, phrase, word_window, delimiters, ignore_phrases = []):
        self.word_window = word_window
        self.delimiters = delimiters
        if '|' not in self.delimiters:
            self.delimiters.append('|')
        phrase_matcher.__init__(self, phrase, ignore_phrases)



class fragment(object):
    """
    implements get_raw_text and get_abs_start/end methods.  positions are absolute ones
    """

    def __init__(self, parent_text, abs_start, abs_end):
        """
        text is another fragment object, unless it is a base_fragment in which case text is raw text
        """
        self.text = parent_text
        self.abs_start = abs_start
        self.abs_end = abs_end

    def get_raw_text(self):
        return self.text.get_raw_text()[(self.abs_start - self.text.get_abs_start()):(self.abs_end - self.text.get_abs_start())]

    def __repr__(self):
        return self.get_raw_text()

    def get_abs_start(self):
        return self.abs_start

    def get_abs_end(self):
        return self.abs_end
        

class base_fragment(fragment):

    def __init__(self, text):
        self.text = text
        self.abs_start = 0
        self.abs_end = len(text)

    def get_raw_text(self):
        return self.text




class match(fragment):
    pass



class word_matcher(object):

    def get_matches(self, text, word_cls):
        """
        returns match object(s).  position in match object is absolute position
        """
        pass

class basic_word_matcher(object):
    def get_matches(self, text, word_cls):
        raw_text = text.get_raw_text()
        #try finding each word one at a time
        ans = []
        for word in word_cls:
            searcher = re.compile('('+string.join(self.word_seps, sep='|') +')' + word + '('+string.join(self.word_seps, sep='|') +')')
            matches = [m for m in searcher.finditer(raw_text)]

            for m in matches:
                # don't want match to include the separators
                local_start = m.start()
                local_end = m.end()
                word_seps_copy = self.word_seps[:]
                word_seps_copy.remove('^')
                word_seps_copy.remove('$')
                if re.search('('+string.join(word_seps_copy, '|') +')', raw_text[m.end()-1:m.end()]) != None:
                    # if last character is not a characterless a separator
                    local_end -= 1
                if re.search('('+string.join(word_seps_copy, '|') +')', raw_text[m.start():m.start()+1]) != None:
                    # if first character is a not a characterless separator
                    local_start += 1
                ans.append(match(text, local_start + text.get_abs_start(), local_end + text.get_abs_start()))

        return ans

    def __init__(self, word_seps = ['^','\s','$','\.',',']):
        self.word_seps = word_seps


class hard_coded_word_matcher(object):

    def get_matches(self, text):
        pass


class hard_coded_basic_word_matcher(basic_word_matcher, hard_coded_word_matcher):

    def get_matches(self, text):
        return basic_word_matcher.get_matches(self, text, self.word_cls)

    def __init__(self, word_cls, word_seps = ['^','\s','$','\.',',']):
        self.word_cls = word_cls
        basic_word_matcher.__init__(self, word_seps)


class multiple_word_in_same_fragment_matcher(object):

    def get_matches(self, text, word_cls1, word_cls2):
        """
        if there is match, returns list of match objects, which is the same as a fragment
        multiple words being matched here.  in this case, return the fragment spanning all matches
        """
        # search for first word, then get its position and corresponding fragment
        basic_matcher = basic_word_matcher()
        possible_one_matches = basic_matcher.get_matches(text, word_cls1)
        ans = []

        for match1 in possible_one_matches:
            fragment = self.fragment_getter.get_fragment(text, match1.get_abs_start())
            possible_two_matches = basic_matcher.get_matches(fragment, word_cls2)
            for match2 in possible_two_matches:
                ans.append(helper.get_spanning_match(match1, match2))
                #ans.append([match1, match2])
        
        return ans

    def __init__(self, fragment_getter):
        self.fragment_getter = fragment_getter




class hard_coded_multiple_word_in_same_fragment_matcher(multiple_word_in_same_fragment_matcher, hard_coded_word_matcher):

    def __init__(self, fragment_getter, word_cls1, word_cls2):
        self.word_cls1 = word_cls1
        self.word_cls2 = word_cls2
        multiple_word_in_same_fragment_matcher.__init__(self,fragment_getter)

    def get_matches(self, text):
        return multiple_word_in_same_fragment_matcher.get_matches(self, text, self.word_cls1, self.word_cls2)



class fragment_getter(object):

    def get_fragment(self, text, position, *args):
        """
        text is fragment object with a get_raw_text() fxn
        position is absolute position
        """
        pass

class fragment_getter_by_delim(fragment_getter):
    """
    if text[position] is delimiter, leftwards search will get it, but rightwards won't.
    imagine that the search starts at the gap between position and position + 1
    position refers to absolute position
    """
    def get_fragment(self, text, position):
        raw_text = text.get_raw_text()
        delimiter_m = re.compile('(' + string.join(self.delimiters, sep='|') + ')')
        

        end_match = helper.get_next_match(raw_text, delimiter_m, position+1 - text.get_abs_start())
        start_match = helper.get_last_match(raw_text, delimiter_m, position - text.get_abs_start())
        if start_match == None:
            local_start = 0
        else:
            local_start = start_match.end()
        if end_match == None:
            local_end = len(raw_text)
        else:
            local_end = end_match.start()
        return fragment(text, text.get_abs_start() + local_start, text.get_abs_start() + local_end)

    def __init__(self, delimiters):
        self.delimiters = delimiters


class fragment_getter_by_stuff_after_colon(fragment_getter):
    """
    returns stuff after a colon up until a return or period(for a colon in the same line)
    for now, don't care if it includes the colon/end character
    returns None if there is no colon
    """
    def get_fragment(self, text, position):

        raw_text = text.get_raw_text()


        # search for colon within the same line
        sentence_getter = sentence_fragment_getter()
        current_line = sentence_getter.get_fragment(text, position)


        searcher = re.compile(':')
        m = searcher.search(current_line.get_raw_text(), position - current_line.get_abs_start())

        if m == None:
            return None
        else:
            colon_pos = m.start()
            #search for first period/return starting from colon_pos
            # make fragment searcher that has colon in it, and get the abs_end
            searcher = fragment_getter_by_delim(global_stuff.sentence_delimiters + [':'])
            after_colon = searcher.get_fragment(current_line, colon_pos + current_line.get_abs_start())
            frag_start = colon_pos + current_line.get_abs_start()
            frag_end = after_colon.get_abs_end()
            #searcher = re.compile('('+string.join(global_stuff.sentence_delimiters, sep='|')+')')
            #m = searcher.search(current_line.get_raw_text(), colon_pos)
            #if m == None:
            #    return None
            #else:
            #pdb.set_trace()
            #frag_start = colon_pos + current_line.get_abs_start()
            #frag_end = m.start() + current_line.get_abs_start()
            return fragment(text, frag_start, frag_end)

class clause_fragment_getter(fragment_getter_by_delim):

    def __init__(self):
        fragment_getter_by_delim.__init__(self, global_stuff.clause_delimiters)

class sentence_fragment_getter(fragment_getter_by_delim):

    def __init__(self):
        fragment_getter_by_delim.__init__(self, global_stuff.sentence_delimiters)



class line_fragment_getter(fragment_getter_by_delim):

    def __init__(self):
        fragment_getter_by_delim.__init__(self, global_stuff.newline_delimiters)






class ignore_detector(object):
    """
    assumes that this only searches for single ignore words, or else would have passed in a word_matcher instance
    returns TRUE if you should ignore the phrase
    """

    def to_ignore(self, text, position):
        context = self.fragment_getter.get_fragment(text, position)
        word_matcher = basic_word_matcher()
        matched = word_matcher.get_matches(context, self.ignore_words)
        #if len(matched) > 0:
        #    print 'ignored: ', matched
        return len(matched) > 0

        

    
    def __init__(self, fragment_getter, ignore_words = global_stuff.ignore_words):
        self.fragment_getter = fragment_getter
        self.ignore_words = ignore_words


class compound_ignore_detector(object):
    """
    takes in (for now) two ignore_detectors, and returns TRUE if either of them says ignore
    """
    def __init__(self, ignore_detector1, ignore_detector2):
        self.ignore_detector1 = ignore_detector1
        self.ignore_detector2 = ignore_detector2

    def to_ignore(self, text, position):
        if self.ignore_detector1.to_ignore(text, position) or self.ignore_detector2.to_ignore(text, position):
            return True
        return False


class moderating_detector(object):

    def is_moderated(self, text, position):
        context = self.fragment_getter.get_fragment(text, position)
        word_matcher = basic_word_matcher()
        return len(word_matcher.get_matches(context, self.moderating_words)) > 0


    def __init__(self, fragment_getter, moderating_words = global_stuff.moderating_words):
        self.fragment_getter = fragment_getter
        self.moderating_words = moderating_words
        

class negation_detector(object):

    def is_negated(self, text, position):
        """
        decides whether term at position in text is negated.  returns T or F
        """

class clause_negation_detector(negation_detector):
    """
    only looks at clause, not the sentence
    """
    def is_negated(self, text, position):
        clause = clause_fragment_getter().get_fragment(text, position)
        basic_matcher = basic_word_matcher()
        num_local_negations = len(basic_matcher.get_matches(clause, self.negation_words_cls))
        return num_local_negations % 2 == 1

    def __init__(self, negation_words_cls):
        self.negation_words_cls = negation_words_cls

class basic_negation_detector(negation_detector):
    """
    first looks within a clause and does standard negation.  if clause contains a key word, return answer.  else, if no, return no.  if there were ZERO negation words in that, look in entire sentence
    """

    def is_negated(self, text, position):

        clause = clause_fragment_getter().get_fragment(text, position)
        basic_matcher = basic_word_matcher()
        num_local_negations = len(basic_matcher.get_matches(clause, self.negation_words_cls))
        if len(basic_matcher.get_matches(clause, self.look_at_clause_words)) > 0:
            return num_local_negations % 2 == 1
        elif num_local_negations % 2 == 1:
            return True

        elif num_local_negations == 0:
            sentence = sentence_fragment_getter().get_fragment(text, position)
            num_sentence_negations = len(basic_matcher.get_matches(sentence, self.negation_words_cls))
            return num_sentence_negations % 2 == 1
        else:
            assert num_local_negations % 2 == 0
            return False


        assert False
        return nuaam_negations % 2 == 1

    def __init__(self, look_at_clause_words = [], negation_words_cls = global_stuff.negation_words_cls):
        self.look_at_clause_words = look_at_clause_words
        self.negation_words_cls = negation_words_cls


# some decision rules are only valid if answer is a certain one.  otherwise, raise exception
class decision_rule_filter(decision_rule):

    def __init__(self, base_rule, allowed_values):
        self.allowed_values = allowed_values
        self.base_rule = base_rule

    def _generate(self, text):
        try:
            val = self.base_rule.generate(text)
        except my_exceptions.NoFxnValueException:
            raise my_exceptions.NoFxnValueException
        else:
            if val in self.allowed_values:
                return val
            else:
                raise my_exceptions.NoFxnValueException

# things that change for rules.  sign of word.  if word indicates presence of side effect, moderating word sends from 2 to 1.  0 ro 1 if word indicates no side effect.
# need to specify what makes negation detector not look to entire sentence
# basic decision rule just looks for a match (can be any type of get_match object), a negation detector instance, moderating detector instance, and the sign of the phrase


class generic_basic_decision_rule(decision_rule):
    """
    convention: sign of 0 means unnegated phrase indicates presence of bad thing, so if there is a unnegated match, should return 2
    """

    def __init__(self, hard_matcher, negation_detector, ignore_detector, moderating_detector, sign):
        self.hard_matcher = hard_matcher
        self.negation_detector = negation_detector
        self.ignore_detector = ignore_detector
        self.moderating_detector = moderating_detector
        self.sign = sign

    
    def _generate(self, text):
        matches = self.hard_matcher.get_matches(text)
        for m in matches:
            if not self.ignore_detector.to_ignore(text, m.get_abs_start()):
                frag = sentence_fragment_getter().get_fragment(text, m.get_abs_start())
                #print 'frag: ', frag
                #if 'date' in frag.get_raw_text():
                #    pdb.set_trace()
                assert self.sign in [0,1]
                if self.sign == 0:
                    if self.negation_detector.is_negated(text, m.get_abs_start()) == False:
                        if self.moderating_detector.is_moderated(text, m.get_abs_start()) == False:
                            return sv_int(2)
                        else:
                            return sv_int(1)
                    else:
                        return sv_int(0)
                elif self.sign == 1:
                    if self.negation_detector.is_negated(text, m.get_abs_start()) == False:
                        if self.moderating_detector.is_moderated(text, m.get_abs_start()) == False:
                            return sv_int(0)
                        else:
                            return sv_int(1)
                    else:
                        return sv_int(2)

        raise my_exceptions.NoFxnValueException





