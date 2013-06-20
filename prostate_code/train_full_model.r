# given a folder containing data, 1. turns folder into input for rstan, 2. runs model, 3. saves parameters in appropriate folder



library(rstan)

source('train_helper.r')

model_file <- 'full_model.stan'

data <- get_simulated_full_data(5,2,1,1,1,.5,.5,2,c(1,2,3,4),.01,.01,.01,.1)


fit <- stan(file = model_file, data = data, iter = 1000, chains = 1)



