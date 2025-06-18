from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Recipe, FavouriteRecipe


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class FavouriteRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), write_only=True, source='recipe'
    )

    class Meta:
        model = FavouriteRecipe
        fields = ['id', 'user', 'recipe', 'recipe_id']
        read_only_fields = ['user']


class RecipeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'ner']


class FavouriteRecipeSummarySerializer(serializers.ModelSerializer):
    recipe = RecipeSummarySerializer(read_only=True)  # tutaj skrócony serializer przepisu

    class Meta:
        model = FavouriteRecipe
        fields = ['id', 'recipe']