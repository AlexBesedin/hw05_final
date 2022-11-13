# Generated by Django 2.2.16 on 2022-11-10 13:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0003_auto_20221109_1309"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={
                "ordering": ["-created"],
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
        migrations.AddField(
            model_name="post",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата публикации",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="comment",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Дата публикации"
            ),
        ),
    ]