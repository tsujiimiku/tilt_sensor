#!/usr/bin/env python3

from sys import argv
from reader import sock_send, log_reader

interval = float(argv[1])

sock_send('.sample_logger.sock', str(interval))

try:
    log_reader(output_file_path = 'data/%Y/%m/%Y%m%d.dat')
except KeyboardInterrupt:
    pass
finally:
    sock_send('.sample_logger.sock', '10')
    pass
