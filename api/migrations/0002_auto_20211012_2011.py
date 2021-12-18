# Generated by Django 3.2.7 on 2021-10-12 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attraction_Voting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='City_Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='City_Voting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Nation_Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Nation_Voting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant_Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant_Voting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Stay_Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Stay_Voting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField()),
            ],
        ),
        migrations.RenameModel(
            old_name='Image',
            new_name='Attraction_Image',
        ),
        migrations.RemoveField(
            model_name='voting',
            name='item_vote',
        ),
        migrations.RenameField(
            model_name='attraction',
            old_name='city_id',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='city',
            old_name='nation_id',
            new_name='nation',
        ),
        migrations.RenameField(
            model_name='restaurant',
            old_name='city_id',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='stay',
            old_name='city_id',
            new_name='city',
        ),
        migrations.RemoveField(
            model_name='attraction',
            name='global_id',
        ),
        migrations.RemoveField(
            model_name='city',
            name='global_id',
        ),
        migrations.RemoveField(
            model_name='nation',
            name='global_id',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='global_id',
        ),
        migrations.RemoveField(
            model_name='stay',
            name='global_id',
        ),
        migrations.AlterField(
            model_name='attraction_image',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.attraction'),
        ),
        migrations.DeleteModel(
            name='GlobalId',
        ),
        migrations.DeleteModel(
            name='Voting',
        ),
        migrations.AddField(
            model_name='stay_voting',
            name='item_vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.stay'),
        ),
        migrations.AddField(
            model_name='stay_voting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stay_image',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.stay'),
        ),
        migrations.AddField(
            model_name='restaurant_voting',
            name='item_vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.restaurant'),
        ),
        migrations.AddField(
            model_name='restaurant_voting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='restaurant_image',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.restaurant'),
        ),
        migrations.AddField(
            model_name='nation_voting',
            name='item_vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.nation'),
        ),
        migrations.AddField(
            model_name='nation_voting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='nation_image',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.nation'),
        ),
        migrations.AddField(
            model_name='city_voting',
            name='item_vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.city'),
        ),
        migrations.AddField(
            model_name='city_voting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='city_image',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.city'),
        ),
        migrations.AddField(
            model_name='attraction_voting',
            name='item_vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.attraction'),
        ),
        migrations.AddField(
            model_name='attraction_voting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]