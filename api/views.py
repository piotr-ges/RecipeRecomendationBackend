from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe, FavouriteRecipe
import json
from django.contrib.auth.models import User

from .serializers import RegisterSerializer, FavouriteRecipeSerializer, RecipeSerializer, RecipeSummarySerializer, \
    FavouriteRecipeSummarySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class FavouriteRecipeListCreateView(generics.ListCreateAPIView):
    serializer_class = FavouriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavouriteRecipe.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            # Dla listy ulubionych (GET) - użyj "lekkiego" serializera
            return FavouriteRecipeSummarySerializer
        else:
            # Dla POST (tworzenia) lub innych - pełny serializer
            return FavouriteRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)


class FavouriteRecipeDeleteView(generics.DestroyAPIView):
    serializer_class = FavouriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavouriteRecipe.objects.filter(user=self.request.user)


class FavouriteRecipeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = FavouriteRecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavouriteRecipe.objects.filter(user=self.request.user)
