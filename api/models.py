from django.contrib.auth.models import User
from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    ingredients = models.JSONField()  # lista stringów
    directions = models.JSONField()
    link = models.URLField(blank=True)
    source = models.CharField(max_length=255)
    ner = models.JSONField()  # czyste składniki (bez ilości)
    site = models.URLField(blank=True)

    def __str__(self):
        return self.title


class FavouriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')