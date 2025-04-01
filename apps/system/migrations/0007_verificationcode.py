# Generated by Django 4.2.11 on 2025-01-07 02:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_user_line_bind_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改时间', verbose_name='修改时间')),
                ('is_deleted', models.BooleanField(default=False, help_text='删除标记', verbose_name='删除标记')),
                ('code', models.CharField(max_length=6, verbose_name='驗證碼')),
                ('is_used', models.BooleanField(default=False, verbose_name='是否已使用')),
                ('expires_at', models.DateTimeField(verbose_name='過期時間')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP位址')),
                ('attempt_count', models.IntegerField(default=0, verbose_name='嘗試次數')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='員工')),
            ],
            options={
                'verbose_name': '驗證碼',
                'verbose_name_plural': '驗證碼',
                'ordering': ['-create_time'],
            },
        ),
    ]
