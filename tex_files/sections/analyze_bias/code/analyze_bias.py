import pymc
import math
import helper
import random
import pdb
import numpy as np
import matplotlib.pyplot as plt
import math


def g(x):
    return 1.0 / (1.0 + math.exp(-1.0 * x))

def g_inv(y):
    return math.log(y/(1.0-y))

def squash(x,B, mu_pop_a_inv):
    return g(mu_pop_a_inv + B*x)

def m_s_to_alpha_beta(center, rho, mean_or_mode):

    s = (1.0 / rho) - 1
    if mean_or_mode == 'mean':
        m = (center * (s+2) - 1) / s
    elif mean_or_mode == 'mode':
        m = center
    a = 1 + s*m
    b = 1 + s*(1-m)
    return a,b


def get_beta(center, rho, mean_or_mode):
    alpha, beta = m_s_to_alpha_beta(center, rho, mean_or_mode)
    return random.betavariate(alpha, beta)


def get_beta_p(v,mu,rho,mean_or_mode):
    alpha, beta = m_s_to_alpha_beta(mu, rho, mean_or_mode)
    return pymc.distributions.beta_like(v,alpha,beta)


def get_beta_mean_given_mode_rho(mode, rho):
    s = (1.0 / rho) - 1
    return (s * mode + 1) / (s + 2)


base_folder = '/Users/glareprotector/prostate_git/glare/tex_files/sections/analyze_bias/files/'


#####################################################
# for several means, plot distribution as rho varies#
#####################################################

if False:

    """
    First question is whether we should have a linear model for the mean or mode of the beta distribution that a comes from
    In each subplot, I plot several beta distributions.  All of them have the same \emph{mean}, but different $\phi$'s
    """


    rhos_to_try = [.01,.04,.07,.1,.3,.5,.7]
    mus_to_try = [.6,.7,.8,.9]

    file_name = base_folder + 'beta_vs_mu.png'

    fig = plt.figure()
    fig.suptitle(r'beta distribution for fixed mean, as $\phi$ varies')
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)    
    

    for mu,i in zip(mus_to_try,range(4)):
        ax = fig.add_subplot(2,2,i+1)
        ax.set_title(r'$\mu=$'+str(mu))
        ax.set_xlabel(r'$x$')
        ax.set_ylabel(r'$p(x)$')
        for rho in rhos_to_try:
            ppx = helper.seq(0,1,1000)
            ppy = [math.exp(get_beta_p(x,mu,rho,'mean')) for x in ppx]
            ax.plot(ppx,ppy,label=str(rho))
        ax.legend(loc=2, prop={'size':6})
        
    fig.show()

    fig.savefig(file_name)

    pdb.set_trace()


#####################################################
# for several modes, plot distribution as rho varies#
#####################################################

if False:

    """
    In each subplot, I plot several beta distributions.  All of them have the same \emph{mode}, but different $\phi$'s
    It seems better to have a linear model for the mode of beta distributions
    """

    file_name = base_folder + 'beta_vs_mode.png'

    rhos_to_try = [.01,.04,.07,.1,.3,.5,.7]

    modes_to_try = [.6,.7,.8,.9]

    fig = plt.figure()
    fig.suptitle(r'beta distribution for fixed mode, as $\phi$ varies')
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)    

    for mu,i in zip(mus_to_try,range(4)):
        ax = fig.add_subplot(2,2,i+1)
        ax.set_title(r'mode='+str(mu))
        ax.set_xlabel(r'$x$')
        ax.set_ylabel(r'$p(x)$')
        for rho in rhos_to_try:
            ppx = helper.seq(0,1,1000)
            ppy = [math.exp(get_beta_p(x,mu,rho,'mode')) for x in ppx]
            ax.plot(ppx,ppy,label=str(rho))

    fig.show()
    fig.savefig(file_name)

    pdb.set_trace()


###################################################
# for several rhos, plot distribution as mu varies#
###################################################

if False:

    """
    Let's try to get a grasp on the $\phi$ parameter.  In each subplot, I fix $\phi$ and plot a beta distribution with various modes, with that $\phi$.
    """

    file_name = base_folder + 'beta_phi.png'

    mus_to_try = [.5,.55,.6,.65,.7,.75,.8,.85,.9,.95]
    rhos_to_try = [.01,.04,.07,.1,.3,.5]

    fig = plt.figure()
    fig.suptitle(r'beta distribution for fixed $\phi$, as mode varies')
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)    

    for rho,i in zip(rhos_to_try,range(len(rhos_to_try))):
        ax = fig.add_subplot(2,3,i+1)
        ax.set_title(r'$\phi=$'+str(rho))
        ax.set_xlabel(r'$x$')
        ax.set_ylabel(r'$p(x)$')
        for mu in mus_to_try:
            ppx = helper.seq(0,1,1000)
            ppy = [math.exp(get_beta_p(x,mu,rho,'mode')) for x in ppx]
            ax.plot(ppx,ppy,label=str(mu))

    fig.show()

    fig.savefig(file_name)

    pdb.set_trace()




######################################################################################
# for several mu_pop_as, plot the posterior distribution of B, for many values of rho#
######################################################################################

if True:

    """
    Now, goal is to see if this beta regression produces biased MLE estimates of B.  In the below plots, I set B=1.0
    Below, for each $(\mu_{pop}^a,\phi)$ combination, I do the following:
    \begin{enumerate}
    \item let $X_i$ be number between -1 and 1.  The $X_1, \ldots X_n$ are chosen to be equally spaced between -1 and 1.  $n=100$.
    \item for each $X_i$, generate $a_i$ according to the model, with randomness.$(\mu_{pop}^a$ and $\phi^a)$ and B are all specified, so this is well defined.
    \item Plot the distribution of $P(B;X_i,a_i,\phi,\mu_{pop}^a)$
    \end{enumerate}
    These plots are mildly informative.  Small $\phi$'s get rid of bias.  It's not clear if higher $\phi$ leads to bias in one direction.
    """


    file_name = base_folder + 'B_posterior.png'

    init_B = 1.0


    num_xs = 50
    xs = [x/float(num_xs) for x in range(-1*num_xs, num_xs+1)]
    xs = [1.0 for gg in range(100)]
    #xs = [1.0]

    mu_pop_as = [.5,.6,.7,.8]
    #rhos = [.1,.2,.3,.4,.5,.6,.7,.8,.9]
    #rhos = [.1,.2,.3,.4]
    rhos = [.01,.04,.07,.1,.3,.5,.7]
    fig = plt.figure()
    fig.suptitle('posterior of B for artificial dataset, B='+str(init_B))
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)    

    for mu_pop_a,i in zip(mu_pop_as,range(4)):

        mu_pop_a_inv = g_inv(mu_pop_a)
        
        ax = fig.add_subplot(2,2,i+1)
        ax.set_title('mode='+str(mu_pop_a))
        ax.set_xlabel('B')
        ax.set_ylabel(r'$P(B;X_i,a_i,\phi^a,\mu_{pop}^a)$')

        for rho in rhos:

            a_s = [get_beta(squash(x,init_B,mu_pop_a_inv),rho,'mode') for x in xs]
            #a_s = [squash(x,init_B,mu_pop_a_inv) for x in xs]

            @pymc.stochastic(observed=False, verbose = 0)
            def M_B(value = 1):
                return 0

            @pymc.stochastic(observed=True, verbose = 0)
            def M_rho(value = rho):
                return 0

            a_vars = []

            for x,a,i in zip(xs,a_s,xrange(len(xs))):

                @pymc.stochastic(observed=True,name='a_'+str(i), verbose = 0)
                def M_a(value = a, x = x, B=M_B, rho_v = M_rho):
                    m = squash(x,B, mu_pop_a_inv)
                    alpha, beta = m_s_to_alpha_beta(m, rho_v, 'mode')
                    return pymc.distributions.beta_like(value, alpha, beta)
    
                a_vars.append(M_a)

            model = pymc.MCMC([M_B,M_rho,a_vars])

            # can just plot likelihood for various values of B.  forget sampling

            vals = helper.seq(init_B-3,init_B+3,300)
            pdfs = np.zeros(300)
            the_max = -1
            for i in xrange(300):
                model.get_node('M_B').value = vals[i]
                pdfs[i] = math.exp(model.logp)
                if pdfs[i] > the_max:
                    the_max = pdfs[i]
            pdfs = pdfs / the_max
            print pdfs
            ax.plot(vals,pdfs,label=r'$\phi=$'+str(rho))


        ax.legend(loc=2, prop={'size':6})
    
    fig.show()

    fig.savefig(file_name)
    pdb.set_trace()





#################################################################################################
# for a single sample x, for several rhos, plot likelihood x came from beta(mu,rho) as mu varies#
#################################################################################################

if True:

    """
    Try to figure out the cause of the bias.  Here, I fix x. I plot P(x;mode,$\phi$), assuming $x \sim Beta(mode,\phi)$.  Note that for high values of, x the mode of $P(x;mode,\phi)$ does not occur at $x$.  I do this for 4 values of x.
    """

    file_name = base_folder + 'infer_beta_mode.png'

    xs = [.5,.8,.9,.95]
    rhos = [.01,.04,.07,.1,.3,.5,.7]
    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    fig.suptitle(r'likelihood of x if x ~ Beta(mode,$\phi$), as mode varies, $\phi$ fixed')

    ppx = helper.seq(0,1,300)
    for x,i in zip(xs,range(len(xs))):
        ax = fig.add_subplot(2,2,i+1)
        ax.set_title(r'x='+str(x))
        ax.axvline(x)
        ax.set_xlabel('mode')
        ax.set_ylabel(r'p(x;mode,$\phi$)')
        for rho in rhos:
            pdfs = [math.exp(get_beta_p(x,px,rho,'mode')) for px in ppx]
            ax.plot(ppx,pdfs,label=r'$\phi=$'+str(rho))
        ax.legend(loc=2, prop={'size':6})
    fig.show()

    fig.savefig(file_name)

    pdb.set_trace()


#########################################################################################
# for single sample x, y is squash(x,B,mu_pop_inv) where B is fixed. for several mu_pop,# 
# assume y came from squash(x,B,mu_pop_inv) and plot how likelilood varis with B        #
#########################################################################################

if True:

    """
    From previous plot, we know that if x is close to 1, and we assume x ~ Beta(mode,$\phi$), the MLE estimate of mode will be biased.  Let's see how this causes the estimate of B to be biased.
    Here, I basically repeat the previous plots where I simulated data and tried to infer B.  However, here there is only 1 datapoint, $x_0=1$, and I let $a_0=\mu_0^a$.
    """

    init_B = 2.0

    file_name = base_folder + 'B_posterior_simple.png'

    x = 1
    mu_pops = [.5,.6,.7,.8]
    rhos = [.01,.04,.07,.1]
    rhos = [.01,.04,.07,.1,.3,.5,.7]
    #rhos = [.1,.3,.5,.7]
    
    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    
    fig.suptitle('posterior of B, x with x=1, true B='+str(init_B))

    Bs = helper.seq(init_B-3.0,init_B+3.0,300)

    for mu_pop,i in zip(mu_pops,range(4)):

        ax = fig.add_subplot(2,2,i+1)
        mu_pop_inv = g_inv(mu_pop)
        y = squash(x,init_B,mu_pop_inv)
        ax.set_title(r'$\mu_{pop}=$'+str(mu_pop)+r',a=%.2f'%y)
        ax.set_xlabel('B')
        ax.set_ylabel(r'$P(B;x_0,a_0,\phi^a$')
        for rho in rhos:
            pdfs = [math.exp(get_beta_p(y,squash(x,aB,mu_pop_inv),rho,'mode')) for aB in Bs]
            ax.plot(Bs,pdfs,label=r'$\phi$='+str(rho))
            ax.axvline(init_B)
        ax.legend(loc=2, prop={'size':6})
    fig.show()

    fig.savefig(file_name)

    pdb.set_trace()


fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(vals, pdfs)

ax.axvline(1)
fig.show()


pdb.set_trace()

model.sample(num_steps,burn=500, tune_throughout=False)



fig = plt.figure()

ax = fig.add_subplot(1,1,1)
ax.hist(model.trace('B')[:],bins=50)
ax.axvline(1)

fig.show()
fig.savefig('/Users/glareprotector/Documents/prostate/hist001.png')
import pdb

pdb.set_trace()
