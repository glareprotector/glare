# given a folder containing data, 1. turns folder into input for rstan, 2. runs model, 3. saves parameters in appropriate folder

args <- commandArgs(trailing=TRUE)
data_folder <- args[1]
parameters_folder <- args[2]

library(rstan)
source('~/prostate_git/glare/prostate_code/train_helper.r')
model_file <- '~/prostate_git/glare/prostate_code/rstan_stuff/full_model.stan'


data <- get_real_full_data(data_folder)
fit <- stan(file = model_file, data = data, iter = 20000, warmup = 1000, chains = 1)
write_full_posterior_parameters(fit, parameters_folder)


#data <- get_simulated_full_data(50,2,1,-1,2,.5,.5,2,c(.01, .1, 1,2,3,4),.01,.01,.01,.1, 1, 1, 1, 15, 15, 15, 1)
#data <- get_real_full_data('/Users/glareprotector/prostate_git/glare/prostate_code/files_for_rstan/full_model_3_fold/urinary_function/radiation/fold_0_3/train/')