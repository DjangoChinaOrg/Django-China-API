from django.conf import settings
from django.db import models


class Record(models.Model):
    REWARD_TYPE = (
        (0, '每日签到奖励'),
    )

    COIN_TYPE = (
        (0, '金币'),
        (1, '银币'),
        (2, '铜币'),
    )

    created_time = models.DateTimeField("创建时间", auto_now_add=True)
    reward_type = models.IntegerField("奖励类型", choices=REWARD_TYPE)
    coin_type = models.IntegerField("钱币类型", choices=COIN_TYPE)
    amount = models.PositiveIntegerField("数额")
    description = models.CharField("描述", max_length=300, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户")

    class Meta:
        verbose_name = "奖励记录"
        verbose_name_plural = "奖励记录"

    def __str__(self):
        return '%s:%s:%s -> %s' % (self.reward_type, self.coin_type, self.amount, self.user)
