#!/usr/bin/env python3

from logger import Logger_base

class TheLogger(Logger_base):
    def initialize(self):
        self.write_data_to_file('logger start', header = '# ')
        self.cnt = 0
        return

    def do(self):
        msg = self.sock_recv()
        if msg is not None:
            try:
                self.set_interval(float(msg))
            except:
                pass
            pass
        self.cnt += 1
        self.write_data_to_file(str(self.cnt))
        return

    def finalize(self):
        self.write_data_to_file('logger stop', header = '# ')
        return

    pass

aLogger = TheLogger(output_file_path = 'data/%Y/%m/%Y%m%d.dat',
                    lock_file = '.sample_logger.lock',
                    sock_file = '.sample_logger.sock',
                    interval_sec = 10.)
#aLogger.run()
aLogger.run(isDebug = True)
