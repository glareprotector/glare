class my_list(list):

    @classmethod
    def get_class(cls):
        return cls

    def __repr__(self):
        ans = ''
        for item in self:
            ans = ans + repr(item) + '\n'
        return ans

    # NOTE: think about how this should be organized when i have time.  maybe have a class that pairs an object with the kind of list that holds it
    def apply_feature(self, f, cls = self.get_class()):
        """
        returns my_list or child class of it, where each element is f applied to each element as a whole
        f should either return single_value_object or raise exception.  here, item isn't added if exception raised.  elsewhere, entire function raises that exception
        """
        ans = cls()
        for item in self:
            candidate = f.generate(item)
            try:
                candidate.get_value()
            except my_exceptions.NoFxnValueException:
                pass
            else:
                ans.append(candidate)
        return ans

    def apply_feature_no_catch(self, f, cls = self.get_class()):
        ans = cls()
        for item in self:
            candidate = f.generate(item)
            candidate.get_value()
        return ans

# note: to be safe, when creating a my_list or child class of it and passing in an argument, always use basic list, or a parent_class object at least

class ordered_object(object):

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __eq__(self, other):
        pass

class base_single_ordinal_ordered_object(ordered_object):
    """
    ordered_object where the comparison is based on attribute that can be retrieved with get_ordinal member function
    """
    def get_ordinal(self):
        pass

    def __lt__(self, other):
        return self.get_ordinal() < other.get_ordinal()

    def __gt__(self, other):
        return self.get_ordinal() > other.get_ordinal()

    def __eq__(self, other):
        return self.get_ordinal() == other.get_ordinal()


class base_single_value_object(object):

    def get_value(self):
        pass

    def set_value(self, val):
        pass


class no_value_object(base_single_value_object):

    def __init__(self):
        pass

    def get_value(self):
        raise my_exceptions.NoFxnValueException


class single_value_object(base_single_value_object):

    def __init__(self, val):
        self.val = val

    def get_value(self):
        return self.val

    def set_value(self, val):
        self.val = val


class base_single_ordinal_single_value_ordered_object(base_ordinal_ordered_object, base_single_value_object):

    pass


class single_ordinal_single_value_ordered_object(base_single_ordinal_single_value_ordered_object, single_value_object):

    def __init__(self, ordinal, val):
        self.ordinal = ordinal
        single_value_object.__init__(self, val)

    def get_ordinal(self):
        return self.ordinal


class ordered_interval(ordered_object):

    def contains(self, item):
        return item.get_ordinal() >= self.low and item.get_ordinal() < self.high

    def __init__(self, low, high):
        self.low = low
        self.high = high

    def __lt__(self, other):
        return self.low < other.low

    def __gt__(self, other):
        return self.low < other.low

    def __repr__(self):
        return '('+repr(self.low)+'/'+repr(self.high)+')'


class ordinal_list(my_list):
    """
    each element is an ordered_object, which are just comparable objects.  comparison might be done based on objects with get_ordinals() function, but doesn't have to be
    """

    def __iter__(self):
        self.sort()
        return self


class single_ordinal_ordinal_list(my_list):
    """
    holds items where the ordinal comparison is based on single attribute retrieved with get_ordinals
    """
    def get_ordinals(self):
        ans = ordered_list()
        for item in self:
            ans.append(item.get_ordinal())
        return ans    
               
class bucketed_list(my_list):
    """
    list where each element is a single_value_object, and get_value() returns a iterable
    """
    pass

class bucketed_ordinal_list(ordinal_list, bucketed_list):
    """
    now, each element is also a single_ordinal element, and the ordinal is an interval.  could make parent more general classes, but i'm not going to use them
    """
    @classmethod
    def init_from_intervals_and_ordinal_list(cls, intervals, l):
        """
        assumes l is a ordinal_list.  so l might be 
        """
        ans = list()
        for interval in intervals:
            temp = my_list()
            for item in l:
                if interval.contains(item):
                    temp.append(item)
            ans.append(single_ordinal_single_value_ordered_object(interval, temp))
        return cls(ans)

    @classmethod
    def init_from_homo_my_list_list(cls, hll):
        """
        takes in homo_my_list_list, returns bucketed_ordinal_list, where each element is single_ordinal, and single_valued.  don't have a specific class for this type, but could, if there is a function that requires this type.  but could also keep track mentally of what specializing of the class this actually returns
        """
        for  in hll.get_ordinals():
            temp = my_list()
            

# NOTE: didn't think thorugh my_list_list yet

class my_list_list(my_list):

    def apply_feature_vertical(self, f):
        """
        returns new my_list_list with f applied to each list
        """
        ans = my_list_list()
        for l in self:
            ans.append(f.generate(l))
        return ans

class my_list_ordinal_list(my_list_list):
    pass

class homo_my_list_list(my_list_list):
    """
    all the ordinals in the lists are the same
    unlike my_list_list, this requires that each element be a single_ordinal_ordered_object.
    """
    def get_member_ordinals(self):
        try:
            return self[0].get_ordinals()
        except IndexError:
            raise ValueError('homo_my_list_ordinal_list is empty or the lists contained are not single_ordinal_ordered_objects, has no ordinals')

    def get_horizontal_iter(self):
        """
        iterates through each list and return a my_list of the columns
        """
        # create iter instance, and keep calling it, putting results into a my_list
        horizontal_iters = [iter(l) for l in self]
        import itertools
        column_tuple_iter = itertools.izip(horizontal_iters)
        for column_tuple, ordinal in itertools.izip(column_tuple_iter, self.get_member_ordinals()):
            yield single_ordinal_single_value_ordered_object(ordinal, my_list(column_tuple))
        

class homo_my_list_interval_list(homo_my_list_list):
    """
    a homo_my_list_list where the member ordinals are intervals
    """
    @classmethod
    def init_from_intervals_and_my_list_ordinal_list(cls, intervals, ll):
        """
        creates homo list of lists by bucketizing each list, so that each list is single_ordinal_single_value and the value is a bucket
        ll is a parent class, so ans is parent class, so init call is safe(i think)
        """
        def f(l):
            return bucketed_ordinal_list.init_from_intervals_and_ordinal_list(intervals, l)
        ans = ll.apply_f_vertical(f)
        return cls.(ans)

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
