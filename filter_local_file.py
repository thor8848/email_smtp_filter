#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:Administrator
@file: filter_local_file.py
@time: 2021/2/20  15:13
"""
from smtplib import SMTP_SSL
from threadpool import makeRequests, ThreadPool
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
result = open('mail/filter-qq邮箱-2021-02-20.txt', 'a+', encoding='utf-8')
local_file = open('mail/qq邮箱-2021-02-20.txt', 'r', encoding='utf-8')


def filter_email(thread_mail):
    # 连接 smtp 服务器
    service = SMTP_SSL("smtp.qq.com", 465)
    service.ehlo()
    mail_f = '914081010@qq.com'
    service.mail(mail_f)
    for line in thread_mail:
        mail_c = f"{line}"
        c, m = service.rcpt(mail_c)
        logging.warning(f'{c} {m}')
        if c == 250:
            mail_f = mail_c
            result.write(f"{line}\n")
            logging.warning(f"{line}")
        if c == 452:
            service.ehlo()
            service.mail(mail_f)
            c, m = service.rcpt(mail_c)
            if c == 250:
                mail_f = mail_c
                result.write(f"{line}\n")
                logging.warning(f"{line}")
        result.flush()


pool = ThreadPool(40)
args = []
arg = []
temp = 0
for x in local_file:
    if temp < 100:
        arg.append(x.strip())
        temp += 1
    else:
        args.append(arg)
        arg = []
        temp = 0
request = makeRequests(filter_email, args)
[pool.putRequest(req) for req in request]
pool.wait()
