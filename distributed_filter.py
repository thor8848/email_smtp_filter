# -*- coding:utf-8-*-
import requests
from requests.exceptions import RequestException
from mylib.long_connect import SMTPSocket
from threadpool import makeRequests, ThreadPool
from mylib.code_logging import Logger as Log
import time
from random import randint
import json

log = Log('send_email.log').get_log()


def filter_email(thread_id):
    time.sleep(randint(0, 100) / 10)
    # 连接 smtp 服务器
    service = SMTPSocket(log)
    # service.debuglevel = 1
    service.socket_connect()
    service.helo()
    service.ehlo()
    mail_f = '914081010@qq.com'
    service.mail_from(mail_f)
    while True:
        try:
            result = []
            log.debug('>{} request data'.format(thread_id))
            mission_emails = get_mission()
            temp = 0
            success = 0
            for line in mission_emails:
                mail_c = line.strip()
                c, m = service.mail_rcpt(mail_c)
                log.debug('{} - {} {}'.format(thread_id, c, m))
                if c == 250:
                    mail_f = mail_c
                    result.append(line)
                    success += 1
                    log.debug('{} - {}'.format(thread_id, line))
                if temp % 20 == 0:
                    service.ehlo()
                    service.mail_from(mail_f)
                    c, m = service.mail_rcpt(mail_c)
                    if c == 250:
                        mail_f = mail_c
                        result.append(line)
                        success += 1
                        log.debug('{} - {}'.format(thread_id, line))
                if success % 100 == 0:
                    requests.get('http://172.31.8.95:5004/success_number/')
                if temp % 100 == 0:
                    requests.get('http://172.31.8.95:5004/filter_number/')
                temp += 1
            log.debug('send back email data')
            data = json.loads({
                'emails': result
            })
            requests.post('http://172.31.8.95:5004/result/', data=data)
            log.debug('send back data success')
        except RequestException:
            time.sleep(10)
            log.debug('< connection failed retry')
            continue


def get_mission():
    response = requests.get('http://172.31.8.95:5004/filter/')
    data = response.json()
    return data['mission_emails']


pool = ThreadPool(40)
args = []
for x in range(1, 41):
    args.append(x)
request = makeRequests(filter_email, args)
[pool.putRequest(req) for req in request]
pool.wait()


# temp = get_mission()
# data = json.dumps({'emails': temp[0:5000]})
# requests.post('http://172.31.8.95:5004/result/', data=data)