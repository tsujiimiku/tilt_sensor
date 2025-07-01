#!/usr/bin/env python3

import os
from os.path import dirname, abspath, join
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
from email.message import EmailMessage
import mimetypes
import smtplib

isDebug = True

def send_via_gmail(msg, to_addrs=None, from_addr=None):
    if to_addrs is None:
        to_addrs = msg['To']
    if from_addr is None:
        from_addr = msg['From']
    for i in range(10):
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('gbird.auto@gmail.com', 'ugctyzqddawshweg')
            s.send_message(msg, from_addr, to_addrs)
            s.close()
            break
        except OSError:
            sleep(20)
        except Exception as e:
            #print(e)
            pass

def make_message(from_addr, to_addr, subject, text, attach_files=[]):
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()
    if type(attach_files) is str:
        attach_files = [attach_files]
        pass
    for f in attach_files:
        with open(f, 'rb') as fp:
            data = fp.read()
        ctype, encoding = mimetypes.guess_type(f)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(data, maintype=maintype,
                           subtype=subtype)
    return msg

if __name__ == "__main__":
    #m = make_message("gbird.auto@gmail.com", "t.tanaka@astr.tohoku.ac.jp", "test", "test")
    m = make_message("gbird.auto@gmail.com", "syskbks11@gmail.com", "test", "test",
                     ["/home/gb/.gb_video/inside.jpg","/home/gb/.gb_video/outside.jpg"])
    send_via_gmail(m, "syskbks11@gmail.com")
