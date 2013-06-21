 /*
this is full model with B_a,B_b,B_c,phi_a,phi_b,phi_c,phi_noise
*/
data{
	int<lower=0> N; # number of patients
	int<lower=0> K; # number of covariates
	int<lower=0> L; # total number of datapoints

	int<lower=0> ls[N];
	real<lower=0> ts[L];
	real vs[L];

	vector[K] xs[N];
	real<lower=0.0,upper=1.0> ss[N];

	real<lower=0,upper=1> pop_a;	
	real<lower=0,upper=1> pop_b;	
	real<lower=0> pop_c;	

	real<lower=0> c_a;
	real<lower=0> c_b;
	real<lower=0> c_c;

	real<lower=0> l_a;
	real<lower=0> l_b;
	real<lower=0> l_c;
	real<lower=0> l_m;

}
parameters{
	vector[K] B_a;
	vector[K] B_b;
	vector[K] B_c;
	
	real<lower=0,upper=1> phi_a;
	real<lower=0,upper=1> phi_b;
	real<lower=0,upper=1> phi_c;
	real<lower=0> phi_m;
	
	real<lower=0,upper=1> as[N];	
	real<lower=0,upper=1> bs[N];
	real<lower=0,upper=1> cs[N];
}
transformed parameters{

	# these are actual parameters for input into distributions
	real<lower=0> s_a;
	real<lower=0> s_b;		
	real<lower=0> s_c;

	real<lower=0,upper=1> m_as[N];
	real<lower=0,upper=1> m_bs[N];
	real<lower=0> m_cs[N];
	for(i in 1:N){	      
	      m_bs[i] <- inv_logit(pop_b + dot_product(xs[i], B_b));
	      m_cs[i] <- exp(pop_c + dot_product(xs[i], B_c));
	      m_as[i] <- inv_logit(pop_a + dot_product(xs[i], B_a));	
	}
	
	s_a <- 1.0 / phi_a;
	s_b <- 1.0 / phi_b;
	s_c <- (1.0 / phi_c) + 1;

	
	


}
model{
	int c;
	c <- 1;

	B_a ~ normal(0, c_a);
	B_b ~ normal(0, c_b);
	B_c ~ normal(0, c_c);

	phi_a ~ exponential(l_a);
	phi_b ~ exponential(l_b);
	phi_c ~ exponential(l_c);
	phi_m ~ exponential(l_m);

	for(i in 1:N){
	      as[i] ~ beta(1.0 + (s_a * m_as[i]), 1.0 + (s_a * (1.0 - m_as[i])));
	      bs[i] ~ beta(1.0 + (s_b * m_bs[i]), 1.0 + (s_b * (1.0 - m_bs[i])));
	      cs[i] ~ gamma(s_c, m_cs[i] / (s_c - 1.0));
	}


	for(i in 1:N){
	      for(j in 1:ls[i]){
	      	    vs[c] ~ normal(ss[i] * (1.0 - as[i] - as[i] * (1.0 - bs[i]) * exp(-1.0 * ts[c] / cs[i])), phi_m);
		    c <- c + 1;
	      }
	}

}