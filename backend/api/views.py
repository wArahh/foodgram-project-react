from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_204_NO_CONTENT
from rest_framework.mixins import (
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
    Follow
)
from .serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeShoppingCartSerializer,
    TagSerializer,
)
from .permissions import IsAuthenticatedOrReadOnly
from .pagination import PageLimitPagination
from .filters import RecipeFilter


class CustomUserViewSet(UserViewSet):
    pagination_class = PageLimitPagination
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        if self.request.path.endswith('me/'):
            return (IsAuthenticated(),)
        elif self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, pk=None, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            follow_to = get_object_or_404(User, id=self.kwargs['id'])
            if self.request.method == 'POST':
                Follow.objects.create(
                    subscriber=user, subscribed_to=follow_to
                )
                return Response(status=HTTP_201_CREATED)
            elif self.request.method == 'DELETE':
                Follow.objects.filter(
                    subscriber=user, subscribed_to=follow_to
                ).delete()
                return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_401_UNAUTHORIZED)


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
    filterset_class = RecipeFilter
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
