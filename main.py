# -*-coding:utf-8-*-
from mylib.long_connect import SMTPSocket
from smtplib import SMTP_SSL
from threadpool import makeRequests, ThreadPool
from mylib.code_logging import Logger as Log

log = Log('send_email.log').get_log()


def filter_email(thread_id):
    file = open(f'source/1.txt', 'r', encoding='utf-8')
    result = open('result.txt', 'a+', encoding='utf-8')
    # 连接 smtp 服务器
    service = SMTPSocket(log)
    service.debuglevel = 1
    service.socket_connect()
    service.ehlo()
    mail_f = '914081010@qq.com'
    service.mail_from(mail_f)
    for line in file:
        mail_c = line.strip()
        c, m = service.mail_rcpt(mail_c)
        log.debug(f'{thread_id} - {c} {m}')
        if c == 250:
            mail_f = mail_c
            result.write(line)
            log.debug(f'{thread_id} - {line.strip()}')
        if c == 452:
            service.ehlo()
            service.mail_from(mail_f)
            c, m = service.mail_rcpt(mail_c)
            if c == 250:
                mail_f = mail_c
                result.write(line)
                log.debug(f'{thread_id} - {line.strip()}')
        result.flush()


pool = ThreadPool(1)
args = []
for x in range(1, 41):
    args.append(x)
request = makeRequests(filter_email, args)
[pool.putRequest(req) for req in request]
pool.wait()
# filter_email(1)
# service = SMTP_SSL(host='smtp.global-mail.cn')
# service.debuglevel = 1
# service.login('00@666ph.pw', 'cjm1588')