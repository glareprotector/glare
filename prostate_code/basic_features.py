import pandas
import random
import matplotlib.pyplot as plt
import numpy as np

class feature(object):
    """
    feature is just a class that takes in a tumor or something, and implements callable
    there are abstract classes of which all child classes should have the same interface for generate and maybe other functions
    eventually, will be able to cache calls using a key of feature instance + arguments to generate
    """
    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)

    def generate(self, *args, **kwargs):
        self.check_input(*args, **kwargs)
        ans = self._generate(*args, **kwargs)
        self.error_check(ans)
        return ans

    def check_input(self, *args, **kwargs):
        pass

    def error_check(self, ans):
        pass

    def __len__(self):
        return 1

    def get_name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        try:
            return self.name
        except AttributeError:
            return self.__class__.__name__

    def __init__(self, **kwargs):
        pass


class single_backing_f(feature):

    def __repr__(self):
        return self.backing_f.__repr__()


class range_checked_feature(feature):
    

    def error_check(self, *args, **kwargs):
        pass
        #lower, upper = self.get_valid_range()
        #x = args[0]
        #if x < lower or x
        #if self.get_code(tumor) < lower or self.get_code(tumor) > upper:
        #    raise my_exceptions.ScalarFeatureOutOfRange

    def get_valid_range(self):
        return self.low, self.high

    def __init__(self, low, high, **kwargs):
        self.low = low
        self.high = high
        super(range_checked_feature, self).__init__(**kwargs)



class generic_categorical_feature(feature):
    """
    always based on some feature.  specify that, as well as the possible values
    returns a list
    """

    def error_check(self, *args, **kwargs):
        pass
        #if self.backing_feature(tumor) not in self.get_possible_values():
        #    raise Exception

    def _generate(self, *args):
        import helper
        ans = [1 if helper.compare_in(self.backing_feature(*args), val) else 0 for val in self.get_possible_values()]
        return ans

    def get_possible_values(self):
        return self.possible_values

    def __init__(self, possible_values, backing_feature, category_descriptions = None):
        self.possible_values = possible_values
        self.backing_f = backing_feature
        if category_descriptions == None:
            self.category_descriptions = ['' for i in range(len(self.possible_values))]
        else:
            self.category_descriptions = category_descriptions

    def __len__(self):
        return self.get_num_categories()

    def get_num_categories(self):
        return len(self.get_possible_values())

    def get_category_descriptions(self):
        return self.category_descriptions

    def get_actual_value(self, tumor):
        return self.backing_f(tumor)


class series_getter(feature):
    """
    abstract class whose only requirement is that generate returns a time series.  no restrictions on the arguments to generate
    """
    def error_check(self, ans):
        assert isinstance(ans, my_data_types.timed_list)


class raw_series_getter(series_getter):
    """
    returns the raw series corresponding.  assume no option to specify relative_to_what, or what times you want.  you take what you can get
    """
    def _generate(self, pid):
        raise NotImplementedError, 'this is abstract raw_series_getter class'


class ucla_raw_series_getter_panda(feature):
    """
    returns a panda series with no NA's.  time units is month(assume 30 days a month)
    """
    physical_condition, mental_condition, urinary_function, urinary_bother, bowel_function, bowel_bother, sexual_function, sexual_bother = 2,3,4,5,6,7,8,9
    def __init__(self, column, **kwargs):
        self.old_ucla_raw_series_getter = ucla_raw_series_getter(column)
        super(ucla_raw_series_getter_panda, self).__init__(**kwargs)

    def _generate(self, pid):
        my_series = self.old_ucla_raw_series_getter(pid)
        d = {}
        import my_data_types
        for item in my_series:
            if not isinstance(item, my_data_types.no_value_object):
                d[int(item.get_time().days / 30)] = item / 100.0
        return pandas.Series(d)




class retimed_raw_series(feature):
    """
    feature takes as argument for init, a raw_series getter
    """
    def __init__(self, raw_series_getter, fake_time_zero):
        self.fake_time_zero, self.raw_series_getter = fake_time_zero, raw_series_getter

    def _generate(self, pid):
        raw_series = self.raw_series_getter(pid)
        to_keep = raw_series.loc[raw_series.index >= self.fake_time_zero]
        shift = len(raw_series) - len(to_keep)
        new_index = np.zeros(len(to_keep))
        for i in range(shift, len(raw_series)):
            new_index[i-shift] = raw_series.index[i] - self.fake_time_zero

        to_keep.index = new_index
        return to_keep


class specific_time_value_panda_feature(feature):
    """
    takes in panda series getter and returns value at certain time
    """
    def __init__(self, panda_series_getter, the_time):
        self.panda_series_getter, self.the_time = panda_series_getter, the_time

    def _generate(self, pid):
        try:
            return self.panda_series_getter(pid).loc[self.the_time]
        except Exception, e:
            print e, 'asdf', pid
            raise my_exceptions.NoFxnValueException


class get_abc_parameters_feature(feature):
    """
    accepts curve_getter and initial_level_getter in init, pid in generate
    returns abc parameters subject to constraints that a and b are in [0,1] and c > 0
    """
    def __init__(self, curve_getter_f, initial_level_f, f):
        self.curve_getter_f, self.initial_level_f, self.f = curve_getter_f, initial_level_f, f

    def _generate(self, pid):
        curve = self.curve_getter_f(pid)
        initial_level = self.initial_level_f(pid)
        a = initial_level
        #print curve, initial_level
        def obj_f(x):
            error = 0.0
            for time, value in curve.iteritems():
                error += pow(self.f(time, initial_level, x[0], x[1], x[2]) - value, 2)
            return error

        import scipy.optimize
        x, f, d = scipy.optimize.fmin_l_bfgs_b(obj_f, np.array([0.5, 0.5, 2.0]), approx_grad = True, bounds = [(0.01,.99),[0.01,.99],[0.01,None]])
        #pdb.set_trace()
        return x


class compose(feature):

    def __init__(self, f, g):
        self.f,self.g = f,g

    def _generate(self, *args, **kwargs):
        return self.f(self.g(*args, **kwargs))





class apply_f_g_then_apply_h(feature):

    """
    f gets initialized with same arguments
    """

    def __init__(self, f, g, h):
        self.f,self.g,self.h = f,g,h

    def _generate(self, *args, **kwargs):
        f_result = self.f(*args, **kwargs)
        g_result = self.g(*args, **kwargs)
        return self.h(f_result, g_result)

class get_all_data_feature(feature):

    """
    divides datapoints by initial level.  
    """

    def __init__(self, attribute_fs, curve_getter, initial_level_f, curve_fxn):
        self.attribute_fs, self.curve_getter, self.curve_fxn, self.initial_level_f = attribute_fs, curve_getter, curve_fxn, initial_level_f

    def _generate(self, pid):
        import helper
        a,b,c = get_abc_parameters_feature(self.curve_getter, self.initial_level_f, self.curve_fxn)(pid)
        initial_level = self.initial_level_f(pid)
        data_points = self.curve_getter(pid) 
        x = patient_features_feature(self.attribute_fs)(pid)
        
        the_cov = helper.cov(x, initial_level)

        return helper.all_data(the_cov, a, b, c, data_points)

class get_abc_data_feature(feature):
    """
    given regular attributes, raw_series_getter, returns the abc data.  raises exception if failed
    """
    def __init__(self, attribute_fs, curve_getter, initial_level_f, curve_fxn):
        self.attribute_fs, self.curve_getter, self.curve_fxn, self.initial_level_f = attribute_fs, curve_getter, curve_fxn, initial_level_f

    def _generate(self, pid):
        import helper
        a,b,c = get_abc_parameters_feature(self.curve_getter, self.initial_level_f, self.curve_fxn)(pid)
        initial_level = self.initial_level_f(pid)
        x = patient_features_feature(self.attribute_fs)(pid)
        
        the_cov = helper.cov(x, initial_level)

        return helper.abc_data(the_cov, a, b, c)
        

class get_complete_data_feature(feature):
    """
    given regular attributes, curve_getter, returns 
    """
    def __init__(self, attribute_fs, curve_getter, initial_level_f):
        self.attribute_fs, self.curve_getter, self.initial_level_f = attribute_fs, curve_getter, initial_level_f

    def _generate(self, pid):
        initial_level = self.initial_level_f(pid)
        x = patient_features_feature(self.attribute_fs)(pid)
        curve = self.curve_getter(pid)
        return helper.complete_data(helper.cov(x,initial_level),curve)

class apply_return_as_dict_f(feature):
    """
    applies f supplised to init to every pid in the iterator supplised to generate, and returns dict
    """
    def __init__(self, f):
        self.f = f

    def _generate(self, pid_iterator):
        ans = {}
        for pid in pid_iterator:
            print pid
            try:
                ans[pid] = self.f(pid)
            except my_exceptions.NoFxnValueException:
                pass

        return ans



class normalize_data_dict(feature):
    """
    takes in data_dict_f in init, returns properly normalized data dict
    """
    def __init__(self, data_dict_f):
        self.data_dict_f = data_dict_f

    def _generate(self, pid_iterator):
        d = self.data_dict_f(pid_iterator)
        num_attributes = len(d.iteritems().next()[1].cov.x)

        sums = np.zeros(num_attributes)

        for i in range(num_attributes):
            vals = [data.cov.x[i] for pid,data in d.iteritems()]
            mean = np.mean(vals)
            std = np.std(vals)
            for pid,data in d.iteritems():
                data.cov.x[i] = (data.cov.x[i] - mean) / std
        
        return d
                


"""
raw series 
"""


class plot_function_wrapper(feature):
    """
    takes in a regular function, keyworded arguments for those you want to hard code in init.
    """
    def __init__(self, f, **kwargs):
        self.kwargs = kwargs
        self.f = f

    def _generate(self, **kwargs):
        merged = dict(self.kwargs.items() + kwargs.items())
        self.f(merged)


class fig_with_one_subfig(feature):
    """
    function takes in a function which takes in a subfig and modifies it, and returns a figure with with only that 1 subfig
    """
    def _generate(self, subfig_f):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax = subfig_f(ax)
        return fig

class show_fig_f(feature):
    """
    takes in function that returns a figure.  generate will call it and show the fig
    """
    def __init__(self, f):
        self.f = f

    def _generate(self, **kwargs):
        fig = self.f(**kwargs)
        fig.show()


class save_fig_f(feature):
    """
    takes in function that returns a figure.  saves the figure to specified file
    """
    def __init__(self, f, file_name):
        self.f, self.file_name = f, file

    def _generate(self, **kwargs):
        fig = self.f(**kwargs)
        plt.savefig(self.file)


class fake_raw_series_getter(feature):
    """
    hackish.  takes in normalized data which only has 1 attribute, and returns c * attribute fed through squashing function to get mean of a
    assume that variance of beta is constant
    """
    def __init__(self, normalized_data, c, squashing_f, beta_var, mu_noise_sd, obs_noise_sd, num_samples, avg_a):
        self.normalized_data, self.c, self.squashing_f, self.beta_var, self.mu_noise_sd, self.obs_noise_sd, self.avg_a, self.num_samples = normalized_data, c, squashing_f, beta_var, mu_noise_sd, obs_noise_sd, avg_a, num_samples
        
    def _generate(self, pid):
        import helper, pdb
        age = self.normalized_data.loc[pid]['age']
        mu = self.avg_a + self.squashing_f(self.c*age + random.normalvariate(0, self.mu_noise_sd))
        alpha, beta = helper.beta_mu_v_to_alpha_beta(mu, self.beta_var)
        a_i = random.betavariate(alpha, beta)
        d = {}
        for i in range(self.num_samples):
            d[i] = a_i + random.normalvariate(0, self.obs_noise_sd)
        return pandas.Series(d)


class data_getter(feature):
    
    def __init__(self, series_getter):
        self.series_getter = series_getter

    def _generate(self, pid_iterable):
        d = {}
        for pid in pid_iterable:
            d[pid] = self.series_getter(pid)
        return d
        



class ucla_raw_series_getter(raw_series_getter):
    """
    initalize with the file name and the column number the series lies in
    returns series where the times are my_datedelta objects.  assume that each month is 30 days
    """
    physical_condition, mental_condition, urinary_function, urinary_bother, bowel_function, bowel_bother, sexual_function, sexual_bother = 2,3,4,5,6,7,8,9
    def __init__(self, column, **kwargs):
        self.column = column
        super(ucla_raw_series_getter, self).__init__(**kwargs)

    def _generate(self, pid):
        import ucla_objects, param
        the_dict = wc.get_stuff(ucla_objects.UCLA_raw_series_dict, param.param())
        return the_dict[(pid, self.column)]

class relative_raw_series_getter(raw_series_getter):
    """
    takes in a raw_series_getter, and a time_getter, and returns the series that raw_series gets relative to whatever the time_getter returns
    raises NoFxnValueException if it cannot get the time series or relative_to_date
    """
    def __init__(self, raw_series_getter, time_getter, **kwargs):
        self.raw_series_getter = raw_series_getter
        self.time_getter = time_getter
        super(relative_raw_series_getter, self).__init__(**kwargs)

    def _generate(pid):
        try:
            raw_series = self.raw_series_getter(pid)
        except my_exceptions.NoFxnValueException:
            raise my_exceptions.NoFxnValueException
        try:
            relative_to_time = self.time_getter(pid)
        except my_exceptions.NoFxnValueException:
            raise my_exceptions.NoFxnValueException
        import copy
        ans = copy.deepcopy(raw_series)
        for item in raw_series:
            item.set_time(item.get_time() - relative_to_time)
        return ans
        

class processed_series_getter(series_getter):
    """
    returns a time series with the specified time type and specified time points of that type
    difference between this and raw_series_getter is that here, you know what times you will be getting back
    """
    def _generate(self, pid, times):
        raise NotImplementedError


class processed_exact_time_series_getter(processed_series_getter):
    """
    calls raw_series_getter, and returns a time series where the a raw time point is included at a time point only if the times match exactly
    output_times are same as the times in what raw_series_getter
    """
    def __init__(self, raw_series_getter, **kwargs):
        self.raw_series_getter = raw_series_getter
        super(processed_exact_time_series_getter, self).__init__(**kwargs)

    def _generate(self, pid, times):
        """
        obtains series at the specified times.  note that times is not a timed_list.  it is just a list of times
        """
        raw_series = self.raw_series_getter(pid)

        ans = []
        for time in times:
            found = False
            for item in raw_series:
                assert type(item.get_time()) == type(time) # only has to be true for this particular processed_series_getter
                if item.get_time() == time:
                    ans.append(item)
                    found = True
                    break
            if not found:
                ans.append(my_data_types.timed_no_value_object(time = time))
        return my_data_types.timed_list(ans)
                          



class processed_interval_time_series(processed_series_getter):
    """
    returns a time series where the times are the specified time intervals.  the label for each interval is determined by applying label function to the
    time points that fall into the interval
    """
    def __init__(self, series_getter_instance, aggregate_feature_instance, **kwargs):
        import aggregate_features
        assert isinstance(series_getter_instance, series_getter)
        assert isinstance(aggregate_feature_instance, aggregate_features.aggreagte_feature)
        super(processed_interval_time_series, self).__init__(**kwargs)
    
    def _generate(self, pid, intervals):
        """
        assume that interval.contains works on the times in raw_series
        """
        raw_series = self.series_getter(pid)
        import my_data_types, aggregate_features as af
        bucket_list = my_data_types.bucket_timed_list.init_from_time_intervals_and_timed_list(intervals, raw_series)
        print bucket_list
        interval_series = bucket_list.apply_feature_always_add(self.aggregate_feature)
        return interval_series



class single_time_processed_time_series(feature):
    """
    __init__ takes in a processed_series_getter, and generate takes in a single time.  returns the value for that time
    want to be able to treat this as a pid feature.  therefore, generate should only take one argument - the pid
    """
    def __init__(self, processed_series_getter, time, **kwargs):
        self.processed_series_getter = processed_series_getter
        self.time = time
        super(single_time_processed_time_series, self).__init__(**kwargs)

    def _generate(self, pid_for_processed_series):
        return self.processed_series_getter.generate(pid_for_processed_series, [self.time])[0]


class aggregate_processed_series_getter(processed_series_getter):
    """
    should never raise exception
    instead of having a list of pids, just need to have a iterable whose iterator returns pids
    """

    def __init__(self, processed_series_getter, aggregate_feature, **kwargs):
        self.processed_series_getter = processed_series_getter
        self.aggregate_feature = aggregate_feature
        super(aggregate_processed_series_getter, self).__init__(**kwargs)

    def _generate(self, pid_iterable, times):
        import my_data_types, aggregate_features

        bl = my_data_types.bucket_timed_list.init_empty_bucket_timed_list_with_specified_times(times)
        for pid in pid_iterable:
            processed_series = self.processed_series_getter(pid, times)
            bl.lay_in_matching_timed_list(processed_series)
        ans = bl.apply_feature_always_add(self.aggregate_feature)
        return ans


class pid_iterable(object):
    """
    abstract class
    iteratable whose iterator goes returns a sequence of pids
    """
    def __iter__(self):
        raise NotImplementedError

    def next(self):
        raise NotImplementedError

class pid_iterable_from_iterable(pid_iterable):

    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return iter(self.iterable)



"""
1st feature: plugging data directly into model.  requires no processing besides maybe setting time 1 stuff to be the new 0.
2nd feature: should let time 1 stuff be time 0.  well, for both, need a feature that extracts raw series, and retimes the times
"""





class all_ucla_pid_iterable(pid_iterable):

    def __iter__(self):
        return iter(self.pid_list)
    
    def dummy(self):
        print 'all_ucla_pid_iterable'

    def __init__(self):
        # just gets ucla pid list from wc.
        import ucla_objects
        p = param()
        self.pid_list = wc.get_stuff(ucla_objects.UCLA_patient_list, p)
        super(all_ucla_pid_iterable,self).__init__()







class restricted_pid_iterable(pid_iterable):

    def __init__(self, backing_iterable, limit):
        self.backing_iterable = backing_iterable
        self.limit = limit

    def __iter__(self):
        """
        returns generator object that stops after at most self.limit entries
        """
        count = 0
        for pid in self.backing_iterable:
            if count == self.limit:
                break
            yield pid
            count += 1

class filtered_pid_iterable(pid_iterable):

    def __init__(self, backing_iterable, filtering_f):
        self.backing_iterable = backing_iterable
        self.filtering_f = filtering_f
        super(filtered_pid_iterable, self).__init__()

    def dummy(self):
        print 'filtered_pid_iterable'


    def __iter__(self):
        """
        this will return a generator object
        only yields a pid if no exception is raised and filtering_f on pid is True
        """
        for pid in self.backing_iterable:
            import pdb
            try:
                if self.filtering_f(pid):
                    #print pid
                    yield pid
            except my_exceptions.NoFxnValueException:
                pass

class no_exception_pid_iterable(pid_iterable):
    """
    returns pid iterable where a pid is returned if the supplied function does not raise exception
    """
    def __init__(self, backing_iterable, test_f):
        self.backing_iterable = backing_iterable
        self.test_f = test_f

    def __iter__(self):
        for pid in self.backing_iterable:
            try:
                temp = self.test_f(pid)
            except my_exceptions.NoFxnValueException:
                pass
            else:
                yield pid


class hard_coded_f(feature):

    def __init__(self, val, **kwargs):
        self.val = val
        super(hard_coded_f, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        return self.val

class feature_applier(feature):
    """
    applies feature to pids in pid_iterable
    returns a my_list, since these points are not ordered
    correction: now return a panda series where the row labels are the pids
    should never be putting a no_value_object into the series.  this means i don't have to decorate the input f - it is automatically decorated
    """
    def __init__(self, apply_f, **kwargs):
        import helper
        self.apply_f = always_raise(apply_f)
        super(feature_applier, self).__init__(**kwargs)

    def _generate(self, pid_iterable):
        import my_data_types, pandas
        vals = []
        indicies = []
        for pid in pid_iterable:
            try:
                ans = self.apply_f(pid)
            except my_exceptions.NoFxnValueException:
                pass
            else:
                vals.append(ans)
                indicies.append(pid)
        asdf = pandas.Series(vals, index = indicies)
        return asdf



class single_filter_f(single_backing_f):
    """
    takes in a backing f.  raises exception if the output is not "ok"
    """
    def __init__(self, backing_f, **kwargs):
        self.backing_f = backing_f
        super(single_filter_f, self).__init__(**kwargs)

class filter_by_explicit_cutoff_f(single_filter_f):

    def __init__(self, low, high, backing_f, **kwargs):
        self.low, self.high = low, high
        super(filter_by_explicit_cutoff_f, self).__init__(backing_f, **kwargs)

    def _generate(self, *args, **kwargs):
        ans = self.backing_f(*args, **kwargs)
        if ans < self.low or ans > self.high:
            import my_exceptions
            raise my_exceptions.NoFxnValueException
        else:
            return ans



class filter_f(single_backing_f):
    """
    takes in a backing f, and filters the output
    """
    def __init__(self, backing_f, **kwargs):
        self.backing_f = backing_f
        super(filter_f, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        raise NotImplementedError

class remove_outlier_f(filter_f):
    pass

class remove_outlier_by_explicit_cutoff(filter_f):
    """
    assumes that values returned by backing_f are scalars
    removes values in the list outside of specified range
    for now, assume that backing_f returns a panda series.  this means that i don't have to check if each val is a no_value_type because series can't have those
    """
    def __init__(self, low, high, backing_f, **kwargs):
        self.low, self.high = low, high
        super(remove_outlier_by_explicit_cutoff, self).__init__(backing_f, **kwargs)

    def _generate(*args, **kwargs):
        raw_vals = self.backing_f(*args, **kwargs)
        d = {}
        ok = raw_vals < self.high & raw_vals > self.low
        return raw_vals.loc[ok]
                


class cross_feature(feature):
    """
    takes in a list of features, and returns a my_list of their results.
    returns a my_tuple because i actually know how to plot a my_tuple if it is 2 dimensions
    returns no_value_object if any of the features raises exception or returns no_value_object
    """
    def __init__(self, *args, **kwargs):
        self.features = args
        super(cross_feature, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        import my_data_types
        ans = []
        import helper
        for f in self.features:
            try:
                ans.append(helper.raise_NoFxnValueException_dec(f)(*args, **kwargs))
            except my_exceptions.NoFxnValueException:
                return my_data_types.no_value_object()
        return my_data_types.my_tuple(ans)


class always_one(feature):
    """
    always returns 1.  to use for bias in regression
    """
    def _generate(self, *args, **kwargs):
        return 1

class indicator_feature(single_backing_f):
    """
    takes in a feature and a target value.  returns 1 if the feature value and target value are the same
    may also raise exception if there is no value from backing_feature
    """
    def __init__(self, backing_feature, target_value, **kwargs):
        self.backing_f = backing_feature
        self.target_value = target_value
        super(indicator_feature, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        ans = self.backing_f(*args, **kwargs)
        if ans == self.target_value:
            return 1
        else:
            return 0


class range_indicator_feature(single_backing_f):
    """
    takes in a scalar feature and a target high/low.  returns 1 if the low < feature_value <= high
    """
    def __init__(self, backing_feature, low, high, **kwargs):
        self.backing_f, self.low, self.high = backing_feature, low, high
        super(range_indicator_feature, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        import pdb
        ans = self.backing_f(*args, **kwargs)
        if ans <= self.high and self.low < ans:
            return 1
        else:
            return 0


class and_indicator_feature(feature):
    """
    takes in multiple indicator feature(all taking same arguments) and returns 1 if all of them are true
    if one of the features raises exception, return 0
    """
    def __init__(self, *args, **kwargs):
        self.features = args
        super(and_indicator_feature, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        import my_exceptions
        for f in self.features:
            try:
                if not f(*args, **kwargs):
                    return 0
            except my_exceptions.NoFxnValueException:
                return 0
        return 1

class function_feature(feature):
    """
    takes in a function, features, and computes function of the output of the features
    assumes that each of the features takes in the same arguments(those passed to the function call)
    """
    def __init__(self, f, *args, **kwargs):
        self.f = f
        self.fs = args
        super(function_feature, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        results = [f(*args, **kwargs) for f in self.fs]
        return self.f(*results)




class always_raise(single_backing_f):
    """
    takes in a feature and becomes one that raises exception when no_value_object is returned
    sets its own name to that of backing_f
    """
    def __init__(self, backing_f, **kwargs):
        self.backing_f = backing_f
        super(always_raise, self).__init__(**kwargs)

    def _generate(self, *args, **kwargs):
        import my_exceptions, my_data_types
        try:
            ans = self.backing_f(*args, **kwargs)
        except my_exceptions.NoFxnValueException:
            raise my_exceptions.NoFxnValueException
        else:
            if isinstance(ans, my_data_types.no_value_object):
                raise my_exceptions.NoFxnValueException
            else:
                return ans
        assert False


class bin_specifier_feature(feature):
    """
    takes in a iterable and returns what to use for the bin argument in hist (could be int or list)
    """
    def _generate(self, vals):
        raise NotImplementedError

class int_bin_specifier_feature(bin_specifier_feature):
    """
    optional init arguments are min/max/avg count per bin
    """
    def __init__(self, avg_count = None, min_val = None, max_val = None, **kwargs):
        self.avg_count = avg_count
        self.min_val = min_val
        self.max_val = max_val
        super(int_bin_specifier_feature, self).__init__(**kwargs)

    def _generate(self, bucket):
        avg_count = self.avg_count if self.avg_count else 10
        min_val = int(self.min_val) if self.min_val else int(min(bucket))
        max_val = int(self.max_val) if self.max_val else int(max(bucket)) + 1
        actual_bin_size = max(int((max_val - min_val) / (len(bucket) / avg_count)), 1)
        bins = range(min_val, max_val+1, actual_bin_size)
        return bins


class data_frame_feature(feature):
    """
    takes in a list of features that takes in the output of the input iterator, and outputs a dataframe.
    """
    def __init__(self, feature_list):
        self.feature_list = feature_list

    def _generate(self, iterable):
        import pandas, helper, my_exceptions
        from numpy import nan
        df = pandas.DataFrame(index = [x for x in iterable])
        
        for f in self.feature_list:
            df[str(f)] = feature_applier(f)(iterable)

        return df





class patient_features_feature(feature):
    """
    given patient id, feature_list, returns features for that patient.  raises NoFxnValueException if any of the features are missing
    returns a pandas Series where the index is the feature name
    assumes features have __str__ implemented
    """
    def __init__(self, feature_list):
        self.feature_list = feature_list

    def _generate(self, pid):
        indicies = [str(f) for f in self.feature_list]
        
        try:
            vals = [f(pid) for f in self.feature_list]
        except my_exceptions.NoFxnValueException, e:
            raise my_exceptions.NoFxnValueException
        else:
            return pandas.Series(vals, index = indicies)

class data_frame_feature_alternate(feature):
    """
    does same thing as data_frame_feature, but populates the DataFrame row by row instead of column by column
    """

    def __init__(self, feature_list, **kwargs):
        self.feature_list = feature_list
        super(data_frame_feature_alternate, self).__init__(**kwargs)

    def _generate(self, iterable):
        records = []
        indicies = [str(f) for f in self.feature_list]
        used_pids = []
        for pid in iterable:
            try:
                records.append(patient_features_feature(self.feature_list)(pid))
                used_pids.append(pid)
            except my_exceptions.NoFxnValueException:
                pass
        return pandas.DataFrame.from_records(records, columns = indicies, index = used_pids)


class series_f(feature):
    """
    does something to a series and returns another series
    """
    pass

class normalize_series_by_max_f(series_f):
    """
    centers covariate relative to its mean, then divide by max element
    """
    def _generate(self, series):
        import aggregate_features as af
        mean = af.get_bucket_mean_feature()(series)
        series = series.apply(lambda x: x - mean)
        abs_series = series.apply(lambda x: abs(x))
        max_val = af.get_bucket_max_feature()(abs_series)
        normalized_series = series.apply(lambda x: x / max_val)
        return normalized_series

class apply_f_to_df_column_f(feature):
    """
    applies feature to each row of a dataframe
    """
    def __init__(self, parent_f, column_f, **kwargs):
        self.parent_f = parent_f
        self.column_f = column_f
        super(apply_f_to_df_column_f, self).__init__(**kwargs)

    def _generate(self, iterable):
        df = self.parent_f(iterable)
        return df.apply(self.column_f, axis=0)

class normalized_data_frame_f(feature):
    """
    takes in list of features, pid_iterable, and returns dataframe where each attribute is normalized to have mean 0, sd 1
    """
    def __init__(self, data_frame_f, **kwargs):
        self.data_frame_f = data_frame_f
        super(normalized_data_frame_f, self).__init__(**kwargs)

    def _generate(self, iterable):
        import aggregate_features as af
        df = self.data_frame_f(iterable)
        meaner = dataset_aggregate_f(af.get_bucket_mean_feature(), self.data_frame_f)
        sder = dataset_aggregate_f(af.get_bucket_sd_feature(), self.data_frame_f)
        means = meaner(iterable)
        sds = sder(iterable)
        for idx in df.columns:
            f = lambda x: (x - means[idx]) / sds[idx]
            df[idx] = df[idx].apply(f)
        return df

class dataset_aggregate_f(feature):
    """
    takes in pid iterable as  argument, aggregate feature and dataframe returning feature in __init__, and returns pandas Series where each feature has been aggregated
    """
    def __init__(self, aggregate_f, data_frame_f, **kwargs):
        self.aggregate_f = aggregate_f
        self.data_frame_f = data_frame_f
        super(dataset_aggregate_f, self).__init__(**kwargs)

    def _generate(self, iterable):
        df = self.data_frame_f(iterable)
        indicies = df.columns
        vals = [self.aggregate_f(df[idx]) for idx in indicies]
        return pandas.Series(vals, index = indicies)
            


class avg_curve_parameters_f(feature):
    """
    takes in pid iterable and returns a tuple of average curve parameters.  for now, just returns numbers i made up
    """
    def _generate(self, iterable):
        import pandas
        return pandas.Series({'a':0.8, 'c':2, 'b':0.2})



class run_CV(feature):
    """
    takes in dataframe, CV iterator, attribute dataframe, target value series, metric function.  just calls sklearn's cross_validation.cross_val_score for now
    """
    def _generate(self, model_builder, attributes, target, cv_iterator, score_func):
        from sklearn import cross_validation
        return cross_validation.cross_val_score(model_builder, attributes, target, cv = cv_iterator, score_func = score_func)



import my_exceptions
import my_data_types
import global_stuff
import pdb
from param import param
import pandas

import aggregate_features as af



# import might cause problems
import wc
#import objects
