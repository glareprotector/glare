import my_exceptions
import pdb



def get_ordered_equivalent(val):

    if isinstance(val, int):
        return timed_int
    elif isinstance(val, float):
        return timed_float
    elif isinstance(val, my_list):
        return timed_bucket
    elif isinstance(val, no_value_object):
        return timed_no_value_object
    assert False

class my_list(list):

    @classmethod
    def get_class(cls):
        return cls

    def __repr__(self):
        ans = '{'
        for item in self:
            ans = ans + repr(item) + ' '
        ans = ans + '}'
        return ans

    def __init__(self, *args, **kwargs):
        """
        because my_list can be the parent of a timed_object, whose __new__ takes in both the time value and actual init value,
        both of those things will be passed to init, which is too much for the original list.  so have to have my own __init__
        that just gets rid of the arguments that don't matter
        """
        super(my_list, self).__init__(*args)

    def apply_feature(self, f):
        """
        returns my_list or child class of it, where each element is f applied to each element as a whole
        does not add object if exception is raised.  still adds object is f returns no_value_object
        """

        ans = my_list()
        import helper
        for item in self:
            try:
                candidate = f(item)
            except my_exceptions.NoFxnValueException:
                pass
            except AssertionError:
                pdb.set_trace()
            else:
                ans.append(candidate)
        return ans

    def apply_feature_always_add(self, f):
        """
        same as apply_feature, except if NoFxnValueException is raised, a ordered_no_value_object is added
        """
        ans = my_list()
        for item in self:
            try:
                assert isinstance(item, timed_object)
                candidate = f(item)
            except my_exceptions.NoFxnValueException:
                ans.append(ordered_no_value_object(item.get_time()))
            except AssertionError:
                pdb.set_trace()
            else:
                ans.append(candidate)
        return ans

    def apply_feature_no_catch(self, f):
        ans = my_list()
        for item in self:
            candidate = f(item)
            ans.append(candidate)
        return ans


class no_value_object(object):
    """
    supports no operations.  so define both __add__ and __radd__ and all other regular/reflected operations to raise the NoFxnValueException
    """

    def __new__(cls, *args, **kwargs):
        inst = super(no_value_object, cls).__new__(cls, *args, **kwargs)
        return inst

    def __init__(self, *args, **kwargs):
        pass

    def __add__(self, other):
        raise my_exceptions.NoFxnValueException

    def __radd__(self, other):
        raise my_exceptions.NoFxnValueException

    def __mul__(self, other):
        raise my_exceptions.NoFxnValueException

    def __rmul__(self, other):
        raise my_exceptions.NoFxnValueException

    def __sub__(self, other):
        raise my_exceptions.NoFxnValueException

    def __rsub__(self, other):
        raise my_exceptions.NoFxnValueException

    def __div__(self, other):
        raise my_exceptions.NoFxnValueException

    def __rdiv__(self, other):
        raise my_exceptions.NoFxnValueException

    def __repr__(self):
        return 'NA'

    def __lt__(self, other):
        raise my_exceptions.NoFxnValueException

    def __gt__(self, other):
        raise my_exceptions.NoFxnValueException

    def __eq__(self, other):
        raise my_exceptions.NoFxnValueException

    def __neq__(self, other):
        raise my_exceptions.NoFxnValueException
    
class timed_object(object):
    """
    supply time as named argument
    assumes that parent class's __new__ takes whatever is in *args
    """
    def __new__(cls, *args, **kwargs):
        inst = super(timed_object, cls).__new__(cls, *args)
        inst.time = kwargs['time']
        return inst

    def get_time(self):
        return self.time

    def __lt__(self, other):
        if not isinstance(other, timed_object):
            return NotImplemented
        return self.get_time() < other.get_time()

    def __gt__(self, other):
        if not isinstance(other, timed_object):
            return NotImplemented
        return self.get_time() > other.get_time()


    def __eq__(self, other):
        if not isinstance(other, timed_object):
            return NotImplemented
        return self.get_time() == other.get_time()

class timed_int(timed_object, int):
    pass

class timed_float(timed_object, float):
    pass

class timed_bucket(timed_object, my_list):
    pass

class timed_no_value_object(timed_object, no_value_object):
    pass


class time_subsetter(object):
    """
    implements the contains method, which takes in a timed_object instance, and returns a boolean of whether the instance is 'in' the subset 
    """
    def contains(self, timed_object_inst):
        raise NotImpelementedError

class exact_time(timed_object, time_subsetter):
    """
    contains a timed_object instance only if their times are exactly the same
    """
    def contains(self, timed_object_inst):
        assert isinstance(timed_object_inst, timed_object)
        if self.get_time() == timed_object_inst.get_time():
            return True
        else:
            return False



class time_interval(time_subsetter):

    def contains(self, timed_object_inst):
        if not isinstance(timed_object_inst, timed_object):
            return False
        try:
            return timed_object_inst.get_time() >= self.low and timed_object_inst.get_time() < self.high
        except my_exceptions.NoFxnValueException:
            return False

    def __init__(self, low, high):
        self.low = low
        self.high = high

    def __repr__(self):
        return '('+repr(self.low)+'/'+repr(self.high)+')'



class timed_list(my_list):
    """
    each element is an timed_object
    """

    def sort_by_time(self):
        self.sort(key = lambda x: x.get_time())
        return my_list.__iter__(self)

    def __iter__(self):
        pdb.set_trace()
        self.sort()
        return my_list.__iter__(self)

    def apply_feature(self, f):
        import helper
        g = helper.attach_time_dec(f)
        return timed_list(my_list.apply_feature(self, g))

    def apply_feature_always_add(self, f):
        import helper
        g = helper.attach_time_dec(f)
        return timed_list(my_list.apply_feature_always_add(self, g))

    def apply_feature_no_catch(self, f):
        import helper
        g = helper.attach_time_dec(f)
        return timed_list(my_list.apply_feature_no_catch(self, g))

class bucket_timed_list(timed_list):

    @classmethod
    def init_from_time_intervals_and_timed_list(cls, intervals, l):
        """
        assumes l is a timed_list, and interval units are same as the time_values of the timed_list
        """
        ans = list()
        for interval in intervals:
            temp = my_list()
            for item in l:
                if interval.contains(item):
                    temp.append(item)
            ans.append(timed_bucket(interval, temp))
        return cls(ans)

    @classmethod
    def init_empty_bucket_timed_list_with_specified_times(cls, times):
        ans = list()
        for time in times:
            ans.append(timed_bucket(my_list(), time=time))
        return cls(ans)

    def lay_in_matching_timed_list(self, to_add):
        #assert len(to_add) == len(self)
        for timed_bucket_instance in self:
            for item in to_add:
                if timed_bucket_instance.get_time() == item.get_time():
                    timed_bucket_instance.append(item)

        """
        for timed_bucket_instance, item in zip(self, to_add):
            assert timed_bucket_instance.get_time() == item.get_time()
            timed_bucket_instance.append(item)
        """

                      







# same as regular dictionary, except that key and value type are specified at init
class IO_dict(dict):

    def __init__(self, key_cls, val_cls, data = {}):
        self.key_cls = key_cls
        self.val_cls = val_cls
        dict.__init__(self, data)

    @classmethod
    def init_from_str(cls, key_cls, val_cls, the_string):
        #assume that keys are on their own line, and the line begins with $$KEY$$
        m = {}
        s = the_string.split('\n')
        i = 0
        key_str = s[0].strip().split('|')[0]
        assert key_str == '$$KEY$$'
        pdb.set_trace()
        while i < len(s):
            if s[i].strip().split('|')[0] == '$$KEY$$':
                key_str = s[i].strip().split('|')[1]
                key = init_from_str(key_cls, key_str)
                val_str = ''
            else:
                val_str = val_str + s[i]
            if i == len(s)-1 or s[i+1].strip().split('|')[0] == '$$KEY$$':
                val = init_from_str(val_cls, val_str)
                m[key] = val
                
            i += 1

        return cls(key_cls, val_cls, m)

    def __str__(self):
        ans = ''
        for key in self:
            ans = ans + '$$KEY$$' + '|' + str(key) + '\n'
            ans = ans + str(self[key]) + '\n'
        return ans
