# Generated by Django 5.2.3 on 2025-06-12 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_recipe_link_alter_recipe_site_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="directions",
            field=models.TextField(),
        ),
    ]
