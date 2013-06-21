import pandas
import basic_features as bf
import pdb
import my_exceptions
import ucla_features as uf
import helper
import numpy as np
from helper import get_branded_version as brand
import cross_validate

import subprocess
from analyze_helper import *

"""
base folder has attributes, number of folds specified


generates files corresponding to posterior params

"""

base_folder = '/Users/glareprotector/prostate_git/glare/prostate_code/files_for_rstan/full_model_3_fold/'

treatments = [treatment_radiation]
side_effects = [side_effect_sexual_function]
attributes = [attribute_age]
model = model_full
num_folds = 3

if True:


    for side_effect in side_effects:
        
        for treatment in treatments:

            for i in range(num_folds):
                
                data_folder = se_treatment_fold_to_training_folder(base_folder, side_effect, treatment, i, num_folds)

                parameters_folder = se_treatment_fold_model_to_posterior_folder(base_folder, side_effect, treatment, i, num_folds, model)

                train_cmd = model.train_script + ' ' + data_folder + ' ' + parameters_folder
                
                print train_cmd

                subprocess.call(train_cmd, shell=True)
