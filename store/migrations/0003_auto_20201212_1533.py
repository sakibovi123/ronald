# Generated by Django 3.1.2 on 2020-12-12 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_city_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='id',
        ),
        migrations.AlterField(
            model_name='order',
            name='invoice',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
