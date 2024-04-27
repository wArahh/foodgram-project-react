from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram.models import (FavoriteRecipe, Follow, Ingredient,
                             IngredientAmountForRecipe, Recipe,
                             RecipeShoppingCart, Tag, User)
from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer)

CANNOT_FOLLOW_TWICE = 'Нельзя подписаться на одного пользователя дважды'
CANNOT_FOLLOW_YOURSELF = 'Нельзя подписаться на себя'
CANNOT_SHOPPING_CARTED_TWICE = 'Нельзя добавить в список покупок дважды'
CANNOT_FAVORITED_TWICE = 'Нельзя добавть в избранное дважды'
CANNOT_DELETE_NONE = 'Нельзя удалить пустоту'


class CustomUserViewSet(UserViewSet):
    pagination_class = PageLimitPagination
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        user = self.request.user
        follow_to = get_object_or_404(
            User,
            id=self.kwargs['id']
        )
        request_follow = Follow.objects.filter(
            subscriber=user,
            subscribed_to=follow_to
        )
        if self.request.method == 'POST':
            if user == follow_to:
                return Response(
                    CANNOT_FOLLOW_YOURSELF,
                    status=HTTP_400_BAD_REQUEST
                )
            elif request_follow.exists():
                return Response(
                    CANNOT_FOLLOW_TWICE,
                    status=HTTP_400_BAD_REQUEST
                    # просит Postman,
                    # но по факту бессмысленно с UniqueTogether
                )
            return Response(
                FollowSerializer(
                    Follow.objects.create(
                        subscriber=user,
                        subscribed_to=follow_to
                    ),
                    context={'request': request}
                ).data,
                status=HTTP_201_CREATED
            )
        if request_follow.exists():
            request_follow.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=['GET'],
        pagination_class=PageLimitPagination,
    )
    def subscriptions(self, request):
        return self.get_paginated_response(FollowSerializer(
            self.paginate_queryset(
                Follow.objects.filter(
                    subscriber_id=self.request.user,
                )),
            context={'request': request},
            many=True,
        ).data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name_starts_with = self.request.query_params.get(
            'name',
        )
        if name_starts_with:
            queryset = queryset.filter(name__istartswith=name_starts_with)
        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PageLimitPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredient_list = IngredientAmountForRecipe.objects.filter(
            recipe__shopping_carted__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(quantity=Sum('amount'))
        ingredient_response = []
        for ingredient in ingredient_list:
            quantity = ingredient['quantity']
            measurement_unit = ingredient['ingredient__measurement_unit']
            name = ingredient['ingredient__name']
            ingredient_response.append(f'{quantity} {measurement_unit} {name}')

        return Response(
            ingredient_response,
            content_type='text/plain',
            status=HTTP_200_OK
        )

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        return self.recipe_section(
            RecipeShoppingCart,
            CANNOT_SHOPPING_CARTED_TWICE
        )

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        return self.recipe_section(
            FavoriteRecipe,
            CANNOT_FAVORITED_TWICE
        )

    def recipe_section(self, SectionModel, answer_if_twice,):
        user = self.request.user
        if not self.request.user.is_authenticated:
            return Response(HTTP_401_UNAUTHORIZED)
        try:
            recipe = Recipe.objects.get(
                id=self.kwargs['id']
                # достаточно get_object_or_404, но Postman требует 400
            )
        except Recipe.DoesNotExist:
            if self.request.method == 'POST':
                return Response(
                    status=HTTP_400_BAD_REQUEST
                )
            return Response(
                status=HTTP_404_NOT_FOUND
            )
        get_section = SectionModel.objects.filter(
            user=user,
            recipe=recipe
        )
        if self.request.method == 'POST':
            if get_section.exists():
                return Response(
                    answer_if_twice,
                    status=HTTP_400_BAD_REQUEST
                    # просит Postman,
                    # но по факту бессмысленно с UniqueTogether
                )
            SectionModel.objects.create(
                user=user,
                recipe=recipe
            )
            recipe_data = ShortRecipeSerializer(
                recipe
            ).data
            return Response(
                recipe_data,
                status=HTTP_201_CREATED
            )
        if not get_section.exists():
            return Response(
                CANNOT_DELETE_NONE,
                status=HTTP_400_BAD_REQUEST
            )
        get_section.delete()
        return Response(status=HTTP_204_NO_CONTENT)
