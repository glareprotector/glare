"""
later on, want to be able to specify a variable name, pid, and get out the value.  need mapping from variable name and pid to VID(when deciding what to name variable).  need mapping from variable name and sample number to VID(when storing results of chain).  need mapping from variable name and (single)pid to variable name.
sampler should spit out list of pids.
function that takes in covariate for single sample, values for B??, returns values for all\?? at specified time step, with variables named with pid passed to function.  output should be a covariate matrix(with pids) and that data structure storing whatever variables we get to observe.  if it's not observed, then later on, set it to unobsered.


so to set the value of every stochastic, have a variable storer class where you can set/retrieve variable values given a name and/or associated pid
also have to set the name (name_func(name, pid)) and init_val(name, pid).  if had a function that 
choose name.  choose value.

"""


import pandas
import numpy.random
import numpy
import pdb

class time_point(object):

    def __init__(self, time, value):
        self.time, self.value = time, value


class attribute_holder(object):
    pass

class variable_manager(object):
    """
    provides way to set and get *values* and *names* of variables in model.  this can be done before the model is created
    also store values of constants/non
    """

    def __init__(self):
        self.val_cache = {}
        self.observed_cache = {}
        self.x_cache = {}
        self.observed_cache_blanket = {}
        self.x_cache = {}
        self.time_point_cache = {}
        self.constants = attribute_holder

    def get_variable_name(seed):
        return seed

    def get_pid_variable_name(seed, pid):
        return seed + '_' + pid

    def set_variable_value(seed, val):
        self.val_cache[get_variable_name(seed)] = val

    def set_pid_variable_value(seed, pid, val):
        self.val_cache[get_pid_variable_name(seed, pid)] = val

    def get_pid_variable_value(seed, pid):
        return self.val_cache[get_pid_variable_name(seed, pid)]

    def get_variable_observed(seed):
        return self.observed_cache[get_variable_name(seed)]

    def set_variable_observed(seed, observed):
        self.observed_cache[get_variable_name(seed)] = observed

    def get_pid_variable_observed(seed, pid):
        try:
            return self.get_pid_variable_observed_blanket(seed):
        except:
            return self.observed_cache[get_pid_variable_name(seed, pid)]

    def set_pid_variable_observed(seed, pid, val):
        self.observed_cache[get_pid_variable_name(seed, pid)] = val

    def get_pid_variable_observed_blanket(seed):
        return self.observed_cache_blanket[seed]

    def set_pid_variable_observed_blanket(seed, val):
        self.observed_cache_blanket[seed] = val

    def set_pid_x(pid, x):
        self.x_cache[pid] = x

    def get_pid_x(pid):
        return self.x_cache[pid]

    def set_pid_x_from_dataframe(X):
        for pid in X.index:
            self.set_pid_x(pid, X.loc[pid])

    def get_pid_iterable():
        return self.x_cache.keys()

    def get_pid_data_times(pid):
        return self.time_point_cache[pid]

    def set_pid_data_times(pid, time_points):
        self.time_point_cache[pid] = time_points

    def get_x_len():
        return len(iter(self.x_cache).next())

    

def var_name_pid_to_vid(var_name, pid):
    return var_name + '_' + pid

class data(object):

    def __init__(self, X, obs):
        self.X, self.obs = X, obs

    def get_value(self, var_name, pid):
        return self.obs[var_name][pid]

class fake_data_getter(object):
    """
    is ultimately able, for input model, generate covariates and joint samples.  input is a one patient model.  assuming all sigmas are 1 for now.
    """
    def get_data(self, a_pop, b_pop, c_pop, B_a, B_b, B_c, l_a, l_b, l_c):

        import get_model
        X_records = []
        obs_records = []


        import matplotlib.pyplot as plt

        num_steps = 100
        num_samples = 50

        """
        for each generated covariate
        """

        for i in range(num_samples):
            x = numpy.random.normal(0, 1)
            temp_X = pandas.DataFrame([[x]], index = [str(i)])
            X_records.append([x])
            X_pop = pandas.Series([0])
            M, pid = get_model.get_model_Bs_fixed(temp_X, X_pop, a_pop, b_pop, c_pop, 1.0, 1.0, 1.0, l_a, l_b, l_c, B_a, B_b, B_c)
            M.sample(num_steps)
            a_val = M.trace(var_name_pid_to_vid('mu_a', pid))[num_steps-1]
            b_val = M.trace(var_name_pid_to_vid('mu_b', pid))[num_steps-1]
            c_val = M.trace(var_name_pid_to_vid('mu_c', pid))[num_steps-1]
            obs_records.append([a_val, b_val, c_val])

        X = pandas.DataFrame.from_records(X_records, index = [str(i) for i in range(num_samples)])
        obs = pandas.DataFrame.from_records(obs_records, index = [str(i) for i in range(num_samples)], columns = ['a', 'b', 'c'])

        d = data(X, obs)


        fig = plt.figure()
        fig.subplots_adjust(hspace = 0.4, wspace = 0.25)

        ax = fig.add_subplot(2,2,1)

        ax.scatter(d.X[0], d.obs['a'])
        ax.set_xlabel('value of the single covariate x')
        ax.set_ylabel('value of a')
        ax.set_title('a')

        ax = fig.add_subplot(2,2,2)

        ax.scatter(d.X[0], d.obs['b'])
        ax.set_xlabel('value of the single covariate x')
        ax.set_ylabel('value of b')
        ax.set_title('b')

        ax = fig.add_subplot(2,2,3)

        ax.scatter(d.X[0], d.obs['c'])
        ax.set_xlabel('value of the single covariate x')
        ax.set_ylabel('value of c')
        ax.set_title('c')

        fig.show()
        fig.savefig('/Users/glareprotector/prostate_git/glare/bin/abc_vs_covariates.png')






        ML = get_model.get_model_abc_observed(X, X_pop, a_pop, b_pop, c_pop, 1.0, 1.0, 1.0, l_a, l_b, l_c, d)

        ML.sample(10000)

        fig = plt.figure()
        fig.subplots_adjust(hspace = 0.4, wspace = 0.25)
        ax = fig.add_subplot(2,2,1)
        import helper
        ax.hist(ML.trace('MM_B_mu_a')[:], bins = 50)
        ax.set_title(r'$B_a$')


        ax = fig.add_subplot(2,2,2)
        ax.hist(ML.trace('MM_B_mu_b')[:], bins = 50)
        ax.set_title(r'$B_b$')


        ax = fig.add_subplot(2,2,3)
        ax.hist(ML.trace('MM_B_mu_c')[:], bins = 50)
        ax.set_title(r'$B_c$')

        fig.show()
        fig.savefig('/Users/glareprotector/prostate_git/glare/bin/Bs.png')
