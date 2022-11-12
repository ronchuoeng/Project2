# Generated by Django 4.1.2 on 2022-11-12 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='New_listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('description', models.TextField(max_length=1000)),
                ('s_bid', models.DecimalField(decimal_places=2, max_digits=8)),
                ('img', models.URLField()),
                ('category', models.URLField()),
            ],
        ),
    ]
