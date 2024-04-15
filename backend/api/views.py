from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets
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
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

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
    RecipeSerializer,
    RecipeShoppingCartSerializer,
    TagSerializer,
    CustomUserSerializer
)
from .permissions import IsAuthenticatedOrReadOnly
from .pagination import PageLimitPagination


class CustomUserViewSet(UserViewSet):
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.request.path.endswith('me/'):
            return (IsAuthenticated(),)
        elif self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()


class GETOnly(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    pass


class IngredientViewSet(GETOnly):
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name_starts_with = self.request.query_params.get('name', None)
        if name_starts_with:
            queryset = queryset.filter(name__istartswith=name_starts_with)
        return queryset


class TagViewSet(GETOnly):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
