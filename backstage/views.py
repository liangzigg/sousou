from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View

from order.models import Order
from user.models import UserInfo


def index(request):
    """后台管理首页"""
    uid = request.session.get('uid')
    user = UserInfo.objects.get(pk=uid)
    return render(request, 'backstage/index.html', locals())


class Administrators(View):
    """管理员管理"""

    def get(self, request):
        users = UserInfo.objects.filter(user_status__in=[0, 1])
        now = datetime.now()
        return render(request, 'backstage/administrators.html', locals())

    def post(self, request):
        """权限修改"""
        uid = request.POST.get('uid')
        operation = request.POST.get('type')
        status = request.session.get('status')
        try:
            user = UserInfo.objects.get(pk=uid)
        except UserInfo.DoesNotExist:
            return JsonResponse({'status': False, 'msg': '用户ID获取错误!'})
        if operation == '升权':  # 提升权限操作
            if status == 0:
                user.user_status -= 1
            elif status == 1:
                user.user_status = 1
        elif operation == '降权':  # 降低权限操作
            if status == 0:
                user.user_status += 1
            elif status == 1:
                user.user_status = 2
        user.save()
        if operation == '删除':  # 删除用户
            user.delete()
        if user.user_status not in [0, 1, 2]:
            return JsonResponse({'status': False, 'msg': '权限错误!'})
        return JsonResponse({'status': True, 'msg': '修改成功!'})


class Common(View):
    """普通用户管理"""

    def get(self, request):
        users = UserInfo.objects.filter(user_status=2)
        now = datetime.now()
        return render(request, 'backstage/common.html', locals())


class OrdersInfo(View):
    """订单管理"""

    def get(self, request):
        """获取订单信息"""
        ostatus = request.GET.get('ostatus')
        orders = Order.objects.filter(status=int(ostatus))
        now = datetime.now()
        return render(request, 'backstage/order.html', locals())

    def post(self, request):
        """修改订单状态"""
        oid = request.POST.get('oid')
        operation = request.POST.get('type')
        if not all([oid, operation]):
            return JsonResponse({'status': False, 'msg': '操作失败!'})
        try:
            order = Order.objects.get(pk=oid)
        except Order.DoesNotExist:
            return JsonResponse({'status': False, 'msg': '订单号错误!'})
        result = {'status': True}
        if operation == '删除':
            order.delete()
            result['msg'] = '成功删除订单!'
            return JsonResponse(result)
        elif operation == '取消':
            order.status = 5
            result['msg'] = '成功取消订单!'
        elif operation == '接单':
            order.status = 2
            result['msg'] = '接单成功!'
        elif operation == '取货':
            order.status = 3
            result['msg'] = '确认取货成功!'
        else:
            result['status'] = False
            result['msg'] = '操作失败!'
        order.save()
        return JsonResponse(result)
