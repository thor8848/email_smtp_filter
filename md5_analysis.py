from peewee import *
from threadpool import makeRequests, ThreadPool
import redis

db = MySQLDatabase('emails_account', **{'host': 'localhost', 'password': '123456', 'port': 3306, 'user': 'root'})
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class DomainNameId(Model):
    id = PrimaryKeyField()
    domain_id = IntegerField()
    domain = CharField(max_length=255)

    class Meta:
        database = db
        table_name = 'domain_name_id'


class UserNameId(Model):
    id = PrimaryKeyField()
    user_id = IntegerField()
    domain_id = IntegerField()
    type_id = IntegerField()
    username = CharField(max_length=255)

    class Meta:
        database = db
        table_name = 'user_name_id'


class UserInfo(Model):
    id = PrimaryKeyField()
    user_id = IntegerField()
    pass_word = CharField(max_length=255)

    class Meta:
        database = db
        table_name = 'user_info'


def query_password(thread_id):
    file = open('account_data_70w.txt', 'a+', encoding='utf-8')
    while True:
        data = str(r.lpop('username')).split('/')
        username = data[0]
        domain_id = int(data[1])
        user_id = int(data[2])
        domain_data = DomainNameId.get(DomainNameId.domain_id == domain_id)
        try:
            password_data = UserInfo.get(UserInfo.user_id == user_id)
            result = f'{username}@{domain_data.domain} {password_data.pass_word}'
            print(result)
            file.write(result + '\n')
            file.flush()
        except UserInfo.DoesNotExist:
            print(f'{username}@{domain_data.domain} 密码查询失败')


r.flushall()
user_name_data = UserNameId.select()
print('用户名读取完毕')
temp = 0
with r.pipeline(transaction=False) as p:
    for per in user_name_data:
        r.lpush('username', f'{per.username}/{per.domain_id}/{per.user_id}')
        if temp % 10000 == 0:
            print('loading...')
            p.execute()
        temp += 1
    p.execute()
print('用户名导入完毕')
pool = ThreadPool(48)
args = []
for x in range(1, 11):
    args.append(x)
request = makeRequests(query_password, args)
[pool.putRequest(req) for req in request]
pool.wait()

