from PIL import Image
from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe, FavouriteRecipe
import json
from django.contrib.auth.models import User

from .serializers import RegisterSerializer, FavouriteRecipeSerializer, RecipeSerializer, RecipeSummarySerializer, \
    FavouriteRecipeSummarySerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes
from rest_framework.parsers import MultiPartParser
from ultralytics import YOLO


model = YOLO('api/yolo11v05.pt')

@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'ingredients': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            },
            'required': ['ingredients']
        }
    },
    responses=OpenApiTypes.OBJECT,
    methods=["POST"],
    description="Zwraca rekomendacje przepisów na podstawie listy składników."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_recipes(request):
    user_ingredients = request.data.get('ingredients', [])

    if not user_ingredients:
        return Response({"error": "Missing ingredients"}, status=400)

    user_ingredients_set = set(user_ingredients)

    query = Q()
    for ingredient in user_ingredients:
        query |= Q(ner__contains=[ingredient])
    recipes = Recipe.objects.filter(query)

    recommendations = []

    for recipe in recipes:
        try:
            recipe_ingredients = set(recipe.ner)
        except json.JSONDecodeError:
            continue

        matched = user_ingredients_set & recipe_ingredients
        match_count = len(matched)

        if match_count == 0:
            continue

        match_percentage = (match_count / len(recipe_ingredients)) * 100

        if match_count > 0:
            recommendations.append({
                "id": recipe.id,
                "title": recipe.title,
                "match_count": match_count,
                "total_ingredients": len(recipe_ingredients),
                "match_percentage": round(match_percentage, 2),
                "link": recipe.link
            })

    # sortujemy po liczbie dopasowań
    recommendations.sort(key=lambda x: (-x['match_percentage'], x['total_ingredients']))

    return Response(recommendations[:10])  # Top 10 przepisów


@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {'type': 'string', 'format': 'binary'}
            },
            'required': ['image']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'ingredients': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['cheese', 'tomato', 'basil']
                }
            }
        },
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    },
    methods=["POST"],
    description="Przetwarza zdjęcie i zwraca listę wykrytych składników."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def process_image(request):
    image_file = request.FILES.get('image')

    if not image_file:
        return Response({"error": "Image is required"}, status=status.HTTP_400_BAD_REQUEST)

    def process_image_to_ingredients(image_file):
        image = Image.open(image_file)

        # Przetwarzanie modelem YOLO
        results = model.predict(image)

        # Zbierz unikalne etykiety
        detected_labels = set()
        for result in results:
            if result.boxes is not None:
                for cls_id in result.boxes.cls:
                    label = result.names[int(cls_id)]
                    detected_labels.add(label)

        return list(detected_labels)

    ingredients = process_image_to_ingredients(image_file)

    if not ingredients:
        return Response({"error": "No ingredients detected"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"ingredients": ingredients}, status=status.HTTP_200_OK)


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
