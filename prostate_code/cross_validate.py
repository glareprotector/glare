"""
What does cross validation return?
- get parameter for a test fold (obtained via training)
- armed with parameter, can get stuff from each fold, then combine them to get something for entire dataset.
- could have every db have a custom args to db-specific 'key'.  so in theory, every db would have a method that takes in arguments, and figures out how to cache it.  in __call__ 

how is data stored? was a dictionary of some sort of data structure
let's say i want to compute squared loss for now.
- for each test_fold, create data dictionary, call R to get parameters trace/distribution
- have some sort of data structure to store the distribution of scores for each patient in a fold.  this can be the first thing i compute
- after i compute distribution of scores, i should still have the actual data.  scores will be in the form of dictionary keyed

for each fold, get distribution of score data structure.  more generally, from distribution of parameters and data for the fold, compute something.  then, have a 2nd function that combines those somethings

for fold in folds
    parameter[i] = get parameters(fold.train_data)

for each blah in stuff to do
for fold in folds
    1. results[i] = compute_scores(parameters[i], fold.test_data)
2. do something with all results   

to same figures, return the fig object, and the writer calls fig.savefig



ok, need to make 
- model.  one huge vector of times, one huge vector of function values, one vector of patient lengths
- r code that reads in data written by python, and converts it into the data structures that will be used by rstan.

to train, specify model file, folder where data will go.

"""


class k_fold_getter(object):

    def __init__(self, k, d):
        self.k, self.d = k, d

    def __iter__(self):
        count = 0
        for i in range(self.k):
            train = {}
            test = {}
            for key,val in self.d.iteritems():
                if count % self.k == i:
                    test[key] = val
                else:
                    train[key] = val
                count += 1
            yield fold(i, self.k, train, test)




class fold(object):

    def __init__(self, i, k, train_data, test_data):
        self.i, self.k, self.train_data, self.test_data = i, k, train_data, test_data

    def __str__(self):
        return 'fold' + str(i) + '_' + str(k)

def cross_validate(full_data_d, fold_getter, stuffs_to_do, train_parameters_f):
    """
    stuffs_to_do is a tuple: (function to run on each fold, function that combines the stuff run on each fold)
    combiner_f's should be memoized
    """

    trained_parameters = []

    for fold in fold_getter(full_data_d):
        trained_parameters.append(train_parameters_f(fold.train_data))

    results = []
    for stuff in stuff_to_do:
        do_on_each_test_fold_f = stuff[0]
        combiner_f = stuff[1]
        stuff_results = []
        for fold, trained_parameter in zip(fold_getter(full_data_d), trained_parameters):
            stuff_results.append(do_on_each_test_fold(trained_parameter, fold.test_data))
        results.append(combiner_f(stuff_results))

    return results
