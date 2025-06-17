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
