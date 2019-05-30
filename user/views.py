from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

from order.models import Order
from user.models import UserInfo, Address, Refund
from tools.db import is_legal, check_info


def login(request):
    """用户登录"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    if not all([username, password]):
        return JsonResponse({'status': False, 'msg': '用户信息填写不完整!'})
    legal, info = is_legal(username, password)
    if not legal:
        return JsonResponse({'status': False, 'msg': info})
    request.session['is_login'] = True
    request.session['username'] = info.username
    request.session['uid'] = info.id
    request.session['status'] = info.user_status
    info.last_login = datetime.now()
    info.save()
    ret = JsonResponse({'status': True, 'msg': '登录成功！'})
    ret.set_cookie(
        'username', username.encode('utf-8').decode('latin-1'),
        max_age=14 * 24 * 3600
    )
    return ret


def register(request):
    """用户注册"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    print(username, password, email)
    legal, ret = check_info(username, password, email)
    if not legal:
        return ret
    with transaction.atomic():
        UserInfo.objects.create(
            username=username, password=password, email=email
        )
    return JsonResponse({'status': True, 'msg': '注册成功!'})


def logout(request):
    """用户注销"""
    if not request.session.get('is_login'):
        return redirect('index')
    request.session.flush()
    return render(request, 'index.html')


def address(request):
    """地址簿"""
    if not request.session.get('is_login'):
        return redirect('index')
    return render(request, 'address.html')


def address_query(request):
    """查询收发地址"""
    if not request.session.get('is_login'):
        return JsonResponse({'status': '0', 'msg': '请登录!'})
    try:
        atype = request.GET.get('type')
        atype = True if int(atype) == 1 else False
        uid = request.session.get('uid')
        user = UserInfo.objects.get(pk=uid)
        address_list = Address.objects.filter(uid=user, address_type=atype).values()
        if not address_list:
            return JsonResponse({'status': '1', 'msg': '暂无地址'})
        return JsonResponse({'status': '2', 'address_list': list(address_list)})
    except UserInfo.DoesNotExist:
        return JsonResponse({'status': '3', 'msg': '非法请求!'})
    except TypeError:
        aid = request.GET.get('aid')
        address = Address.objects.filter(id=int(aid)).values()
        return JsonResponse({'status': '4', 'msg': list(address)})


def delete_address(request):
    """删除地址"""
    params = request.GET
    address = dict(params)
    save_id = transaction.savepoint()
    try:
        for add in address['delete_addresses']:
            Address.objects.filter(address_detailed=add).delete()
    except Exception:
        transaction.savepoint_rollback(save_id)
        return JsonResponse({'status': False, 'msg': '删除失败!地址可能已与订单绑定!'})
    transaction.savepoint_commit(save_id)
    return JsonResponse({'status': True, 'msg': '删除成功!'})


def wallet(request):
    """用户钱包"""
    if not request.session.get('is_login'):
        return redirect('index')
    username = request.session.get('username')
    user = UserInfo.objects.get(username=username)
    today = datetime.now().date()
    order_list = Order.objects.filter(uid=user, status=4)
    total_consumption = 0
    for order in order_list:
        total_consumption += order.cost
    return render(request, 'wallet.html', locals())


def query_refund(request):
    """查询退款记录"""
    if not request.session.get('is_login'):
        return redirect('index')
    uid = request.session.get('uid')
    user = UserInfo.objects.get(pk=uid)
    results = Refund.objects.filter(user=user)
    today = datetime.now().date()
    return render(request, 'refund.html', locals())
