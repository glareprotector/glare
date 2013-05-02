


class named_object(object):

    def __new__(cls, *args, **kwargs):
        """
        assuming whatever arguments needed to make parent class are in args
        can't include **kwargs because some objects don't allow named arguments
        alternatively, could rewrite the __new__ of the parent classes but not doing that for now
        """
        inst = super(named_object, cls).__new__(cls, *args)
        inst.name = kwargs.pop('name')
        return inst

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()

    def __init__(self, *args, **kwargs):
        super(named_object, self).__init__(*args, **kwargs)


import pdb

class my_int(int):

    def __new__(cls, *args, **kwargs):
        inst = super(my_int, cls).__new__(cls, *args)
        inst.arg = kwargs.pop('arg')
        # prints {}
        print "inside __new__: ", kwargs
        return inst

    def __init__(self, *args, **kwargs):
        # prints {'arg':'asdf}'
        print "inside __init__: ", kwargs
        print kwargs    


a = my_int(5, arg = 'asdf')

pdb.set_trace()
# inits for base classes need to take named arguments because whatever gets passed into new gets passed into init
# alternatively, assume that init does not need any named arguments
def ok(f, name):
    def g(*args):
        class D(named_object,f):
            def __init__(self, *args, **kwargs):
                print 'D: ', D.__mro__
                super(D,self).__init__(*args)
        return D(*args, name=name)
    return g
import basic_features as bf
gfg = ok(bf.filtered_pid_iterable, 'asdf')(bf.all_ucla_pid_iterable(), lambda x: True)


#gfg = ok(int, 'asdf')(5)

pdb.set_trace()


class ordered_object(object):

    def __new__(cls, ordered_value, *args):
        inst = super(ordered_object, cls).__new__(cls, *args)
        inst.ordered_value = ordered_value
        return inst

class ordered_int(ordered_object, int):
    pass

class ordered_float(ordered_object, float):
    pass

class ordered_bucket(ordered_object, list):
    pass




class A(object):

    def g(self):
        print 'A'

    def f(self):
        print 'A'

    @classmethod
    def get_cls(cls):
        return cls

    def h(self):
        import pdb
        pdb.set_trace()
        print super(self.get_cls(),self).f()

class asdf(object):

    def f(self):
        print 'asdf'

    def __init__(self):
        import pdb
        print 'inside asdf init'
        pdb.set_trace()

    def __new__(cls):
        import pdb
        print 'inside asdf new'
        pdb.set_trace()
        inst = super(asdf, cls).__new__(cls)
        return inst
        
# lesson: 2nd argument of super is the instance or subclass of first argument that method is bound to.  so first argument on its own completely determines which method is called.  (it's only ok to bind a method to a subclass instance or subclass - that's why the binding argument has to be a subclass or instance of).  in the case of super with __new__, since we're dealing with a staticmethod, the returned method cannot be bound anyways, so 2nd argument isn't really useful.  but since i don't know the behavior of super when only 1 argument is supplied, supply the 2nd argument anyways

class asdf2(asdf):

    def __new__(cls):
        import pdb
        print 'inside asdf2 new'
        pdb.set_trace()
        args = []
        kwargs = {}
        inst = super(asdf2, asdf2).__new__(cls, *args, **kwargs)
        return inst

    def __init__(self):
        import pdb
        print 'inside asdf2 init'
        pdb.set_trace()



class B(asdf,A):


    

    def f(self):
        print 'B'

    #def h(self):
    #    super(B,A).g(self)

class my_int(object):

    def __add__(self, other):
        return my_int(int.__add__(self, other))

    def __new__(cls, val, order):
        #inst = super(my_int, cls).__new__(cls, val)
        inst = int.__new__(cls, val)
        inst.order = order
        import pdb
        pdb.set_trace()
        return inst
        

class my_string(str):

    def __add__(self, other):
        return my_string(str.__add__(self, other))

    def __radd__(self, other):
        import pdb
        pdb.set_trace()
        return self.__add__(other)


# if i subclass int, and do int+my_int, my_int's __radd__ will be called with (my_int, int).  so only need to define __add__ for my_int, and have __radd__ call __add__

a = my_string('asdf')

print a+a
print type(a+a)


