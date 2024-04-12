from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_200_OK
from rest_framework.generics import ListAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from foodgram.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    Tag,
    User,
)
from .serializers import (
    FavoriteRecipeSerializer,
    FollowSerializer,
    CertainFollowSerializer,
    IngredientSerializer,
    ProfileSerializer,
    RecipeSerializer,
    RecipeShoppingCartSerializer,
    TagSerializer,
    CustomUserSerializer,
)


class GETOnly(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    pass


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer


class IngredientViewSet(GETOnly):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)


class TagViewSet(GETOnly):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'post', 'patch', 'delete',)


class RecipeSectionViewSet(ModelViewSet):
    serializer_class = FavoriteRecipe
    http_method_names = ('post', 'delete',)
    permission_classes = (IsAuthenticated,)

    def get_recipe(self):
        return get_object_or_404(
            Recipe,
            id=self.kwargs.get('recipe_id')
        )

    def get_queryset(self):
        return FavoriteRecipe.objects.filter(
            recipe=self.get_recipe()
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            recipe=self.get_recipe()
        )


class FavouriteRecipeViewSet(RecipeSectionViewSet):
    serializer_class = FavoriteRecipeSerializer


class RecipeShoppingCartViewSet(RecipeSectionViewSet):
    serializer_class = RecipeShoppingCartSerializer


class ShoppingCartTextListView(
    ListModelMixin,
    GenericViewSet
):
    serializer_class = RecipeShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        with open('shopping_cart.txt', 'w') as file:
            file.write(str(response.data))
        return Response(
            data=response.data,
            status=HTTP_200_OK
        )


class FollowViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowListView(
    ListAPIView,
    GenericViewSet
):
    serializer_class = CertainFollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()


class CertainProfileView(
    RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)
