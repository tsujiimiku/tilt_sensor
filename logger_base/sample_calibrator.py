#!/usr/bin/env python3

from calibrator import Calibrator_base

class TheCalib(Calibrator_base):
    def initialize(self):
        self.write_data_to_file('calib start', header = '# ')
        return

    def calib(self, date_time, data):
        cnt = int(data)
        cnt *= 10
        self.write_data_to_file(str(cnt), now = date_time)
        return

    def finalize(self):
        self.write_data_to_file('calib stop', header = '# ')
        return

    pass

aCalib = TheCalib(input_file_path  = 'data/%Y/%m/%Y%m%d.dat',
                  output_file_path = 'data/%Y/%m/%Y%m%d.cal',
                  lock_file = '.sample_calibrator.lock',
                  sock_file = '.sample_calibrator.sock',
                  interval_read = 0.5)
aCalib.run(isDebug = True)
