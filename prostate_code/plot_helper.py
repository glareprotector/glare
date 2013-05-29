import matplotlib.pyplot as plt
import numpy as np
import pdb

def plot_1d_likelihoods(out_file, ba_test_vals, bb_test_vals, bc_test_vals, model, pos = 0):

    """
    varies the pos coordinate of B_a, B_b, B_c according to ba_test_vals, etc, and plots the likelihood, with other variables fixed
    """
    orig_Ba = model.get_node('B_a').value.copy()
    orig_Bb = model.get_node('B_b').value.copy()
    orig_Bc = model.get_node('B_c').value.copy()

    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    dot_size = .1

    """
    modulate B_a[pos]
    """
    
    ba_log_ps = []

    for ba_test in ba_test_vals:
        Ba_test = orig_Ba.copy()
        Ba_test[pos] = ba_test
        model.get_node('B_a').value = Ba_test
        ba_log_ps.append(model.logp)
    
    ax = fig.add_subplot(2,2,1)
    ax.scatter(ba_test_vals, ba_log_ps, s = dot_size)
    ax.set_xlabel('b_a value')
    ax.set_ylabel('logp')
    ax.set_title('b_a vs logp')

    model.get_node('B_a').value = orig_Ba

    """
    modulate B_b[pos]
    """


    bb_log_ps = []

    for bb_test in bb_test_vals:
        Bb_test = orig_Bb.copy()
        Bb_test[pos] = bb_test
        model.get_node('B_b').value = Bb_test
        bb_log_ps.append(model.logp)
    
    ax = fig.add_subplot(2,2,2)
    ax.scatter(bb_test_vals, bb_log_ps, s = dot_size)
    ax.set_xlabel('b_b value')
    ax.set_ylabel('logp')
    ax.set_title('b_b vs logp')

    model.get_node('B_b').value = orig_Bb


    """
    modulate B_c[pos]
    """


    bc_log_ps = []

    for bc_test in bc_test_vals:
        Bc_test = orig_Bc.copy()
        Bc_test[pos] = bc_test
        model.get_node('B_c').value = Bc_test
        bc_log_ps.append(model.logp)
    
    ax = fig.add_subplot(2,2,3)
    ax.scatter(bc_test_vals, bc_log_ps, s = dot_size)
    ax.set_xlabel('b_c value')
    ax.set_ylabel('logp')
    ax.set_title('b_c vs logp')

    model.get_node('B_c').value = orig_Bc

    fig.savefig(out_file)
    fig.show()
    



def plot_contour_2d(out_file, ba_test_vals, bb_test_vals, model, mle_a, mle_b, pos = 0):

    """
    varies B_a[pos] and B_b[pos], plots likelihood, with all other variables fixed
    returns the contour axis so I can add modifications later if desired
    """

    fig=plt.figure()
    first, second = np.meshgrid(ba_test_vals, bb_test_vals)
    likelihoods = np.ndarray((len(bb_test_vals),len(ba_test_vals)))

    orig_Ba = model.get_node('B_a').value.copy()
    orig_Bb = model.get_node('B_b').value.copy()

    for ba,i in zip(ba_test_vals,range(len(ba_test_vals))):
        for bb,j in zip(bb_test_vals,range(len(bb_test_vals))):

            test_Ba = orig_Ba.copy()
            test_Ba[pos] = ba
            test_Bb = orig_Bb.copy()
            test_Bb[pos] = bb


            model.get_node('B_a').value = test_Ba
            model.get_node('B_b').value = test_Bb

            likelihoods[j,i] = model.logp


    ax = fig.add_subplot(111)

    ax.contour(first, second, likelihoods, 80)


    circle = plt.Circle((mle_a, mle_b),radius=.2)
    ax.add_patch(circle)
    ax.axhline(orig_Bb[pos], alpha=1, lw=3)
    ax.axvline(orig_Ba[pos], alpha=1, lw=3)

    fig.savefig(out_file)
    fig.show()




def plot_curves(out_file, Xs, B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c, time_points, max_time):

    import get_model_new as get_model

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    import helper
    for X in Xs:
        a,b,c = get_model.get_deterministic_abc_given_x_and_Bs(helper.cov(X,1.0), B_a, B_b, B_c, mu_pop_a, mu_pop_b, mu_pop_c)
        get_model.add_curve(ax, 1.0, a, b, c, max_time, time_points)
    fig.suptitle('simulated curves')
    fig.savefig(out_file)
    fig.show()




def plot_Bs_histogram(out_file, sampled_model):

    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    fig.suptitle('histogram of Bs')
    num_bins = 50

    B_a_vals = sampled_model.trace('B_a')[:]
    ax = fig.add_subplot(2,2,1)
    ax.hist(B_a_vals, bins = num_bins)
    ax.set_xlabel('B_a value')

    B_b_vals = sampled_model.trace('B_b')[:]
    ax = fig.add_subplot(2,2,2)
    ax.hist(B_b_vals, bins = num_bins)
    ax.set_xlabel('B_b value')

    B_c_vals = sampled_model.trace('B_c')[:]
    ax = fig.add_subplot(2,2,3)
    ax.hist(B_c_vals, bins = num_bins)
    ax.set_xlabel('B_c value')

    fig.savefig(out_file)
    fig.show()




def plot_Bs_trace(out_file, sampled_model):

    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    fig.suptitle('trace of Bs')

    B_a_vals = sampled_model.trace('B_a')[:]
    ax = fig.add_subplot(3,1,1)
    ax.plot(B_a_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel('B_a value')

    B_b_vals = sampled_model.trace('B_b')[:]
    ax = fig.add_subplot(3,1,2)
    ax.plot(B_b_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel('B_b value')

    B_c_vals = sampled_model.trace('B_c')[:]
    ax = fig.add_subplot(3,1,3)
    ax.plot(B_c_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel('B_c value')

    fig.show()
    fig.savefig(out_file)




def plot_logp_trace(out_file, sampled_model):

    num_samples = sampled_model.trace(iter(sampled_model.stochastics).next().__name__).length()
    log_ps = np.zeros(num_samples)

    for i in xrange(num_samples):

        for var in sampled_model.stochastics:
            """
            set value of variables to the trace value
            """
            var.value = sampled_model.trace(var.__name__)[i]

        log_ps[i] = sampled_model.logp

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_title('log_p trace')
    ax.set_xlabel('iteration')
    ax.set_ylabel('log_p')
    ax.plot(log_ps)

    fig.savefig(out_file)
    fig.show()




def plot_rho_trace(out_file, sampled_model):


    rho_a_vals = sampled_model.trace('rho_a')[:]
    rho_b_vals = sampled_model.trace('rho_b')[:]
    rho_c_vals = sampled_model.trace('rho_c')[:]
    rho_noise_vals = sampled_model.trace('rho_noise')[:]



    fig = plt.figure()
    fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
    fig.suptitle(r'trace of $\phi$s')


    ax = fig.add_subplot(4,1,1)
    ax.plot(rho_a_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_a$ val')

    ax = fig.add_subplot(4,1,2)
    ax.plot(rho_b_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_b$ val')

    ax = fig.add_subplot(4,1,3)
    ax.plot(rho_c_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_c$ val')

    ax = fig.add_subplot(4,1,4)
    ax.plot(rho_noise_vals)
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'$rho_{noise}$ val')
    
    fig.show()
    fig.savefig(out_file)
