# Generated by Django 2.0.6 on 2019-05-13 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20190513_0217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='value',
            field=models.CharField(default='50元以下', max_length=20),
        ),
    ]