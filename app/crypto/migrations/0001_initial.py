# Generated by Django 4.0.7 on 2022-08-19 21:39

import crypto.utils
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crypto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(help_text='Crypto Ticker used for querying from CoinMarketCap', max_length=10)),
                ('display_name', models.CharField(help_text='Used as the header when charting', max_length=64)),
                ('show_overall', models.BooleanField(default=False, help_text='Show overall value instead of current price')),
                ('show_chart', models.BooleanField(default=False, help_text='Show 7-day chart with price trend on Dashboard', verbose_name='Chart crypto')),
                ('image', models.ImageField(default='crypto/default.png', upload_to=crypto.utils.crypto_image_path)),
                ('enabled', models.BooleanField(default=True, help_text='Hides crypto from Dashboard and does not pull further information')),
                ('order', models.PositiveSmallIntegerField(default=999)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('order', 'symbol'),
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Wallet', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CryptoPurchases',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('buy_price', models.FloatField(help_text='If no buy price is specified, it will be looked up on CoinMarketCap based on the buying timestamp (requires Advanced API plan)')),
                ('buy_currency', models.CharField(max_length=4)),
                ('target_price', models.FloatField(blank=True, help_text='Automatically converts buying price into localized-target price if left empty')),
                ('target_currency', models.CharField(blank=True, help_text='Automatically converty buying price into localized-target price if left empty', max_length=4)),
                ('bought_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='crypto.crypto')),
            ],
            options={
                'verbose_name': 'Purchase',
            },
        ),
        migrations.CreateModel(
            name='CryptoData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_price', models.FloatField()),
                ('source_currency', models.CharField(max_length=4)),
                ('target_price', models.FloatField()),
                ('target_currency', models.CharField(max_length=4)),
                ('percent_day', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='24h Percentual Change')),
                ('rank', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='crypto.crypto')),
            ],
            options={
                'verbose_name': 'Price Data',
                'verbose_name_plural': 'Price Data',
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.AddField(
            model_name='crypto',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.wallet'),
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(help_text='Price of crypto in target currency to surpass')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.crypto')),
            ],
            options={
                'verbose_name': 'Price Alert',
            },
        ),
    ]
