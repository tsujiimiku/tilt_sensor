#!/usr/bin/env python3

from datetime import datetime
from time import sleep

from find_data_file import find_file_it, find_latest_file
from base import Base


## main function
##   Calibrator_base.run(isDebug = False)
##
## virtual function
##   Calibrator_base.initialize()
##   Calibrator_base.calib(date_time, data)
##   Calibrator_base.finalize()
## 
## sub function
##   Calibrator_base.write_data_to_file(data_str, header = '', now = None)
##   Calibrator_base.sock_recv()
##
class Calibrator_base(Base):
    def __init__(self,
                 input_file_path  = 'data/%Y/%m/%Y%m%d.raw',
                 output_file_path = 'data/%y/%m/%Y%m%d.cal',
                 file_header = '##  Localtime  Unixtime  Value\n',
                 tzone = None, # argument for pytz.timezone (ex. Asia/Tokyo)
                 lock_file = None,
                 sock_file = None,
                 sock_buff_size = 4096,
                 interval_read   = 0.1, # sec
                 ):
        super().__init__(output_file_path = output_file_path,
                         file_header = file_header,
                         tzone = tzone,
                         lock_file = lock_file,
                         sock_file = sock_file,
                         sock_buff_size = sock_buff_size)
        self._ifile_it_ = find_file_it(str(input_file_path))
        self._output_file_path_ = str(output_file_path)
        self._file_header_ = str(file_header)
        self._interval_read_ = float(interval_read)
        self._ifile_ = None
        # check datetime of final calibrated data
        latest_oname = find_latest_file(self._output_file_path_)
        dt = None
        if latest_oname is not None:
            latest_ofile = open(latest_oname)
            line = None
            for tmpline in latest_ofile:
                if tmpline[0] != '#': line = tmpline
                pass
            if line is not None:
                dt, data = self._divide_datetime_data_(line)
                pass
            latest_ofile.close()
            pass
        # find new raw data
        if dt is None: 
            self._ifile_it_.set_time(datetime.fromtimestamp(0))
        else:
            self._ifile_it_.set_time(dt)
            pass
        self._ifile_ = open(self._ifile_it_.next())
        if dt is not None:
            while True:
                line = self._readline_()
                if len(line) <= 0: break
                tmp_dt, data = self._divide_datetime_data_(line)
                if tmp_dt == dt: break
                assert tmp_dt < dt
                pass
            pass
        pass


    ## virtual function
    def initialize(self): pass
    def calib(self, date_time, data): pass
    def finalize(self): pass


    ## user function
    def run(self, isDebug = False):
        try:
            self.initialize()
            while True:
                line = self._readline_()
                if len(line) > 0:
                    dt, data = self._divide_datetime_data_(line)
                    self.calib(dt, data)
                    continue
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
            try:
                next_ifile = self._ifile_it_.next()
            except StopIteration:
                break
            self._ifile_.close()
            self._ifile_ = open(next_ifile)
            pass
        return line
