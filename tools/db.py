import json
import pickle

from datetime import datetime
from django.db import transaction
from django_redis import get_redis_connection

from order.models import Order
from user.models import UserInfo, Address
from django.http import JsonResponse


def is_legal(username, pwd):
    """判断用户是否合法"""
    try:
        user = UserInfo.objects.get(username=username)
        if user.check_password(pwd):
            return True, user
    except UserInfo.DoesNotExist:
        return False, '用户名不存在!'
    return False, '用户名或密码错误!'


def check_info(username, password, email):
    """检查用户注册信息"""
    if not all([username, password, email]):
        return False, JsonResponse({'status': False, 'msg': '注册信息填写不完整!'})
    if len(username) != 11 or len(password) < 6 or len(password) > 16:
        return False, JsonResponse({'status': False, 'msg': '注册信息填写不正确!'})
    if UserInfo.objects.filter(username=username):
        return False, JsonResponse({'status': False, 'msg': '用户名已存在!'})
    return True, None


@transaction.atomic
def store_address(post_data, uid):
    """存储收发货地址"""
    save_id = transaction.savepoint()  # 设置事务保存点
    try:
        slo, sla = post_data.get('sender_position').split(',')
        rlo, rla = post_data.get('receiver_position').split(',')
        send = Address.objects.filter(
            address_type=False, address_longitude=slo, address_latitude=sla)
        recv = Address.objects.filter(
            address_type=True, address_longitude=rlo, address_latitude=rla)
        if not send:
            # 发货地址
            sender_address = Address()
            sender_address.recv_name = post_data.get('sender_name')
            sender_address.liaison = post_data.get('sender_phone')
            sender_address.address_detailed = post_data.get('sender_address')
            sender_address.address_number = post_data.get('sender_door')
            sender_address.address_longitude = slo
            sender_address.address_latitude = sla
            sender_address.uid_id = uid
            sender_address.address_type = False
            if post_data.get('save_send'):
                sender_address.is_default = True
            sender_address.save()
        else:
            sender_address = send[0]
        if not recv:
            # 收货地址
            receiver_address = Address()
            receiver_address.recv_name = post_data.get('receiver_name')
            receiver_address.liaison = post_data.get('receiver_phone')
            receiver_address.address_detailed = post_data.get('receiver_address')
            receiver_address.address_number = post_data.get('receiver_door')
            receiver_address.address_longitude = rlo
            receiver_address.address_latitude = rla
            receiver_address.uid_id = uid
            receiver_address.address_type = True
            if post_data.get('save_recv'):
                receiver_address.is_default = True
            receiver_address.save()
        else:
            receiver_address = recv[0]
    except Exception:
        transaction.savepoint_rollback(save_id)
        return False
    transaction.savepoint_commit(save_id)
    return sender_address, receiver_address


def create_order(request):
    """创建订单"""
    try:
        conn = get_redis_connection()  # redis链接
        username = request.session.get('username')
        key = 'order_' + username
        order_info = json.loads(conn.get(username))
        order = Order()
        order.id = datetime.now().strftime('%Y%m%d%H%M%S') + str(request.session['uid'])
        order.cost = request.session.get('o_fare')
        order.sender_addr_id = request.session.get('sender_address_id')
        order.recv_addr_id = request.session.get('receiver_address_id')
        order.uid_id = request.session.get('uid')
        order.stdmode = order_info.get('gtype')
        order.value = order_info.get('gvalue')
        order.demo = order_info.get('demo')
        order.save()
        conn.delete(username)
        conn.hset(key, order.id, pickle.dumps(order))
        conn.expire(key, 900)  # 设置过期时间
    except Exception:
        return False
    return order
