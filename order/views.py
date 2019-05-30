import json
import os
import pickle

from alipay import AliPay
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View

from django_redis import get_redis_connection

from order.models import Order
from tools.db import store_address, create_order
from tools.utils import calculate_distance, calculate_price
from user.models import UserInfo, Refund


def create(request):
    """在线下单"""
    return render(request, 'order/create_order.html')


def unpay(request):
    """未支付"""
    conn = get_redis_connection()
    username = request.session.get('username')
    key = 'order_' + username
    orders = conn.hgetall(key)
    if request.method == 'GET':
        order_list = list()
        if orders:
            order_list = [pickle.loads(v) for k, v in orders.items()]
        return render(request, 'order/unpay_order.html', {'order_list': order_list})
    elif request.method == 'POST':
        # 去支付按钮
        try:
            oid = request.POST.get('oid')
            order = pickle.loads(orders[oid.encode()])
            alipay = AliPay(
                appid=settings.ALIPAY_APPID,
                app_notify_url=None,
                app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key.pem'),
                alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem'),
                sign_type='RSA2',
                debug=True
            )
            order_string = alipay.api_alipay_trade_page_pay(
                product_code='FAST_INSTANT_TRADE_PAY',
                out_trade_no=order.id,
                total_amount=str(order.cost),  # 支付金额
                subject='嗖嗖物流 订单号%s' % order.id,
                notify_url=None  # 回调URL
            )
            pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
            return JsonResponse({'status': True, 'msg': pay_url})
        except Exception:
            return JsonResponse({'status': False, 'msg': '支付失败!'})


def check_pay(request):
    """查询点击去支付后的结果"""
    order_id = request.POST.get('oid')
    username = request.session.get('username')
    if not all([order_id, username]):
        return JsonResponse({'status': False, 'msg': '订单ID获取错误!'})
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'status': False, 'msg': '无效的订单!'})
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,  # 应用id
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem'),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )
    while True:
        # 支付宝接口查询订单支付状态
        response = alipay.api_alipay_trade_query(order_id)
        code = response.get('code')

        if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
            # 支付成功
            # 获取支付宝交易号
            trade_no = response.get('trade_no')
            # 更新订单状态
            order.trade_no = trade_no
            order.status = 1
            order.save()
            # 返回结果
            key = 'order_' + username
            conn = get_redis_connection()
            conn.hdel(key, order_id)
            return JsonResponse({'status': True, 'msg': '支付成功!'})
        elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
            # 等待买家付款
            # 业务处理失败，可能一会就会成功
            import time
            time.sleep(5)
            continue
        else:
            # 支付出错
            print(code)
            return JsonResponse({'status': False, 'msg': '支付失败!'})


def unpack(request):
    """未接单"""
    uid = request.session.get('uid')
    if request.method == 'GET':
        order_list = Order.objects.filter(uid_id=uid, status=1)
        return render(request, 'order/unpack_order.html', {'order_list': order_list})
    elif request.method == 'POST':
        save_id = transaction.savepoint()
        try:
            oid = request.POST.get('oid')
            user = UserInfo.objects.get(pk=uid)
            order = Order.objects.get(id=oid, status=1)
            order.status = 5
            order.save()
            user.balance += order.cost
            Refund.objects.create(user=user, order=order)
        except Exception:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'status': False, 'msg': '订单错误！'})
        transaction.savepoint_commit(save_id)
        return JsonResponse({'status': True, 'msg': '取消成功！'})


def untoken(request):
    """待取货"""
    uid = request.session.get('uid')
    if request.method == 'GET':
        order_list = Order.objects.filter(uid_id=uid, status=2)
        return render(request, 'order/untoken_order.html', {'order_list': order_list})
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                user = UserInfo.objects.get(pk=uid)
                oid = request.POST.get('oid')
                order = Order.objects.get(id=oid, status=2)
                order.status = 5
                order.save()
                user.balance += order.cost
                Refund.objects.create(user=user, order=order)
            return JsonResponse({'status': True, 'msg': '取消成功！'})
        except Exception:
            return JsonResponse({'status': False, 'msg': '订单错误！'})


def distribution(request):
    """配送中"""
    if request.method == 'GET':
        uid = request.session.get('uid')
        order_list = Order.objects.filter(uid_id=uid, status=3)
        return render(request, 'order/distribution_order.html', {'order_list': order_list})
    elif request.method == 'POST':
        try:
            oid = request.POST.get('oid')
            order = Order.objects.get(id=oid, status=3)
            order.status = 4
            order.save()
            return JsonResponse({'status': True, 'msg': '收货成功！'})
        except Order.DoesNotExist:
            return JsonResponse({'status': False, 'msg': '订单错误！'})


def finished(request):
    """已完成"""
    uid = request.session.get('uid')
    order_list = Order.objects.filter(uid_id=uid, status=4)
    return render(request, 'order/finished_order.html', {'order_list': order_list})


def cancel(request):
    """已取消"""
    uid = request.session.get('uid')
    order_list = Order.objects.filter(uid_id=uid, status=5)
    return render(request, 'order/cancel_order.html', {'order_list': order_list})


class Confirm(View):
    """确认订单"""
    conn = get_redis_connection()  # redis链接

    def get(self, request):
        try:
            order = self.conn.get(request.session['username'])
            data = json.loads(order)
            slo, sla = data['sender_position'].split(',')
            rlo, rla = data['receiver_position'].split(',')
            dis = calculate_distance((sla, slo), (rla, rlo))  # 计算距离
            weight = data['weight']
            fare = calculate_price(dis, weight)  # 计算运费
            request.session['o_fare'] = format(fare, '.2f')  # 记录运费
            balance = UserInfo.objects.get(pk=request.session['uid']).balance
            return render(request, 'order/confirm_order.html', locals())
        except Exception:
            return render(request, '404.html')

    def post(self, request):
        sa = request.POST.get('sender_address')
        ra = request.POST.get('receiver_address')
        sn = request.POST.get('sender_name')
        rn = request.POST.get('receiver_name')
        sp = request.POST.get('sender_phone')
        rp = request.POST.get('receiver_phone')
        gtype = request.POST.get('gtype')
        gvalue = request.POST.get('gvalue')
        print(request.POST)
        if not all([sa, ra, sn, rn, sp, rp, gtype, gvalue]):
            return JsonResponse({'status': False, 'msg': '信息填写不完整!'})
        self.conn.set(request.session['username'], json.dumps(request.POST))
        self.conn.expire(request.session['username'], 15 * 60)
        result = store_address(request.POST, request.session['uid'])
        if not result:
            return JsonResponse({'status': False, 'msg': '收发货地址信息有误,请确认有无重复地址!'})
        request.session['sender_address_id'] = result[0].id
        request.session['receiver_address_id'] = result[1].id
        return JsonResponse({'status': True, 'msg': 'success'})


def online_payment(request):
    """在线支付"""
    try:
        order = create_order(request)
        fare = request.session.get('o_fare')
        if not all([order, fare]):
            return JsonResponse({'status': False, 'msg': '下单失败!'})
        request.session['oid'] = order.id
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem'),
            sign_type='RSA2',
            debug=True
        )
        order_string = alipay.api_alipay_trade_page_pay(
            product_code='FAST_INSTANT_TRADE_PAY',
            out_trade_no=order.id,
            total_amount=str(fare),  # 支付金额
            subject='嗖嗖物流 订单号%s' % order.id,
            notify_url=None  # 回调URL
        )
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'status': True, 'msg': pay_url})
    except Exception:
        return JsonResponse({'status': False, 'msg': '下单失败!'})


def check(request):
    """获取支付结果"""
    order_id = request.session.get('oid')
    fare = request.session.get('o_fare')
    username = request.session.get('username')
    if not all([order_id, fare, username]):
        return JsonResponse({'status': False, 'msg': '订单ID获取错误!'})
    try:
        order = Order.objects.get(id=order_id, status=0)
    except Order.DoesNotExist:
        return JsonResponse({'status': False, 'msg': '无效的订单!'})
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,  # 应用id
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem'),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )
    while True:
        # 支付宝接口查询订单支付状态
        response = alipay.api_alipay_trade_query(order_id)
        code = response.get('code')

        if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
            # 支付成功
            # 获取支付宝交易号
            trade_no = response.get('trade_no')
            # 更新订单状态
            order.trade_no = trade_no
            order.status = 1
            order.save()
            # 返回结果
            key = 'order_' + username
            conn = get_redis_connection()
            conn.hdel(key, order_id)
            return JsonResponse({'status': True, 'msg': '支付成功!'})
        elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
            # 等待买家付款
            # 业务处理失败，可能一会就会成功
            import time
            time.sleep(5)
            continue
        else:
            # 支付出错
            print(code)
            return JsonResponse({'status': False, 'msg': '支付失败!'})
