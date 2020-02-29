#! /usr/bin/env python3
import socket
import socks
import dns.resolver
from logging import Logger
from base64 import b64encode


__all__ = ["SMTPException", "SMTPReplyError", "SMTPServerDisconnected", "SMTPSocket"]


class SMTPException(OSError):
    """base exception 基础异常类"""


class SMTPReplyError(SMTPException):
    """reply message error 返回消息异常"""


class SMTPServerDisconnected(SMTPException):
    """disconnection error 连接失败"""


class SMTPBlockedByRateLimit(SMTPException):
    """连接频率限制"""


class SMTPAuthenticationError(SMTPException):
    """连接频率限制"""


SMTP_PORT = 25
CRLF = "\r\n"
bCRLF = b"\r\n"
_MAXLINE = 8192     # more than 8 times larger than RFC 821, 4.5.3


class SMTPSocket:
    debuglevel = 0

    def __init__(self, logging: Logger):
        # socks.set_default_proxy(socks.HTTP, "190.2.144.46", 18044)
        # socket.socket = socks.socksocket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.service = object
        self.domain = object
        self.logging = logging
        self.username = ''
        self.password = ''

    def send_command(self, data):
        request = f'{data} {CRLF}'
        if self.debuglevel > 0:
            self.logging.debug(f'> {data}')
        self.socket.sendall(str(request).encode('utf-8'))

    def send_mail(self, sender, receivers, message):
        # type: (str, str/list, str) -> (int, str)
        """
        :param sender :
        :param receivers:
        :param message:
        :return:
        """
        self.mail_from(sender)
        self.mail_rcpt(receivers)
        self.send_data(message)

    def socket_connect(self):
        self.service = f'smtp.qq.com'
        if self.debuglevel > 0:
            self.logging.debug(f'> Connect: smtp.qq.com')
        self.socket.connect((f'smtp.qq.com', SMTP_PORT))
        code, msg = self.get_reply()
        if code == 452:
            raise SMTPBlockedByRateLimit(msg)
        return True

    def helo(self):
        c, m = self.compile_send_command("HELO global-mail.cn")
        return c, m

    def ehlo(self):
        c, m = self.compile_send_command("EHLO global-mail.cn")
        return c, m

    def auth_user(self):
        self.helo()
        self.ehlo()
        self.logging.debug(f'> RANDOM ACCOUNT username:{self.username} password:{self.password}')
        username = str(b64encode(bytes(self.username, encoding='utf-8')), 'utf-8')
        c, m = self.compile_send_command(f'AUTH LOGIN {username}')
        password = str(b64encode(bytes(self.password, encoding='utf-8')), 'utf-8')
        c, m = self.compile_send_command(password)
        return c, m

    def mail_from(self, sender):
        c, m = self.compile_send_command(f'MAIL FROM:<{sender}>')
        return c, m

    def mail_rcpt(self, receivers):
        if isinstance(receivers, list):
            for email in receivers:
                self.compile_send_command(f'RCPT TO:<{email}>')
        else:
            c, m = self.compile_send_command(f'RCPT TO:<{receivers}>')
            return c, m

    def send_data(self, message):
        c, m = self.compile_send_command('DATA')
        if c == 354:
            if self.debuglevel > 0:
                self.logging.debug(f'> Send Content Data: ........')
            self.socket.send(message + b'\r\n.\r\n')
            msg = self.socket.recv(4096)
            data = str(msg, encoding='utf-8')
            c, m = data[:3], data[3:]
            if self.debuglevel > 0:
                self.logging.debug(f'< {c} {m}')
            return c, m
        else:
            return c, m

    def socket_close(self):
        self.compile_send_command('QUIT')

    def get_reply(self):
        msg = self.socket.recv(4096)
        data = str(msg, encoding='utf-8').strip().split('\r\n')
        if self.debuglevel > 0:
            for line in data:
                self.logging.debug(f'< {line}')
        if len(msg) > 0:
            c, m = data[-1][:3], data[-1][3:]
            return int(c), m
        else:
            raise SMTPReplyError

    # def query_mx(self):
    #     try:
    #         mx = dns.resolver.query(self.domain, 'MX')
    #         preference = 0
    #         exchange = ''
    #         recode = []
    #         for i in mx:
    #             if self.debuglevel == 1:
    #                 self.logging.debug(f'> dns:{i.preference}{i.exchange}')
    #             if int(i.preference) > preference:
    #                 recode.append({i.preference, i.exchange})
    #                 preference = i.preference
    #                 exchange = str(i.exchange).strip('.')
    #         return preference, exchange, recode
    #     except dns.resolver.NXDOMAIN:
    #         return 0, '', []

    def compile_send_command(self, command):
        if self.debuglevel > 0:
            self.logging.debug(f'> {command}')
        self.socket.sendall(str(f'{command}{CRLF}').encode('utf-8'))
        c, m = self.get_reply()
        return c, m
