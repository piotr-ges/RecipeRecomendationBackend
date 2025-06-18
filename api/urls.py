from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    recommend_recipes,
    RegisterView,
    FavouriteRecipeListCreateView,
    RecipeDetailView,
    FavouriteRecipeDeleteView,
    FavouriteRecipeDetailView
)


urlpatterns = [
    path('api/recommend/', recommend_recipes, name='recommend_recipes'),
    path('api/token/', obtain_auth_token),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('api/favourites/', FavouriteRecipeListCreateView.as_view(), name='favourite-list-create'),
    path('favourites/<int:pk>/', FavouriteRecipeDeleteView.as_view(), name='favourite-delete'),
    path('api/favourites/<int:pk>/', FavouriteRecipeDetailView.as_view(), name='favourite-detail'),

    # OpenAPI schema (plik JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc UI (opcjonalnie)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]