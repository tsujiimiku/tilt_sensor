#!/usr/bin/env python3

from time import sleep

from find_data_file import find_file_it, find_latest_file
from base import Base
from mail_sender import send_via_gmail, make_message

## main function
##   Controller_base.run(isDebug = False)
##
## virtual function
##   Controller_base.initialize()
##   Controller_base.control(date_time, data)
##   Controller_base.freeze()
##   Controller_base.finalize()
##
## sub function
##   Controller_base.write_data_to_file(data_str, header = '', now = None)
##   Controller_base.sock_recv()
##
class Controller_base(Base):
    def __init__(self,
                 input_file_path  = 'data/%Y/%m/%Y%m%d.dat',
                 output_file_path = 'data/%y/%m/%Y%m%d.log',
                 file_header = '##  Localtime  Unixtime  Value\n',
                 tzone = None, # argument for pytz.timezone (ex. Asia/Tokyo)
                 lock_file = None,
                 sock_file = None,
                 sock_buff_size = 4096,
                 interval_read   = 0.1, # sec
                 interval_reopen = 11., # sec
                 interval_freeze = 31., # sec
                 ):
        super().__init__(output_file_path = output_file_path,
                         file_header = file_header,
                         tzone = tzone,
                         lock_file = lock_file,
                         sock_file = sock_file,
                         sock_buff_size = sock_buff_size)
        self._input_file_path_  = str(input_file_path)
        self._file_header_ = str(file_header)
        self._interval_read_  = float(interval_read)
        self._cnt_reopen_max_ = round(float(interval_reopen)
                                      / self._interval_read_ + 0.5)
        self._cnt_freeze_max_ = round(float(interval_freeze)
                                      / self._interval_read_ + 0.5)
        self._cnt_reopen_ = 0
        self._cnt_freeze_ = 0
        self._iname_ = find_latest_file(self._input_file_path_)
        self._ifile_ = open(self._iname_)
        for line in self._ifile_: pass
        self.initialize()
        pass


    ## virtual function
    def initialize(self): pass
    def control(self, date_time, data): pass
    def freeze(self): pass
    def finalize(self): pass


    ## user function
    def run(self, isDebug = False):
        try:
            while True:
                line = self._readline_()
                if len(line) > 0:
                    self._cnt_freeze_ = 0
                    dt, data = self._divide_datetime_data_(line)
                    self.control(dt, data)
                    continue
                if self._cnt_freeze_ < self._cnt_freeze_max_:
                    self._cnt_freeze_ += 1
                else:
                    self._cnt_freeze_ = 0
                    self.freeze()
                    pass
                sleep(self._interval_read_)
                pass
        except Exception:
            if isDebug: raise
            pass
        finally:
            self.finalize()
            pass
        return


    ## internal function
    def _readline_(self):
        while True:
            line = self._ifile_.readline()
            if len(line) > 0:
                if line[0] == '#':
                    continue
                else:
                    break
                pass
            if self._cnt_reopen_ < self._cnt_reopen_max_:
                self._cnt_reopen_ += 1
            else:
                self._cnt_reopen_ = 0
                if self._iname_ != find_latest_file(self._input_file_path_):
                    self._iname_ = find_latest_file(self._input_file_path_)
                    self._ifile_.close()
                    self._ifile_ = open(self._iname_)
                    continue
                    pass
                pass
            break
        return line

