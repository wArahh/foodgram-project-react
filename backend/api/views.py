from collections import defaultdict

from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from foodgram.models import (
    FavoriteRecipe,
    Follow,
    Ingredient,
    Recipe,
    RecipeShoppingCart,
    Tag,
    User
)

from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    FollowSerializer,
    GETRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer
)

CANNOT_FOLLOW_TWICE = 'Нельзя подписаться на одного пользователя дважды'
CANNOT_FOLLOW_YOURSELF = 'Нельзя подписаться на себя'
CANNOT_SHOPPING_CARTED_TWICE = 'Нельзя добавить в список покупок дважды'
CANNOT_FAVORITED_TWICE = 'Нельзя добавть в избранное дважды'


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
    def subscribe(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = self.request.user
            follow_to = get_object_or_404(
                User,
                id=self.kwargs['id']
            )
            if self.request.method == 'POST':
                if user == follow_to:
                    return Response(
                        CANNOT_FOLLOW_YOURSELF,
                        status=HTTP_400_BAD_REQUEST
                    )
                elif Follow.objects.filter(
                        subscriber=user,
                        subscribed_to=follow_to
                ).exists():
                    return Response(
                        CANNOT_FOLLOW_TWICE,
                        status=HTTP_400_BAD_REQUEST
                        # просит Postman,
                        # но по факту бессмысленно с UniqueTogether
                    )
                Follow.objects.create(
                    subscriber=user,
                    subscribed_to=follow_to
                )
                user_follow_to_data = FollowSerializer(
                    Follow.objects.get(
                        subscriber=user,
                        subscribed_to=follow_to,
                    ),
                    context={'request': request}
                ).data
                find_user_recipe = Recipe.objects.filter(
                    author=user
                )
                if 'recipes_limit' in request.GET:
                    find_user_recipe = Recipe.objects.filter(
                        author=follow_to
                    )[:int(request.GET['recipes_limit'])]
                recipe = ShortRecipeSerializer(
                    find_user_recipe,
                    context={'request': request},
                    many=True
                ).data
                recipes_count = find_user_recipe.count()
                response_data = {
                    'email': user_follow_to_data['email'],
                    'id': user_follow_to_data['id'],
                    'username': user_follow_to_data['username'],
                    'first_name': user_follow_to_data['first_name'],
                    'last_name': user_follow_to_data['last_name'],
                    'is_subscribed': user_follow_to_data['is_subscribed'],
                    'recipes': recipe,
                    'recipes_count': recipes_count,
                }
                return Response(
                    response_data,
                    status=HTTP_201_CREATED
                )
            elif self.request.method == 'DELETE':
                request_follow = Follow.objects.filter(
                    subscriber=user,
                    subscribed_to=follow_to
                )
                if request_follow.exists():
                    request_follow.delete()
                    return Response(status=HTTP_204_NO_CONTENT)
                return Response(status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_401_UNAUTHORIZED)

    @action(
        detail=False, methods=['GET'],
        pagination_class=PageLimitPagination,
    )
    def subscriptions(self, request):
        if self.request.user.is_authenticated:
            follow_data = FollowSerializer(
                Follow.objects.filter(
                    subscriber_id=self.request.user,
                ),
                many=True,
                context={'request': request}
            ).data
            response_data_list = []
            for user_data in follow_data:
                user_recipes = Recipe.objects.filter(
                    author=user_data['id']
                )
                if 'recipes_limit' in request.GET:
                    user_recipes = Recipe.objects.filter(
                        author=user_data['id']
                    )[:int(request.GET['recipes_limit'])]
                recipe = ShortRecipeSerializer(
                    self.paginate_queryset(user_recipes),
                    context={'request': request},
                    many=True
                ).data
                response_data = {
                    'email': user_data['email'],
                    'id': user_data['id'],
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_subscribed': user_data['is_subscribed'],
                    'recipes': recipe,
                    'recipes_count': len(recipe)
                }
                response_data_list.append(response_data)
            if 'limit' in request.GET:
                return Response(
                    self.get_paginated_response(
                        response_data_list[:int(request.GET['limit'])]
                    ).data,
                    status=HTTP_200_OK
                )
            return Response(
                self.get_paginated_response(
                    response_data_list
                ).data,
                status=HTTP_200_OK
            )
        return Response(status=HTTP_401_UNAUTHORIZED)


class GETOnly(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    pass


class TagViewSet(GETOnly):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(GETOnly):
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name_starts_with = self.request.query_params.get(
            'name',
            None
        )
        if name_starts_with:
            queryset = queryset.filter(name__istartswith=name_starts_with)
        return queryset


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

    def destroy(self, request, *args, **kwargs):
        try:
            recipe = Recipe.objects.select_related(
                'author'
            ).get(
                id=kwargs['id']
            )
        except Recipe.DoesNotExist:
            raise Http404
        if self.request.user != recipe.author:
            return Response(status=HTTP_403_FORBIDDEN)
        recipe.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        recipe_shopping_carts = RecipeShoppingCart.objects.filter(
            user=self.request.user
        ).select_related('recipe')
        shopping_cart_ingredients = defaultdict(int)
        for shopping_cart_data in recipe_shopping_carts:
            recipe_object = shopping_cart_data.recipe
            recipe_data = GETRecipeSerializer(
                recipe_object,
                context={'request': request}
            ).data
            ingredients = recipe_data['ingredients']
            for ingredient_data in ingredients:
                ingredient_name = ingredient_data['name']
                shopping_cart_ingredients[ingredient_name] += 1
        shopping_cart_list = []
        for ingredient_name, count in shopping_cart_ingredients.items():
            if count > 1:
                shopping_cart_list.append(f'{count} {ingredient_name}')
            else:
                shopping_cart_list.append(ingredient_name)
        shopping_cart_text = ', '.join(shopping_cart_list)
        return Response(
            shopping_cart_text,
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
        if self.request.user.is_authenticated:
            if self.request.method == 'POST':
                try:
                    recipe = Recipe.objects.get(
                        id=self.kwargs['id']
                        # достаточно get_object_or_404, но Postman требует 400
                    )
                except Recipe.DoesNotExist:
                    return Response(
                        status=HTTP_400_BAD_REQUEST
                    )
                if SectionModel.objects.filter(
                        user=user,
                        recipe=recipe
                ).exists():
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
            elif self.request.method == 'DELETE':
                recipe = get_object_or_404(
                    Recipe,
                    id=self.kwargs['id']
                    # тупая конструкция,
                    # но при одинаковых неверных
                    # данных нужно вызвать разные ответы
                )
                try:
                    SectionModel.objects.get(
                        user=user,
                        recipe=recipe
                    ).delete()
                except SectionModel.DoesNotExist:
                    return Response(status=HTTP_400_BAD_REQUEST)
                return Response(status=HTTP_204_NO_CONTENT)
        return Response(HTTP_401_UNAUTHORIZED)
