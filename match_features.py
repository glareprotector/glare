from features import *
import helper
from my_data_types import sv_int, sv_float
import re
import string
import global_stuff

#sv = get_wrapped_single_value_object_feature_factory.get_feature().generate

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

    def get_match(self, text, word_cls):
        """
        returns match object(s).  position in match object is absolute position
        """
        pass

class basic_word_matcher(object):
    def get_match(self, text, word_cls):
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


class fragment_getter(object):

    def get_fragment(self, text, position, *args):
        """
        text is fragment object with a get_raw_text() fxn
        position is absolute position
        """
        pass

class fragment_getter_by_delim(fragment_getter):

    def get_fragment(self, text, position):
        raw_text = text.get_raw_text()
        local_pos = position - text.get_abs_start()
        local_end = local_pos
        local_start = local_pos
        delimiter_m = re.compile('(' + string.join(self.delimiters, sep='|') + ')')
        
        while local_end < len(raw_text) and delimiter_m.search(raw_text[local_end]) == None:
            local_end += 1
            
        while local_start >= 0 and delimiter_m.search(raw_text[local_start]) == None:
            local_start -= 1

        # now local_end and local_start refer to local position of delimiters
        local_start += 1
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
        current_line_getter = fragment_getter_by_delim(global_stuff.newline_delimiters)
        current_line = current_line_getter.get_fragment(text, position)


        searcher = re.compile(':')
        m = searcher.search(current_line.get_raw_text())

        if m == None:
            return None
        else:
            colon_pos = m.start()
            #search for first period/return starting from colon_pos
            searcher = re.compile('('+string.join(global_stuff.delimiters, sep='|')+')')
            m = searcher.search(raw_text, colon_pos)
            if m == None:
                return None
            else:
                frag_start = colon_pos + current_line.get_abs_start()
                frag_end = m.start() + current_line.get_abs_start()
                return fragment(text, frag_start, frag_end)

class sentence_fragment_getter(fragment_getter_by_delim):

    def __init__(self):
        fragment_getter_by_delim.__init__(self, global_stuff.delimiters)

class ignore_fragment_getter(fragment_getter_by_delim):

    def __init__(self):
        fragment_getter_by_delim.__init__(self, global_stuff.ignore_delimiters)


class multiple_word_in_same_fragment_matcher(object):

    def get_matches(self, text, word_cls1, word_cls2):
        """
        if there is match, returns list of match objects
        """
        # search for first word, then get its position and corresponding fragment
        basic_matcher = basic_word_matcher()
        possible_one_matches = basic_matcher.get_match(text, word_cls1)
        ans = []

        for match1 in possible_one_matches:
            fragment = self.fragment_getter.get_fragment(text, match1.get_abs_start())
            possible_two_matches = basic_matcher.get_match(fragment, word_cls2)
            for match2 in possible_two_matches:
                ans.append([match1, match2])
        
        return ans

    def __init__(self, fragment_getter):
        self.fragment_getter = fragment_getter
        

class negation_detector(object):

    def is_negated(self, text, position):
        """
        decides whether term at position in text is negated.  returns T or F
        """

class basic_negation_detector(negation_detector):
    """
    takes as input negation words and fragment getter.  just counts number of negations detected in the gotten fragment
    """

    def is_negated(self, text, position):
        fragment = self.fragment_getter.get_fragment(text, position)
        num_negations = 0
        basic_matcher = basic_word_matcher()
        num_negations = len(basic_matcher.get_match(fragment, self.negation_words_cls))
        return num_negations % 2 == 1

    def __init__(self, fragment_getter, negation_words_cls = global_stuff.negation_words_cls):
        self.fragment_getter = fragment_getter
        self.negation_words_cls = negation_words_cls





class decision_rule(feature):

    pass
