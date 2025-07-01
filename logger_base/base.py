#!/usr/bin/env python3

from os.path import isfile, isdir, dirname
from os import makedirs,uname
from datetime import datetime, timedelta, timezone
import socket
from select import select
from pathlib import Path
from mail_sender import send_via_gmail, make_message

## user function
##   Base.write_data_to_file(data_str, header = '', now = None)
##   Base.sock_recv()
##
class Base(object):
    def __init__(self,
                 output_file_path = 'data/%Y/%m/%Y%m%d.dat',
                 file_header = '##  Localtime  Unixtime  Value\n',
                 tzone = None, # argument for pytz.timezone (ex. Asia/Tokyo)
                 lock_file = None,
                 sock_file = None,
                 sock_buff_size = 4096,
                 ):
        ## check multiple start
        if lock_file is not None:
            import fcntl
            try:
                self._lock_ = open(lock_file, 'a')
                fcntl.lockf(self._lock_.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                exit(1)
                pass
        else:
            self._lock_ = True
            pass
        ## open socket for communication
        self._sock_buff_size_ = int(sock_buff_size)
        if sock_file is not None:
            path = Path(sock_file)
            if path.is_socket(): path.unlink()
            assert not path.exists()
            self._sock_ = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock_.bind(sock_file)
            path.chmod(0o777)
            self._sock_.settimeout(1)
            self._sock_.listen()
        else:
            self._sock_ = None
            pass
        ## setting for output file
        self._output_file_path_ = str(output_file_path)
        self._file_header_ = str(file_header).strip() + '\n'
        self._oname_ = None
        self._ofile_ = None
        if tzone is None:
            from dateutil.tz import tzlocal
            self._tzone_ = tzlocal()
        else:
            import pytz
            self._tzone_ = pytz.timezone(tzone)
            pass
        pass


    ## user function
    def write_data_to_file(self, data_str, header = '', now = None):
        if now is None: now = self._now_()
        self._get_output_file_(now)
        line = header
        line += self._isotime_(now)
        line += '  ' + self._unixtime_(now)
        line += '  ' + data_str.strip() + '\n'
        self._ofile_.write(line)
        self._ofile_.flush()
        return

    def sock_recv(self):
        if self._sock_ is None: return None
        sel = select([self._sock_], [], [], 0)[0]
        if len(sel) == 0: return None
        soc, addr = self._sock_.accept()
        buff = ''
        with soc:
            buff = soc.recv(self._sock_buff_size_).decode()
            pass
        return buff


    def alert(self,from_addr, to_addr, text, level=-1,
              name='', server_name=uname().nodename, attached_files=[]):
        subject = '['+name+']'
        if level == 0: # info
            subject += ' INFO from {}'.format(server_name)
        elif level == 1: # alert
            subject += ' ALERT from {}'.format(server_name)
        elif level == 2: # emergency
            subject += ' EMERGENCY from {}'.format(server_name)
        else:
            subject += ' MESSAGE from {}'.format(server_name)
        self._send_mail(from_addr, to_addr, subject, text, attached_files)

    ## internal function
    def _now_(self):
        return datetime.now(self._tzone_)

    def _isotime_(self, now = None):
        if now is None: now = self._now_()
        s = ''
        try:
            s = now.isoformat(timespec='microseconds') # python3.6+
        except:
            z = now.strftime('%z') # +0100
            z = z[:3] + ':' + z[3:] # +01:00
            s = now.strftime('%Y-%m-%dT%H:%M:%S.%f') + z # isoformat
        return s

    def _unixtime_(self, now = None):
        if now is None: now = self._now_()
        return '%.6f' % now.timestamp()

    def _strftime_(self, st, now = None):
        if now is None: now = self._now_()
        return now.strftime(st)

    def _get_output_file_(self, now = None):
        if now is None: now = self._now_()
        if self._oname_ == self._strftime_(self._output_file_path_, now): return
        if self._ofile_ is not None: self._ofile_.close()
        self._oname_ = self._strftime_(self._output_file_path_, now)
        dname = dirname(self._oname_)
        if not isdir(dname): makedirs(dname)
        if isfile(self._oname_):
            flag_new_file = False
        else:
            flag_new_file = True
            pass
        self._ofile_ = open(self._oname_, 'a')
        if flag_new_file:
            self._ofile_.write(self._file_header_)
            self._ofile_.flush()
            pass
        return

    def _divide_datetime_data_(self, line):
        if line[0] == '#': return None
        isotime, unixtime = line.split()[0:2]
        dtcnt = len(isotime) + len(unixtime) + 4
        data = line[dtcnt:].strip()
        # spltline = line.split()
        # isotime = spltline[0]
        # unixtime = spltline[1]
        # data = spltline[2:]
        try:
            import dateutil.parser
            dt = dateutil.parser.parse(isotime)
        except:
            if isotime[-3] == ':':
                tzone_hour = int(isotime[-6:-3])
            else:
                tzone_hour = int(isotime[-5:-2])
                pass
            tzone_min  = int(isotime[-2:])
            tzone = timezone(timedelta(hours = tzone_hour, minutes = tzone_min))
            dt = datetime.fromtimestamp(float(unixtime))
            dt = dt.replace(tzinfo = tzone)
        return dt, data

    def _send_mail(self, from_addr, to_addr, subject, text, attached_files):
        m = make_message(from_addr, to_addr, subject, text, attached_files)
        send_via_gmail(m)
        return

    pass
