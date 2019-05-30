from django.db import models


class Order(models.Model):
    """订单表"""
    STATUS_CHOICES = [
        (0, '待支付'),
        (1, '待接单'),
        (2, '待取货'),
        (3, '配送中'),
        (4, '已完成'),
        (5, '已取消')
    ]
    PAY_CHOICES = [
        (0, '钱包'),
        (1, '在线支付'),
    ]
    id = models.CharField('订单ID', max_length=20, unique=True, primary_key=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)  # 订单状态
    create_time = models.DateTimeField(auto_now_add=True)  # 下单时间
    status_change_time = models.DateTimeField(auto_now=True)  # 订单状态修改时间
    demo = models.CharField(max_length=50, null=True)  # 订单备注
    cost = models.DecimalField(max_digits=7, decimal_places=2, default=10.0)  # 订单金额, 起价8元
    payment_method = models.SmallIntegerField(choices=PAY_CHOICES, default=1)
    driver = models.CharField(max_length=10, default='嗖嗖骑手')  # 配送者
    value = models.CharField(max_length=20, default='50元以下')  # 物品价值
    trade_no = models.CharField(max_length=128, default='', verbose_name='支付编号')
    stdmode = models.CharField(max_length=10, default='服饰鞋帽')  # 货物类型, 默认为'服饰鞋帽'
    uid = models.ForeignKey(to='user.UserInfo', on_delete=models.CASCADE)  # 所属用户
    recv_addr = models.ForeignKey(
        null=True,
        to='user.Address',
        on_delete=models.DO_NOTHING,
        related_name='o_recv')  # 收货地址
    sender_addr = models.ForeignKey(
        null=True,
        to='user.Address',
        on_delete=models.DO_NOTHING,
        related_name='o_send')  # 发货地址
