from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, mixins, pagination, status

from foodgram.models import (
    Ingredient,
    Tag,
    Recipe,
    FavoriteRecipe
)
from rest_framework.response import Response

from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    FavoriteRecipeSerializer,
    RecipeShoppingCartSerializer
)


class GetOnly(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class IngredientViewSet(GetOnly):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TagViewSet(GetOnly):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = (pagination.LimitOffsetPagination,)
    http_method_names = ('get', 'post', 'patch', 'delete',)


class RecipeSectionViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteRecipe
    pagination_class = (pagination.LimitOffsetPagination,)
    http_method_names = ('post', 'delete',)
    permission_classes = (permissions.IsAuthenticated,)

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


class GETShoppingCartText(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = RecipeShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        with open('shopping_cart.txt', 'w') as file:
            file.write(str(response.data))
        return Response(
            data=response.data,
            status=status.HTTP_200_OK
        )
