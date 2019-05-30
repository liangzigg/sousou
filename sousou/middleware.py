# -*- coding: utf-8 -*-
# create_time: 19-3-20
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from user.models import UserInfo


class CheckStatus(MiddlewareMixin):

    def process_request(self, request):
        # 在request到达view之前执行
        login_path = ['order', ]  # 需要登录权限才能访问的URL地址
        site = request.path_info.split('/')[1]  # 获取URL中的APP地址
        status = request.session.get('is_login')  # 获取session中的登录标识
        if not status and site in login_path:
            return redirect('index')
        if site == 'backstage':
            try:
                uid = request.session.get('uid')
                user = UserInfo.objects.get(pk=uid)
                if user.user_status not in [0, 1]:
                    return redirect('index')
            except UserInfo.DoesNotExist:
                return redirect('index')

    def process_response(self, request, response):
        # view执行之后 返回response之前执行
        return response
