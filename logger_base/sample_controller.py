#!/usr/bin/env python3

from controller import Controller_base

class TheControl(Controller_base):
    def initialize(self):
        print('start')
        return

    def control(self, dt, data):
        cnt = int(data)
        if cnt % 100 == 0: print(cnt)
        return

    def freeze(self):
        print('freeze')
        return

    def finalize(self):
        print('stop')
        return

    pass

aControl = TheControl(input_file_path = 'data/%Y/%m/%Y%m%d.cal',
                      output_file_path = '/dev/null',
                      lock_file = '.sample_controller.lock',
                      sock_file = '.sample_controller.sock',
                      interval_read = 0.5,
                      interval_freeze = 12.)

aControl.run(isDebug = True)
