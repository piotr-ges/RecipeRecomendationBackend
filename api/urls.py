from django.urls import path
from .views import recommend_recipes

urlpatterns = [
    path('api/recommend/', recommend_recipes, name='recommend_recipes'),
]