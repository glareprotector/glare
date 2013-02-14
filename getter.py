import wc
import objects
import param
import pdb

p = param.param()
A = set(wc.get_stuff(objects.PID_with_SS_info, p))
B = set(wc.get_stuff(objects.PID_with_shared_MRN, p))
C = set(wc.get_stuff(objects.PID_with_several_tumors, p))

PID_to_use = A - B - C

PID_to_MRN = wc.get_stuff(objects.PID_to_MRN_dict,p)


i = 0

lengths = []

for PID in PID_to_use:

    
    p.set_param('pid',PID)
    texts = wc.get_stuff(objects.raw_medical_text,p)
    lengths.append(len(texts))
    print i, PID, len(texts)
    i += 1

pdb.set_trace()



