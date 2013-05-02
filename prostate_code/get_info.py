import helper
import pdb
import side_effects
import features
def print_tumor_side_effect_excerpts_and_classification(tumor, side_effect):

    ans = ''

    #excerpts = tumor.get_attribute(tumor.texts).filter_excerpt_by_side_effects(side_effect)
    for record in tumor.get_attribute(tumor.texts):
        filtered_excerpts = record.get_excerpts_by_side_effect(side_effect)

        for excerpt in filtered_excerpts:

            ans += '\nexcerpt: ' + '\n'
            ans += str(excerpt) + '\n'
            ans += 'class: ' + '\n'
            ans += str(features.side_effect_excerpt_feature(side_effect).generate(excerpt)) + '\n'
    return ans




