#!/usr/bin/env python3

from time import sleep

from base import Base

from mail_sender import send_via_gmail, make_message

## main function
##   Logger_base.run(isDebug = False)
##
## virtual function
##   Logger_base.initialize()
##   Logger_base.do()
##   Logger_base.finalize()
##
## sub function
##   Logger_base.write_data_to_file(data_str, header = '', now = None)
##   Logger_base.sock_recv()
##   Logger_base.set_interval(t_sec)
##
class Logger_base(Base):
    def __init__(self,
                 output_file_path = 'data/%Y/%m/%Y%m%d.dat',
                 file_header = '##  Localtime  Unixtime  Value\n',
                 tzone = None, # argument for pytz.timezone (ex. Asia/Tokyo)
                 lock_file = None,
                 sock_file = None,
                 sock_buff_size = 4096,
                 interval_sec = 0., # sec
                 ):
        super().__init__(output_file_path = output_file_path,
                         file_header = file_header,
                         tzone = tzone,
                         lock_file = lock_file,
                         sock_file = sock_file,
                         sock_buff_size = sock_buff_size)
        self._interval_sec_ = float(interval_sec)
        pass


    ## virtual function
    def initialize(self): pass
    def do(self):         pass
    def finalize(self):   pass


    ## user function
    def run(self, isDebug = False):
        try:
            self.initialize()
            while True:
                self.do()
                sleep(self._interval_sec_)
                pass
        except Exception:
            if isDebug: raise
            pass
        finally:
            self.finalize()
            pass
        return

    def set_interval(self, t_sec):
        t = float(t_sec)
        assert t >= 0.
        self._interval_sec_ = float(t)
        return
    
    pass
