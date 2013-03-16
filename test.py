import match_features
c = match_features.clause_fragment_getter()
w = match_features.window_fragment_getter(c)
test = 'A B and C D .,and E F .. G H though I J '
test_fragment = match_features.base_fragment(test)
print w.get_fragment(test_fragment, 15, 1, 1).get_raw_text()
