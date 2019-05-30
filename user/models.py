from django.db import models
from werkzeug.security import generate_password_hash, check_password_hash


class UserInfo(models.Model):
    """用户信息"""
    USER_STATUS = (
        (0, '超级管理员'),
        (1, '管理员'),
        (2, '普通用户'),
    )
    username = models.CharField('用户名', max_length=15, unique=True)
    _password = models.CharField('密码', max_length=128)
    email = models.EmailField('用户邮箱')
    user_status = models.SmallIntegerField(choices=USER_STATUS, default=2)  # 默认为普通用户
    balance = models.DecimalField(max_digits=7, decimal_places=2, default=0)  # 账户余额
    last_login = models.DateTimeField('最后登录时间', auto_now_add=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        """加密存储密码"""
        self._password = generate_password_hash(pwd)

    def check_password(self, pwd):
        """验证密码"""
        return check_password_hash(self._password, pwd)


class Address(models.Model):
    """用户地址簿"""
    recv_name = models.CharField('联系人', max_length=20)
    liaison = models.CharField('联系方式', max_length=11)
    address_detailed = models.CharField('地址', max_length=50)
    address_longitude = models.DecimalField('经度', max_digits=9, decimal_places=6)
    address_latitude = models.DecimalField('纬度', max_digits=9, decimal_places=6)
    address_number = models.CharField('门牌号', max_length=20, null=True)
    address_type = models.BooleanField(default=False)  # False为发货地址 True为收货地址
    is_default = models.BooleanField(default=False)  # 是否为默认收/发货地址
    uid = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)  # 外键关联用户

    class Meta:
        unique_together = ('address_detailed', 'address_number', 'address_type')


class Refund(models.Model):
    """退款记录"""
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to='UserInfo', on_delete=models.DO_NOTHING)
    order = models.ForeignKey(to='order.Order', on_delete=models.DO_NOTHING)
