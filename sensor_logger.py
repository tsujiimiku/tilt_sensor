#!/usr/bin/env python3
from logger_base.logger import Logger_base
import device_model
from os.path import dirname, abspath, join
import time

output_path = '/home/miku/logger/data/witsensor/%Y/%m/%Y%m%d_witsensor.raw'
time_interval = 1  # 1秒間隔で記録
file_header = '## Localtime  Unixtime  '
file_header += 'AccX  AccY  AccZ  '
file_header += 'AsX  AsY  AsZ  '
file_header += 'HX  HY  HZ  '
file_header += 'AngX  AngY  AngZ'
file_header += '\n'
lockfile = join(dirname(abspath(__file__)), '.logger_witsensor.lock')
sockfile = join(dirname(abspath(__file__)), '.logger_witsensor.sock')

class LoggerWitSensor(Logger_base):
    def initialize(self):
        self.dev = device_model.DeviceModel("WitMotion Sensor", "/dev/ttyUSB0", 9600, 0x50, self.update_data)
        self.dev.openDevice()
        self.dev.startLoopRead()
        self.latest_data = None

    def update_data(self, device_model):
        self.latest_data = device_model.deviceData

    def do(self):
        msg = self.sock_recv()
        if msg is not None:
            try:
                self.set_interval(float(msg))
            except:
                pass

        # センサーからデータを読み取る
        try:
            if self.latest_data is not None:
                wstr = '{:.6f}  {:.6f}  {:.6f}  '.format(
                    self.latest_data.get('AccX', 0),
                    self.latest_data.get('AccY', 0),
                    self.latest_data.get('AccZ', 0)
                )
                wstr += '{:.6f}  {:.6f}  {:.6f}  '.format(
                    self.latest_data.get('AsX', 0),
                    self.latest_data.get('AsY', 0),
                    self.latest_data.get('AsZ', 0)
                )
                wstr += '{:.6f}  {:.6f}  {:.6f}  '.format(
                    self.latest_data.get('HX', 0),
                    self.latest_data.get('HY', 0),
                    self.latest_data.get('HZ', 0)
                )
                wstr += '{:.6f}  {:.6f}  {:.6f}'.format(
                    self.latest_data.get('AngX', 0),
                    self.latest_data.get('AngY', 0),
                    self.latest_data.get('AngZ', 0)
                )
                self.write_data_to_file(wstr)
            else:
                self.write_data_to_file('No data', header='# ')
        except Exception as e:
            print(e)
            self.write_data_to_file('failed', header='# ')

    def finalize(self):
        self.dev.stopLoopRead()
        self.dev.closeDevice()

if __name__ == '__main__':
    logger = LoggerWitSensor(output_file_path=output_path,
                             file_header=file_header,
                             lock_file=lockfile,
                             sock_file=sockfile,
                             interval_sec=time_interval)
    logger.run(isDebug=False)
