#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:Administrator
@file: filter_phone_number_qq_email.py
@time: 2021/2/1  16:23
"""
# -*-coding:utf-8-*-
import logging
from smtplib import SMTP_SSL
from threadpool import makeRequests, ThreadPool


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
result = open('../mail/全国手机号QQ邮箱.txt', 'a+', encoding='utf-8')


def filter_email(thread_mail):
    # 连接 smtp 服务器
    service = SMTP_SSL("smtp.qq.com", 465)
    # service.debuglevel = 1
    service.ehlo()
    mail_f = '914081010@qq.com'
    service.mail(mail_f)
    for line in range(thread_mail * 10000, thread_mail * 10000 + 9999):
        # for end in ['@qq.com', '@163.com', '@aliyun.com']:
        for end in ['@qq.com']:
            mail_c = f"{line}{end}"
            c, m = service.rcpt(mail_c)
            if c == 250:
                mail_f = mail_c
                result.write(f"{mail_c}\n")
                logging.warning(f"{mail_c} {m}")
            elif c == 452:
                service.ehlo()
                service.mail(mail_f)
                c, m = service.rcpt(mail_c)
                if c == 250:
                    mail_f = mail_c
                    result.write(f"{mail_c}\n")
                    logging.warning(f"{mail_c} {m}")
            else:
                logging.warning(f'{mail_c} {m}')
            result.flush()


pool = ThreadPool(40)
file = open('phonetmp.csv', 'r', encoding='utf-8')
args = []
temp = 0
for x in file:
    args.append(int(x.split(',')[0]))
request = makeRequests(filter_email, args)
[pool.putRequest(req) for req in request]
pool.wait()
