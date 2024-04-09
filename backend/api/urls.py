from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    FavouriteRecipeViewSet,
    RecipeShoppingCartViewSet,
    GETShoppingCartText
)

router_v1 = SimpleRouter()
router_v1.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients',
)
router_v1.register(
    r'tags',
    TagViewSet,
    basename='tags',
)
router_v1.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavouriteRecipeViewSet,
    basename='favourite_recipe'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    RecipeShoppingCartViewSet,
    basename='recipe_shopping_cart'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/download_shopping_cart',
    GETShoppingCartText,
    basename='download_shopping_cart'
)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
