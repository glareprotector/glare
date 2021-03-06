import wrapper

#import f as features
import param
import pdb
import objects
import global_stuff
import my_exceptions


#pdb.set_trace()
useless = wrapper.famished_wrapper()
wc = wrapper.wrapper_catalog(useless, param.param({}))

def get_stuff(wrapper_class, params, recalculate=False, to_pickle=False, to_filelize=False, always_recalculate = False):

    params.set_param('which_wrapper_class', wrapper_class)
    wc_used_keys, wc_all_keys, wrapper_instance, all_keys_key_key_set = wc.constructor(params, True, False, False)
    try:

        stuff_used_keys, stuff_all_keys, stuff, stuff_all_keys_key_key_set = wrapper_instance.constructor(params, recalculate, to_pickle, to_filelize, always_recalculate = always_recalculate)
    except Exception, err:
        print 'ERROR when calling get_stuff with this error', err
        import traceback, sys

        for frame in traceback.extract_tb(sys.exc_info()[2]):
            fname, lineno,fn,text = frame
            print "Error in %s on line %d" % (fname, lineno)
        print sys.exc_traceback.tb_lineno
        raise my_exceptions.WCFailException
    else:
        return stuff




def get_wrapper_instance(wrapper):
    import param
    temp = param.param()
    temp.set_param('which_wrapper_class', wrapper)
    a,b,c,d = wc.constructor(temp, True, False, False)
    return c
