from time import sleep
import socket

from find_data_file import find_latest_file

def sock_send(sock_file, msg):
    buf = str(msg).strip() + '\n'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sock_file)
    sock.send(buf.encode())
    sock.close()
    pass

def log_reader(output_file_path,
               read_function = lambda x: x,
               reading_interval_sec =  0.1,
               reopen_interval_sec  = 11.,
               last_num_lines = 1):
    try:
        # setting parameter
        reading_interval_sec = float(reading_interval_sec)
        reopen_interval_sec  = float(reopen_interval_sec)
        cnt_reopen = int(reopen_interval_sec / reading_interval_sec) + 1
        cnt = 0
        fname = None
        fp = None

        # define sub function
        def reopen_file():
            nonlocal fname, fp
            if fname != find_latest_file(output_file_path):
                fname = find_latest_file(output_file_path)
                fp = open(fname)
                print('open %s' % fname)
                pass
            return

        # print last of the latest data
        reopen_file()
        lines = []
        for _line in fp:
            lines.append(_line)
            lines = lines[-last_num_lines:]
            pass
        for line in lines:
            linep = read_function(line).strip()
            if len(linep) > 0: print(linep)
            pass

        # monitor the log data
        while True:
            line = fp.readline()
            if len(line) > 0:
                cnt = 0
                linep = read_function(line).strip()
                if len(linep) > 0:
                    print(linep)
                else:
                    continue
                pass
            else:
                cnt += 1
                if cnt > cnt_reopen:
                    cnt = 0
                    reopen_file()
                    continue
                pass
            sleep(reading_interval_sec)
            pass
    except Exception:
        raise
    return
