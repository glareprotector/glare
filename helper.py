import string
#import Bio.PDB
import csv
#import constants
import string
import re
import math
import global_stuff
import pdb
import param
import random
import sys
import my_exceptions
from my_data_types import sv_int, sv_float


def print_traceback():
    import traceback, sys
    for frame in traceback.extract_tb(sys.exc_info()[2]):
        fname, lineno,fn,text = frame
        print "Error in %s on line %d" % (fname, lineno)
    print sys.exc_traceback.tb_lineno


# also sets global_stuff.RESULTS_FOLDER to proper value
def read_param(file_location):
    
    # read folder_name
    f = open(constants.INFO_FOLDER + file_location)
    the_params = param.param({})
    hp_values = param.param()
    folder_name = f.readline().strip()

    global_stuff.RESULTS_FOLDER = global_stuff.RESULTS_BASE_FOLDER + folder_name + '/'

    for line in f.readlines():
        print >> sys.stderr, line
        if line[0] != '#':
            s = line.strip().split(',')
            if s[0] != 'hp':
                the_name = s[0]
                if the_name == 'n':
                    node_features = []
                    for i in range(1, len(s)):
                        node_features.append(constants.get_master_node_feature_list()[int(s[i])])
                    the_params.set_param('n', node_features)
                if the_name == 'e':
                    edge_features = []
                    for i in range(1, len(s)):
                        edge_features.append(constants.get_master_edge_feature_list()[int(s[i])])
                    the_params.set_param('e', edge_features)
                try:
                    the_type = s[1]
                    if the_type == 'f':
                        the_params.set_param(the_name, float(s[2]))
                    elif the_type == 'i':
                        the_params.set_param(the_name, int(s[2]))
                    elif the_type == 's':
                        the_params.set_param(the_name, s[2])
                except:
                    pass

    # hp values file happens to be the same as info file, so set that

    the_params.set_param('hpvf', file_location)


    if len(the_params.get_param('e')) != 0:
        assert the_params.get_param('wif') != 2

    
    return folder_name, the_params




def get_aux_folder(pdb_name, chain_letter, start, end):
    return constants.AUX_FOLDER + string.lower(pdb_name) + '_' + string.upper(chain_letter) + '_' + str(start) + '_' + str(end) + '/'




def shorten(x):
    x = re.sub(r'\'','',x)
    x = re.sub(r'class','',x)
    x = re.sub(r' ','',x)
    x = re.sub(r'<','',x)
    x = re.sub(r'>','',x)
    x = re.sub(r'f\.','',x)
    x = re.sub(r'\),\(',')(',x)
    return x


def super_shorten(x):

    x = re.sub(r'\'','',x)
    x = re.sub(r'class','',x)
    x = re.sub(r' ','',x)

    
    x = re.sub(r'<','',x)
    x = re.sub(r'>','',x)
    x = re.sub(r'f\.','',x)
    x = re.sub(r'\),\(',')(',x)
    #x = re.sub(r'\)\(','|',x)
    #x = re.sub(r'\[\(','[',x)
    #x = re.sub(r'\)\]',']',x)
    #pdb.set_trace()
    return x



def do_map(aa,mapping):
    try:


        return mapping[aa]
    except:

        return mapping['-']

def print_stuff_dec(f):

    def g(*args, **kwargs):
        #print >> sys.stderr, 'calling ', f.func_name, ' with ', args, kwargs
        ans = f(*args, **kwargs)
        #print >> sys.stderr, f.func_name, ' returned ', ans
        return ans
    
    return g

def get_object(p_wrapper, params, recalculate = False, to_pickle = True, use_pickle = True):
    return the_obj_manager.get_variable(p_wrapper(params), recalculate, to_pickle, use_pickle)

def get_file(p_wrapper, params, recalculate = False, option = 'r'):
    return the_file_manager.get_file(p_wrapper(params), recalculate, option)



def dict_deep_copy(d):
    to_return = {}
    for key in d.keys():
        to_return[key] = d[key]
    return to_return

def list_union(a, b):
    A = set(a)
    B = set(b)
    return list(A - B)


def write_mat(mat, f_name, the_sep = ',', option = 'w'):
    f = open(f_name, option)
    #print >> sys.stderr, mat
    for row in mat:
        
        line = string.join([('%.5f' % x)  for x in row], sep=the_sep)
        line = line + '\n'
        f.write(line)
    f.close()

def write_mat_raw(mat, f_name, the_sep = ',', option = 'w'):
    f = open(f_name, option)
    #print >> sys.stderr, mat
    for row in mat:
        
        line = string.join([str(x)  for x in row], sep=the_sep)
        line = line + '\n'
        f.write(line)
    f.close()


def read_mat_to_int_float_tuple(f):
    import pdb

    f = open(f.name, 'r')
    ans = []
    for line in f:
        this = []
        if len(line.strip()) > 0:
            try:
                s = line.strip().split(',')
                for it in s:
                    sp = it[1:len(it)-1]
                    spp = sp.split('-')
                    a = int(spp[0])
                    b = float(spp[1])
                    this.append((a,b))
            except Exception, err:
                print >> sys.stderr, err

                print >> sys.stderr, s
                
        ans.append(this)
    return ans

def write_int_float_tuple_mat(mat, f_name):
    def g(t):
        return '(' + str(t[0]) + '-' + ('%.3f' % t[1]) + ')'
    f = open(f_name, 'w')
    for row in mat:
        line = string.join([g(x) for x in row],sep = ',')
        line = line + '\n'
        f.write(line)
    f.close()
        
        

def write_vect(vect, f_name, the_sep = ',', option = 'w'):
    f = open(f_name, option)
    line = string.join([str(x) for x in vect], sep=the_sep)
    f.write(line)
    f.close()

def read_edge_to_int(f):
    f = open(f.name)
    ans = {}
    for line in f:
        s = line.strip().split(',')
        u = int(s[0])
        v = int(s[1])
        val = int(s[2])
        ans[(u,v)] = val
    return ans

def write_edge_to_int(obj, f_name):
    f = open(f_name, 'w')
    for key in obj:
        f.write(str(key[0]) + ',' + str(key[1]) + ',' + str(obj[key]) + '\n')
    f.close()

def read_vect_to_float(f, the_sep = ','):
    r = csv.reader(f, delimiter = the_sep)
    line = r.next()
    vect = [float(x) for x in line]
    f.close()
    return vect

def write_vect_to_string_vert(obj, f):
    g = open(f,'w')
    for x in obj:
        g.write(str(x) + '\n')
    g.close()

def read_vect_to_string_vert(f, the_sep = ','):
    g = open(f.name,'r')
    ans = []
    for line in g:
        ans.append(line.strip())
    return ans

def read_vect_to_int_vert(f, the_sep = ','):
    g = open(f.name,'r')
    ans = []
    for line in g:
        ans.append(int(line.strip()))
    return ans

def read_vect_to_string_int(f, the_sep = ','):
    g = open(f.name,'r')
    ans = []
    for line in g:
        ans.append(int(line.strip()))
    return ans


def read_mat_to_float(f, the_sep = ','):
    r = csv.reader(f, delimiter = the_sep)
    mat = []
    for line in r:
        vect = [float(x) for x in line]
        mat.append(vect)
    f.close()
    return mat

def read_mat_to_string(f, the_sep = ','):
    r = csv.reader(f, delimiter = the_sep)
    mat = []
    for line in r:
        vect = [x for x in line]
        mat.append(vect)
    f.close()
    return mat

def read_vect_to_int(f, the_sep = ','):
    r = csv.reader(f, delimiter = the_sep)
    line = r.next()
    vect = [int(x) for x in line]
    f.close()
    return vect

def read_mat_to_int(f, the_sep = ','):
    r = csv.reader(f, delimiter = the_sep)
    mat = []
    for line in r:
        vect = [int(x) for x in line]
        mat.append(vect)
    f.close()
    return mat

def get_overlap(n1, n2):
    n1set = set()
    n2set = set()
    count = 0
    for i in range(len(n1)):
        for it in n1[i]:
            n1set.add((i,it[0]))
            count += 1
    for i in range(len(n2)):
        for it in n2[i]:
            n2set.add((i,it[0]))
    intersect = n1set & n2set

    return len(intersect), count

def get_file_string_set(f_name):
    f = open(f_name, 'r')
    ans = set()
    for line in f:
        ans.add(line.strip())
    f.close()
    return ans



class file_sender(object):

    def __init__(self, lock_file, buildup_size):
        self.lock_file = lock_file
        self.buildup_size = buildup_size
        self.buildup = []

    def __send(self, it):
        # first try to make the remote directory
        
        import ssh
        
        here_file = it[0]
        there_file = it[1]
        there_folder = it[2]
        hostname = it[3]
        username = it[4]
        password = it[5]
        port = it[6]
        wrapper = it[7]
        object_key = it[8]
        to_remove = it[9]

        import pdb
        
        
        """
        client = ssh.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        client.connect(hostname, port, username)
        client.exec_command('mkdir ' + there_folder)
        
        cmd = 'scp ' + '\''+here_file+'\'' + ' ' + username + '@' + hostname + ':' + '\''+there_file+'\''
        import subprocess
        subprocess.call(cmd,shell=True,executable='/bin/bash')

        """
        key = ssh.RSAKey(filename='/home/fw27/.ssh/id_rsa')
        t = ssh.Transport((hostname, port))
        t.connect(username=username)
        t.auth_publickey('fultonw',key)

        sftp = ssh.SFTPClient.from_transport(t)
        try:
            print >> sys.stderr, '\t\t\tsending:', here_file, there_file
            sftp.put(here_file, there_file)
            wrapper.record_transferred_file(object_key)
        except Exception, err:
            print >> sys.stderr, err
            print >> sys.stderr, '\t\t\tfailed to send:', here_file, there_file

        if to_remove:
            try:
                import subprocess
                print >> sys.stderr, '               removing:', here_file
                subprocess.call(['rm', here_file])

            except Exception, err:
                print >> sys.stderr, err
        

        try:
            sftp.close()
        except Exception, err:
            print err
        try:
            t.close()
        except Exception, err:
            print err
        
        
        
        
    def send(self, here_file, there_file, hostname, there_folder, username, password, port, wrapper, object_key, whether_to_delete):
        #first check if if it is a file
        import pdb

        import os
        if os.path.isfile(here_file):
            import pdb

            self.buildup.append([here_file, there_file, there_folder, hostname, username, password, port, wrapper, object_key, wrapper, object_key, whether_to_delete])

        import wc
        dist_count = 0
        for it in self.buildup:
            import objects
            if type(it[0]) == objects.general_distance:
                dist_count += 1
                
        if dist_count > 0 or len(self.buildup) > self.buildup_size:
        #if len(self.buildup) > self.buildup_size:
            import FileLock
            print >> sys.stderr, "trying to send before lock: ", here_file
            with FileLock.FileLock(self.lock_file, timeout=200) as lock:
                for it in self.buildup:
                    self.__send(it)
            self.buildup = []
            import pdb

def hamming_distance(s1, s2):
    assert(len(s1) == len(s2))
    count = 0.0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            count += 1
    return count / len(s1)

def PID_to_MRN(pid):
    import wc, objects
    m = wc.get_stuff(objects.PID_to_MRN_dict, param.param())
    return m[pid]


#import numpy


                    
def parse_p_input(p, arg_string):

    for z in range(0,len(arg_string),3):
        param_name = arg_string[z]
        param_type = arg_string[z+2]
        val = arg_string[z+1]
        if param_type == 'i':
            val = int(val)
        elif param_type == 'f':
            val = float(val)
        elif param_type == 's':
            val = val
        p.set_param(param_name, val)


def get_cursor():
    import pyodbc
    connection = pyodbc.connect('DRIVER={SQL Server};SERVER=REDPANDA\REDPANDA;UID=DBA;PWD=tdie4u@tLQM')
    cursor = connection.cursor()
    return cursor


def row_to_dict(row):
    ans = {}
    for desc, val in zip(row.cursor_description, row):
        ans[desc[0]] = val
    return ans

def coded_words_to_words(coded_words):
    raw_words = coded_words.split('&')
    import string
    words = [string.join(raw_word.split('+'),sep=' ').lower() for raw_word in raw_words]
    return words

def words_to_coded_words(words):
    return string.join([string.join(word.split(' '), sep='+') for word in words], sep='&')


def compare(x,y):
    if x == y:
        return True
    else:
        try:
            x = x.strip()
            y = y.strip()
        except:
            return False
        else:
            return x == y

def compare_in(x, collection):
    for item in collection:
        if compare(x, item):
            return True
    return False


def clean_text(text, delimiters):
    """
    replace all delimiters with gsw
    convert to punctuationless string
    """

    def is_word(s):
        return len(s) > 1




    import re, string


    # replace each delimiter with gsw.  
    # if delimiter is a word, require white space or period/comma around it
    for delimiter in self.delimiters:
        if not is_word(delimiter):
            s = re.compile(delimiter)
        else:
            s = re.compile('(^|[\s.,|])'+delimiter+'($|[\s.,|])')
        raw_text = s.sub(' gsw ', raw_text)

    regex = re.compile('[%s]' % re.escape(string.punctuation))
    text = regex.sub(' ', text)
    text = str(string.join(text.split(), ' '))
    return text.lower()

def print_if_verbose(x,level):

    if level <= verbose:
        print x

verbose = 1.2

def match_phrase(excerpt, phrase):
    import re
    searcher = re.compile('(^|\s|\|)'+phrase+'($|\s|\|)')
    matches = [mx for m in searcher.finditer(excerpt)]
    if len(matches) > 0:
        return True
    else:
        return False





def get_last_match(s, searcher, pos):
    """
    returns the last match that ends on or before pos
    """
    all_matches = [m for m in searcher.finditer(s)]
    for i in range(len(all_matches)-1,-1,-1):
        m = all_matches[i]
        if m.end()+1 <= pos:
            return m


def get_next_match(s, searcher, pos):
    """
    returns the next match that starts on or before pos
    """
    return searcher.search(s, pos)



def get_spanning_match(m1, m2):
    """
    assumes m1 and m2 are matches of the same text
    """
    import match_features
    abs_start = min(m1.get_abs_start(), m2.get_abs_start())
    abs_end = max(m1.get_abs_end(), m2.get_abs_end())
    return match_features.match(m1.text, abs_start, abs_end)


# assumes that exactly 1 of the words is present in the excerpt
def get_the_word_and_position(self, raw_text, words):

    import re
    searchers = [re.compile('\s'+word+'\s') for word in words]
    matches = [[x for x in searcher.finditer(raw_text)] for searcher in searchers]

    assert sum([len(ms)>0 for ms in matches]) == 1
    for match in matches:
        if len(match) > 0:
            assert len(match) == 1
            return match[0].group(), match[0].start()
    assert False


import my_data_types


# assumes all records can be filtered
# holds records, not excerpts
class record_list(my_data_types.single_ordinal_ordinal_list):

    # returns a list of list of excerpts
    def get_excerpts_by_words(self, words):
        ans = my_data_types.my_list()
        for record in self:
            filtered_record = record.get_excerpts_by_word(words)
            if len(filtered_record) > 0:
                ans.append(filtered_record)
        return ans

    def get_excerpts_by_word(self, word):
        return self.get_excerpts_by_words([word])

    def get_excerpts_by_side_effect(self, side_effect):
        return self.get_excerpts_by_words(self, side_effect.get_synonyms())

def init_from_str(cls, the_string):
    try:
        return cls.init_from_str(the_string)
    except AttributeError, err:
        print err
        return cls(the_string)

from datetime import date, timedelta


class my_date(date, my_data_types.ordered_object):

        
    def __repr__(self):
        return str(self.month) + '/' + str(self.day) + '/' + str(self.year)
        

    @classmethod
    def init_from_str(cls, date_str):
        month = int(date_str.split('/')[0])
        day = int(date_str.split('/')[1])
        year = int(date_str.split('/')[2])
        return cls(year, month, day)    



    @classmethod
    def init_from_num(cls, num):
        if num < 100:
            return cls(1,1,1)
        year = int(num/10000)
        month = (num/100) % 100
        day = num % 100
        date_str = str(month) + '/' + str(day) + '/' + str(year)
        return cls.init_from_str(date_str)

    @classmethod
    def init_from_hyphen_string(cls, date_string):
        s = date_string.strip().split('-')
        year = int(s[0])
        month = int(s[1])
        day = int(s[2])
        return cls(year, month, day)

    @classmethod
    def init_from_slash_string(cls, date_string):
        s = date_string.strip().split('/')
        year = int(s[2])
        month = int(s[0])
        day = int(s[1])
        return cls(year, month, day)

class my_timedelta(timedelta):

    def __repr__(self):

        return str(self.days / 365.0)


    
class record(my_data_types.single_ordinal_ordered_object):
    """
    refers to patient's record
    """

    def get_ordinal(self):
        return self.date

    def __init__(self, pid, date, raw_text):
        self.pid = pid
        self.date = date
        self.raw_text = raw_text


    def __len__(self):
        return len(self.raw_text)

    def __repr__(self):
        ans = 'PID: ' + str(self.pid) + '\nDate: ' + str(self.date) + '\n' + self.raw_text
        return ans

class report_record(record):

    window_size = 100


    def __init__(self, pid, date, raw_text, idx):
        """
        report_record has to store its index in the list of records for the patient
        """
        self.idx = idx
        record.__init__(self, pid, date, raw_text)

    # returns my_list of excerpts containing a list of words.  this only makes sense for report records that have excerpts.  makes sure a window doesn't contain 2 matches
    def get_excerpts_by_words(self, words):
        """
        returns ordinal_list of excerpts
        """

        # for now, get rid of all punctuation. and then split/join with space to get space separated words

        #cleaned_text = clean_text(self.raw_text)
        

        cleaned_text = self.raw_text.lower()

        searchers = []
        matches = set()
        ans = my_data_types.single_ordinal_ordinal_list()
        import re

        class pos_word_tuple(object):
            def __init__(self, pos, word):
                self.pos = pos
                self.word = word
            def __eq__(self, other):
                return self.pos == other.pos
            def __hash__(self):
                return self.pos.__hash__()
        for word in words:
            searchers.append(re.compile('[\s.,]'+word+'[\s.,]'))
        for searcher in searchers:
            this_matches = [pos_word_tuple(m.start(), m.group()) for m in searcher.finditer(cleaned_text)]
            for match in this_matches:
                matches.add(match)
                
        match_list = list(matches)
        match_list.sort(key = lambda x:x.pos)

        for i in range(len(match_list)):
            position = match_list[i].pos
            if i == 0:
                prev_pos = 0
            else:
                prev_pos = match_list[i-1].pos + len(match_list[i-1].word)
            if i == len(match_list) - 1:
                next_pos = len(cleaned_text)
            else:
                next_pos = match_list[i+1].pos
            low = max(0, max(prev_pos, position - report_record.window_size))
            high = min(len(cleaned_text), min(next_pos, position + report_record.window_size))
            #print low, high
            #to_add = excerpt(self.pid, self.date, cleaned_text[low:high], self, match_list[i].word.strip(), position)
            to_add = excerpt(self.pid, self.date, cleaned_text[low:high], self, match_list[i].word.strip())
            ans.append(to_add)

        return ans
    
    def get_excerpts_by_word(self, word):
        return self.get_excerpts_by_words([word])

    def get_excerpts_by_side_effect(self, side_effect):
        return self.get_excerpts_by_words(side_effect.get_synonyms())

    def get_excerpts_to_display_by_side_effect(self, side_effect):
        return self.get_excerpts_by_words(side_effect.get_display_words())


# excerpt abstract class
class excerpt(record):

    def __init__(self, pid, date, raw_text, parent_record, anchor):
        self.parent_record = parent_record
        self.anchor = anchor
        #self.position = position
        record.__init__(self, pid, date, raw_text)


        

class tumor_lite(object):

    num_attributes = 16
    pid, grade, SEERSummStage2000, surgery_code, radiation_code, date_diagnosed, surgery_date, radiation_date, erection_time_series, incontinence_time_series, DLC, alive, DOB , tumor_tuple, patient_tuple, super_tuple= range(num_attributes)


    """
    pid:int, grade:string, SEERSummStage2000:string, texts:list(string), erection_negation_counts:dict{str:int}, surgery_code:char(2), radiation_code:char(1), psa_value:char(3), prev_psa_level(3). 
    gleason_primary:char(1), gleason_secondary:char(2), erection_ts, date_last_contact, alive_or_not, DOB
    """
    def __init__(self, _pid, _grade, _SEERSummStage, _surgery_code, _radiation_code, _date_diagnosed, _surgery_date, _radiation_date, _erection_time_series, _incontinence_time_series, _DLC, _alive, _DOB, _tt, _pt, _sdt):
        self.attributes = [_pid, _grade, _SEERSummStage, _surgery_code, _radiation_code, _date_diagnosed, _surgery_date, _radiation_date, _erection_time_series, _incontinence_time_series, _DLC, _alive, _DOB, _tt, _pt, _sdt]

    def get_attribute(self, attribute):
        return self.attributes[attribute]

    def get_label(self, label_f):
        ans = label_f.generate(self)
        assert(len(ans) == 1)
        return ans[0]

    def get_csv_string(self, feature_list):
        feature_vector = self.get_feature_vector(feature_list)
        import string
        return string.join([str(x) for x in feature_vector],sep=',')

    def get_feature_vector(self, feature_list):
        """
        creates feature vector given list of features.  if features are categorical and thus a list, flattens them
        """
        vector = []
        for feature in feature_list:
            to_add = feature.generate(self)
            try:
                vector = vector + to_add
            except TypeError:
                vector.append(to_add)
        return vector


class tumor(tumor_lite):


    num_attributes = 1
    texts, = range(tumor_lite.num_attributes, tumor_lite.num_attributes + num_attributes)

    """
    pid:int, grade:string, SEERSummStage2000:string, texts:list(string), erection_negation_counts:dict{str:int}, surgery_code:char(2), radiation_code:char(1), psa_value:char(3), prev_psa_level(3). 
    gleason_primary:char(1), gleason_secondary:char(2), erection_ts, date_last_contact, alive_or_not, DOB
    """
    def __init__(self, _pid, _grade, _SEERSummStage, _surgery_code, _radiation_code, _date_diagnosed, _surgery_date, _radiation_date, _erection_time_series, _incontinence_time_series, _DLC, _alive, _DOB, _tt, _pt, _sdt, _texts):
        tumor_lite.__init__(self, _pid, _grade, _SEERSummStage, _surgery_code, _radiation_code, _date_diagnosed, _surgery_date, _radiation_date, _erection_time_series, _incontinence_time_series, _DLC, _alive, _DOB, _tt, _pt, _sdt)
        self.attributes += [_texts]





def interval_val_as_string(series):
    ans = ''
    lower_strs = []
    val_strs = []
    for item in series:
        lower_str = str(item.get_ordinal().low.days/365)
        try:
            val = item.get_value()
        except my_exceptions.NoFxnValueException:
            val = -1
        val_str = str(val)
        lower_strs.append(lower_str)
        val_strs.append(val_str)
    import string
    actual_lower_str = string.join(lower_strs, sep=',')
    actual_val_str = string.join(val_strs, sep=',')
    return actual_lower_str + '\n' + actual_val_str









class data_set(object):

    def __init__(self, the_data):
        self.the_data = the_data

    def get_num_samples(self):
        return len(self.the_data)

    
    def filter(self, f):
        return data_set(filter(f, self.the_data))

    def get_csv_string(self, feature_list):
        header_strings = []
        for feature in feature_list:
            for i in range(len(feature)):
                header_strings.append(feature.get_name())
        import string
        header_string = string.join(header_strings, sep = ',')
        ans = ''
        for tumor in self.the_data:
            ans += tumor.get_csv_string(feature_list) + '\n'
        return header_string + '\n' + ans

    def get_feature_matrix(self, feature_list):
        import numpy
        temp = []
        for data in self.the_data:
            temp.append(data.get_feature_vector(feature_list))

        return numpy.array(temp)

    def get_labels(self, label_f):
        labels = numpy.zeros(self.get_num_samples())
        for i in range(self.get_num_samples()):
            labels[i] = self.the_data[i].get_label(label_f)
        return labels

    def get_features_and_labels_jointly(self, feature_list, label_f):
        feature_mat = []
        labels = []
        for data in self.the_data:
            print data.get_attribute(tumor.pid)
            pdb.set_trace()
            try:
                feature_vector = data.get_feature_vector(feature_list)
                label = data.get_label(label_f)
            except:
                print 'failed at: ', data.get_attribute(tumor.pid)
            else:
                feature_mat.append(feature_vector)
                labels.append(label)
        import numpy
        feature_mat = numpy.array(feature_mat)
        labels = numpy.array(labels)
        return feature_mat, labels

    def __str__(self):
        ans = ''
        for a_data in self.the_data:
            ans += a_data.__str__() + '\n'
        return ans

    def filter_data_set(self, filter_f):
        new_data = []
        for data in self.the_data:
            if filter_f(data):
                new_data.append(data)
        return data_set(new_data)

    def get_pid_list(self):
        return [tumor.get_attribute(tumor.pid) for tumor in self.the_data]

    def write_pid_list_to_file(self, out_file):
        pid_list = self.get_pid_list()
        write_vect_to_string_vert(pid_list, out_file)

    @classmethod
    def data_set_from_pid_file(cls, pid_file, params):
        f = open(pid_file, 'r')
        pids = []
        for line in f:
            pid = int(line.strip())
            pids.append(pid)
        return cls.data_set_from_pid_list(pids, params)

    
    def __iter__(self):
        return self.the_data.__iter__()


    # functions here don't know about any objects in objects.py, except for this one
    # this function gets tumor object via wc.  nothing in analysis part should call wc
    # if i want to cache any features, do so upstream of creating tumor class
    @classmethod
    def data_set_from_pid_list(cls, pid_list, params):
        import wc
        import objects
        from global_stuff import get_tumor_cls, get_tumor_w
        the_data = []
        i = 0
        for pid in pid_list:
            print i, pid
            i += 1
            params.set_param('pid', pid)
            try:
                a_tumor = wc.get_stuff(get_tumor_w(), params)
                #assert len(a_tumor.attributes) == get_tumor_cls().num_attributes
            except my_exceptions.WCFailException:
                print 'failed to get ', pid
            except AssertionError:
                print 'failed to get ', pid, ' number of attributes was incorrect'
            except Exception:
                print 'failed to get ', pid, ' not sure of error'
            else:
                the_data.append(a_tumor)
        return cls(the_data)



