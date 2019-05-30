import os
import pickle

import django
from django_redis import get_redis_connection



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sousou.settings")
django.setup()
from order.models import Order

from user.models import UserInfo, Address
ostatus = '5'
order = Order.objects.filter(status=int(ostatus)).values(
    'id',
    'cost',
    'create_time',
    'sender_addr__liaison',
    'sender_addr__address_detailed',
    'recv_addr__recv_name',
    'recv_addr__liaison',
    'recv_addr__address_detailed',
)
print(list(order))
""" Address
    recv_name = models.CharField('联系人', max_length=20)
    liaison = models.IntegerField('联系方式')
    address_detailed = models.CharField('收货地址', max_length=50)
    address_number = models.CharField('门牌号', max_length=20)
    address_type = models.BooleanField(default=False)  # False为发货地址 True为收货地址
    is_default = models.BooleanField(default=False)  # 是否为默认收/发货地址
    uid = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)  # 外键关联用户
"""
# users = UserInfo.objects.all().values()
# print(users)
# add = Address.objects.filter(id=17).values()
# print(add)

# o = Order.objects.create(
#     id='1234567891',
#     uid_id=2,
#     sender_addr_id= 17,
#     recv_addr_id= 18
# )
#
# dumpo = pickle.dumps(o)
# conn = get_redis_connection()
# key = str(2) + o.id
# conn.hset(name=2, key=key, value=dumpo)
# conn.expire(key, 60)
#
# obj = conn.hgetall(2)
# print(obj[key.encode()])
# print(type(obj))
# ord = pickle.loads(obj)
# print(ord.create_time)

# Address.objects.create(
#     recv_name='达达',
#     liaison='18234126616',
#     address_detailed='就是看看',
#     address_number='672宿舍',
#     address_type=True,
#     is_default=True,
#     uid_id=2
# )
#
# Address.objects.create(
#     recv_name='达达',
#     liaison='18234126616',
#     address_detailed='中北大学怡丁苑21号楼',
#     address_number='672宿舍',
#     address_type=True,
#     is_default=True,
#     uid_id=2
# )
# django.db.utils.IntegrityError
# from django_redis import get_redis_connection
#
# conn = get_redis_connection('default')
# print(conn)
# print(conn.keys())