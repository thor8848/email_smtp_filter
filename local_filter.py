# -*-coding:utf-8-*-
import logging
from smtplib import SMTP_SSL
from threadpool import makeRequests, ThreadPool


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
result = open('mail/8位QQ邮箱.txt', 'a+', encoding='utf-8')


def filter_email(thread_mail):
    # 连接 smtp 服务器
    service = SMTP_SSL("smtp.qq.com", 465)
    # service.debuglevel = 1
    service.ehlo()
    mail_f = '914081010@qq.com'
    service.mail(mail_f)
    for line in range(thread_mail, thread_mail + 1000):
        mail_c = f"{line}@qq.com"
        c, m = service.rcpt(mail_c)
        logging.warning(f'{c} {m}')
        if c == 250:
            mail_f = mail_c
            result.write(f"{line}@qq.com\n")
            logging.warning(f"{line}@qq.com")
        if c == 452:
            service.ehlo()
            service.mail(mail_f)
            c, m = service.rcpt(mail_c)
            if c == 250:
                mail_f = mail_c
                result.write(f"{line}@qq.com\n")
                logging.warning(f"{line}@qq.com")
        result.flush()


pool = ThreadPool(40)
args = []
temp = 0
for x in range(10000000, 100000000, 1000):
    args.append(x)
request = makeRequests(filter_email, args)
[pool.putRequest(req) for req in request]
pool.wait()
