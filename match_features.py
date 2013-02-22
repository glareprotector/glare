from features import *
import helper
from my_data_types import sv_int, sv_float
import re

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





