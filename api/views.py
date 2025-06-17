from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Recipe
import json

@api_view(['POST'])
def recommend_recipes(request):
    user_ingredients = request.data.get('ingredients', [])

    if not user_ingredients:
        return Response({"error": "Missing ingredients"}, status=400)

    recommendations = []

    for recipe in Recipe.objects.all():
        try:
            recipe_ingredients = recipe.ner
        except json.JSONDecodeError:
            continue

        match_count = len(set(user_ingredients) & set(recipe_ingredients))

        if match_count > 0:
            recommendations.append({
                "title": recipe.title,
                "match_count": match_count,
                "total_ingredients": len(recipe_ingredients),
                "link": recipe.link
            })

    # sortujemy po liczbie dopasowań
    recommendations.sort(key=lambda x: x['match_count'], reverse=True)

    return Response(recommendations[:10])  # Top 10 przepisów
