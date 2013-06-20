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

""'
