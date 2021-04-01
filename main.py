# -*-coding:utf-8-*-
from mylib.long_connect import SMTPSocket
from smtplib import SMTP_SSL
from threadpool import makeRequests, ThreadPool
from mylib.code_logging import Logger as Log

log = Log('send_email.log').get_log()
result = open('mail/8位QQ邮箱.txt', 'a+', encoding='utf-8')


def filter_email(thread_mail):
    # 连接 smtp 服务器
    service = SMTPSocket(log)
    service.debuglevel = 1
    service.socket_connect()
    service.ehlo()
    mail_f = '914081010@qq.com'
    service.mail_from(mail_f)
    for line in range(thread_mail, thread_mail + 1000):
        mail_c = f"{line}@qq.com"
        c, m = service.mail_rcpt(mail_c)
        log.debug(f'{c} {m}')
        if c == 250:
            mail_f = mail_c
            result.write(f"{line}@qq.com\n")
            log.debug(f"{line}@qq.com")
        if c == 452:
            service.ehlo()
            service.mail_from(mail_f)
            c, m = service.mail_rcpt(mail_c)
            if c == 250:
                mail_f = mail_c
                result.write(f"{line}@qq.com\n")
                log.debug(f"{line}@qq.com")
        result.flush()


pool = ThreadPool(40)
args = []
temp = 0
for x in range(10000000, 100000000, 1000):
    args.append(x)
request = makeRequests(filter_email, args)
[pool.putRequest(req) for req in request]
pool.wait()
