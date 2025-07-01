#!/usr/bin/env python3

from os.path import abspath, dirname, join
from re import match
from glob import glob
from datetime import datetime

time_format_keys = {'Y': '[0-9]'*4,
                    'y': '[0-9]'*2,
                    'm': '[0-9]'*2,
                    'd': '[0-9]'*2,
                    'H': '[0-9]'*2,
                    'M': '[0-9]'*2,
                    'S': '[0-9]'*2,
                    's': '[0-9]+'}

class find_file_it(object):
    ## start_time: datetime.datetime
    def __init__(self, file_path, start_time = None):
        self.file_path = abspath(file_path)
        self.base = dirname(self.file_path.split('%')[0])
        tmptree = self.file_path[len(self.base):].split('/')
        self.tree = [s for s in tmptree if s != '']
        if start_time is not None: self.set_time(start_time)
        pass

    ## start_time: datetime.datetime
    def set_time(self, start_time):
        self.it_time = start_time
        self.flag_init = True
        return

    def __iter__(self): return self

    def next(self): return self.__next__() # for python2.7

    def __next__(self):
        path = [self.base]
        # find directory and file in each depth
        for t in range(len(self.tree)):
            fmt = join(self.base, *(self.tree[:t+1]))
            k = self.it_time.strftime(fmt)
            n = self.tree[t]
            # change to wild card
            for tkey in time_format_keys:
                n = n.replace('%%%s' % tkey,
                              time_format_keys[tkey])
                pass
            # get file list
            name_list = []
            for p in path: name_list += glob(join(p, n))
            if len(name_list) == 0: raise StopIteration()
            name_list.sort()
            # search file
            tmp_list = name_list + [k]
            tmp_list.sort()
            i = tmp_list.index(k)
            if self.flag_init:
                # pickup same one and previous one
                name_list = name_list[max([0, i-1]) : min([i+1, len(name_list)])]
            else:
                # pickup same one and next one
                name_list = name_list[i : min([i+2, len(name_list)])]
                pass
            path = name_list
            pass
        if self.flag_init:
            # pickup previous one
            ret = path[0]
        else:
            # pickup next one
            if len(path) < 2: raise StopIteration()
            ret = path[1]
            pass
        # update time for iteration
        self.it_time = self._strptime_(ret)
        self.flag_init = False
        return ret

    def _strptime_(self, path):
        ptn = self.file_path
        for tkey in time_format_keys:
            ptn = ptn.replace('%%%s' % tkey,
                              '('+time_format_keys[tkey]+')')
            pass
        val = match(ptn, path)
        keylist = self.file_path.split('%')
        date_dict = {}
        for k, v in zip(keylist[1:], val.groups()):
            date_dict[k[0]] = v
            pass
        if 's' in date_dict:
            return datetime.fromtimestamp(float(date_dict['s']))
        if 'y' in date_dict:
            if 'Y' in date_dict:
                del date_dict['y']
                pass
            pass
        dptn = ''
        dval = ''
        for d in date_dict:
            dptn += '%%%s' % d
            dval += date_dict[d]
            pass
        return datetime.strptime(dval, dptn)

    pass

def find_latest_file(output_file_path):
    it = find_file_it(output_file_path)
    it.set_time(datetime.now())
    ret = None
    for fn in it: ret = fn
    del it
    return ret


if __name__ == '__main__':
    print('find_file_it')
    it = find_file_it('data/%Y/%m/%Y%m%d.dat')
    t = datetime.strptime('20180621', '%Y%m%d')
    #t = datetime.now()
    it.set_time(t)
    for n in it: print(n)
    print('find_latest_file')
    print(find_latest_file('data/%Y/%m/%Y%m%d.dat'))
