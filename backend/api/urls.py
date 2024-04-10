from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    FavouriteRecipeViewSet,
    FollowViewSet,
    FollowListView,
    CertainProfileView,
    ShoppingCartTextListView,
    IngredientViewSet,
    RecipeShoppingCartViewSet,
    RecipeViewSet,
    TagViewSet
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
    ShoppingCartTextListView,
    basename='download_shopping_cart'
)
router_v1.register(
    r'users/(?P<user_id>\d+)/subscribe/',
    FollowViewSet,
    basename='follow'
)
router_v1.register(
    r'users/(?P<user_id>\d+)/subscriptions/',
    FollowListView,
    basename='follow_list'
)
router_v1.register(
    r'users/(?P<user_id>\d+)',
    CertainProfileView,
    basename='get_profile'
)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
