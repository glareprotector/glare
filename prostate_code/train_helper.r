

# for each elt in a vector, apply function that returns vector(row), and returns matrix of those rows.  used to get covariates
line_apply <- function(v, f){
    return(t(sapply(v, f)))
}

# function that takes in a pid, and returns a vector of its covariates
get_x_by_pid_given_xs <- function(pid, xs){
    return(xs[pid,])		     
}

# function that takes in vector, applies function that returns a matrix, and rbinds all of those matricies
# do this by first calling lapply, then reduce with cbind
# used to get tall thin matrix of all times
cbind_apply <- function(v, f){
    return(Reduce(rbind,lapply(v, f)))	    
}

# function that takes in pid and returns long thin vector of its times/values
get_tvs_given_folder <- function(pid, folder){
    file <- paste(folder_path,'/','pid',sep='')
    return(read.csv(file,header=F))
}

# function that takes in pid and returns how many times it has
get_tv_length <- function(pid, get_tvs_f){
    return(dim(get_tvs_f(pid))[1])
}

# function that takes in an index and returns a covariate vector with entries between -1 and 1
idx_to_cov <- function(i, n, d){
    return(rep(-1.0 + 2*i/n, d))
}

library(functional)


# reads data into list for feeding into rstan, given folder
get_real_full_data <- function(folder_path){
	    

	
    xs_file <- paste(folder_path,'xs.csv',sep='')	
    xs <- read.csv(xs_file,header=T,row.names=1)

    pids <- row.names(xs)		

    get_x_by_pid <- Curry(get_x_by_pid_given_xs, xs=xs)



    get_tvs <- Curry(get_tvs_given_folder, folder=paste(folder_path,'/','datapoints/',sep=''))

    tvs <- cbind_apply(pids, get_tvs)



    tv_lengths <- sapply(pids, Curry(get_tv_length, get_tvs_f=get_tvs))

    # get ss, as, bs, cs
    ss_file <- paste(folder_path,'ss.csv',sep='')
    ss <- read.csv(ss_file,header=F,row.names=1)[,1]
    as_file <- paste(folder_path,'as.csv',sep='')
    as <- read.csv(as_file,header=F,row.names=1)[,1]
    bs_file <- paste(folder_path,'bs.csv',sep='')
    bs <- read.csv(bs_file,header=F,row.names=1)[,1]
    cs_file <- paste(folder_path,'cs.csv',sep='')
    cs <- read.csv(cs_file,header=F,row.names=1)[,1]

    pop_a = mean(as[,1])
    pop_b = mean(bs[,1])
    pop_c = mean(cs[,1])

    data <- list(ls=tv_lengths,ts=tvs[,1],vs=tvs[,2],xs=xs,ss=ss,N=dim(xs)[1],K=dim(xs)[2],L=dim(tvs)[1])

    return(data)

}

a_from_x <- function(x, B, pop){
    y <- pop + sum(x*B)
    return(1 / (1 + exp(-y)))	 
}

c_from_x <- function(x, B, pop){
    y <- pop + sum(x*B)
    return(exp(y))
}

my_rbeta <- function(m, phi){
    s <- 1.0 / phi
    return(rbeta(1, 1+s*m, 1+s*(1-m)))
}

my_rgamma <- function(m, phi){
    alpha <- 1.0 / phi + 1
    beta <- m / (alpha - 1)
    return(rgamma(1, shape=alpha, rate=beta))
}

a_from_x_random <- function(x, B, pop, phi){
    return(my_rbeta(a_from_x(x, B, pop), phi))
}

c_from_x_random <- function(x, B, pop, phi){
    return(my_rgamma(c_from_x(x, B, pop), phi))
}

the_f <- function(t, a, b, c){
   return(1-a - a*(1-b)*exp(-t/c))
}

noise_adder <- function(x, phi){
   return(rnorm(1,x,phi))	   
}

# need function that given a,b,c getters, returns true values at specified times
vals_given_abc <- function(x, a_getter, b_getter, c_getter, ts, f){
   a <- a_getter(x)
   b <- b_getter(x)
   c <- c_getter(x)
   the_f_curried <- Curry(f,a=a,b=b,c=c)
   return(sapply(ts,the_f_curried))
}

# simulate data to feed into rstan
get_simulated_full_data <- function(N, K, B_a, B_b, B_c, pop_a, pop_b, pop_c, ts, phi_a, phi_b, phi_c, phi_m){

    squash_a <- Curry(a_from_x, B=B_a, pop=pop_a)			
    squash_b <- Curry(a_from_x, B=B_b, pop=pop_b)			
    squash_c <- Curry(c_from_x, B=B_c, pop=pop_c)

    squash_a_random <- Curry(a_from_x, B=B_a, pop=pop_a, phi=phi_a)			
    squash_b_random <- Curry(a_from_x, B=B_b, pop=pop_b, phi=phi_b)			
    squash_c_random <- Curry(c_from_x, B=B_c, pop=pop_c, phi=phi_c)

    noise_adder_to_use <- Curry(noise_adder, phi=phi_m)
    custom_compose <- function(s,u){
        composed <- function(t, a, b, c){
	    return(s(u(t,a,b,c)))
	}    		   
    }
    the_f_random <- custom_compose(noise_adder, the_f)

    # can switch getters to random, or f to the_f_random
    get_vals <- Curry(vals_given_abc, a_getter=squash_a, b_getter=squash_b, c_getter=squash_c, f=the_f)

    get_tvs <- function(x, get_vals_f, ts){
        ans <- cbind(ts, get_vals_f(x=x, ts=ts))
	print(ans)
	return(ans)
    }

    # can add noise to get_vals if i want
    get_tvs_to_use <- Curry(get_tvs, get_vals_f=get_vals, ts=ts)

    pids <- 1:N
    idx_to_cov_to_use <- Curry(idx_to_cov,n=N,d=K)
    xs <- line_apply(pids, idx_to_cov_to_use)

    compose <- function(s,u){
    	composed <- function(p){
	    return(s(u(p)))
	}
    }
    get_tvs_from_pid <- compose(get_tvs_to_use, idx_to_cov_to_use)

    tvs <- cbind_apply(pids, get_tvs_from_pid)
    
    tv_lengths <- sapply(pids, Curry(get_tv_length, get_tvs_f=get_tvs_from_pid))

    data <- list(ls=tv_lengths,ts=tvs[,1],vs=tvs[,2],xs=xs,N=dim(xs)[1],K=dim(xs)[2],L=dim(tvs)[1])

    return(data)

}


# given a fitted model and folder, writes the posterior parameters in the folder
write_full_posterior_parameters <- function(fit, folder){
    results_directory <- paste(folder_path, '/', 'posterior_parameters', sep='')
    dir.create(results_directory)

    results <- extract(fit)

    B_aR <- results$B_a
    B_bR <- results$B_b
    B_cR <- results$B_c
    phi_aR <- results$phi_a
    phi_bR <- results$phi_b
    phi_cR <- results$phi_c
    phi_mR <- results$phi_m

    write.csv(B_aR, paste(results_directory,'/','out_B_a.csv',quote=F,header=F))
    write.csv(B_bR, paste(results_directory,'/','out_B_b.csv',quote=F,header=F))
    write.csv(B_cR, paste(results_directory,'/','out_B_c.csv',quote=F,header=F))
    write.csv(phi_aR, paste(results_directory,'/','out_phi_a.csv',quote=F,header=F))
    write.csv(phi_bR, paste(results_directory,'/','out_phi_b.csv',quote=F,header=F))
    write.csv(phi_cR, paste(results_directory,'/','out_phi_c.csv',quote=F,header=F))
    write.csv(phi_mR, paste(results_directory,'/','out_phi_m.csv',quote=F,header=F))

}