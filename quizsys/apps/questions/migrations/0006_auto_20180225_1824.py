# Generated by Django 2.0.2 on 2018-02-25 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_auto_20180129_2332'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='choice',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='testcase',
            options={'ordering': ['-created_at']},
        ),
    ]