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
    HTTP_401_UNAUTHORIZED
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from foodgram.models import (
    User,
    Follow,
    Tag,
    Ingredient,
    Recipe,
)

from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    ShortRecipeForFollowingSerializer,
    RecipeSerializer,
    FollowSerializer
)

CANNOT_FOLLOW_TWICE = 'Нельзя подписаться на одного пользователя дважды'
CANNOT_FOLLOW_YOURSELF = 'Нельзя подписаться на себя'


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
            user = get_object_or_404(User, id=request.user.id)
            follow_to = get_object_or_404(User, id=self.kwargs['id'])
            if self.request.method == 'POST':
                if user == follow_to:
                    return Response(
                        CANNOT_FOLLOW_YOURSELF, status=HTTP_400_BAD_REQUEST
                    )
                elif Follow.objects.filter(
                        subscriber=user,
                        subscribed_to=follow_to
                ).exists():
                    return Response(
                        CANNOT_FOLLOW_TWICE, status=HTTP_400_BAD_REQUEST
                    )
                Follow.objects.create(
                    subscriber=user,
                    subscribed_to=follow_to
                )
                follow_data = FollowSerializer(
                    Follow.objects.get(
                        subscriber=user,
                        subscribed_to=follow_to,
                    ),
                    context={'request': request}
                ).data
                find_user_recipe = Recipe.objects.filter(author=user)
                if 'recipes_limit' in request.GET:
                    find_user_recipe = Recipe.objects.filter(
                        author=follow_to
                    )[:int(request.GET['recipes_limit'])]
                recipe = ShortRecipeForFollowingSerializer(
                    find_user_recipe,
                    context={'request': request},
                    many=True
                ).data
                recipes_count = find_user_recipe.count()
                response_data = {
                    'email': follow_data['email'],
                    'id': follow_data['id'],
                    'username': follow_data['username'],
                    'first_name': follow_data['first_name'],
                    'last_name': follow_data['last_name'],
                    'is_subscribed': follow_data['is_subscribed'],
                    'recipes': recipe,
                    'recipes_count': recipes_count,
                }
                return Response(
                    response_data,
                    status=HTTP_201_CREATED
                )
            elif self.request.method == 'DELETE':
                Follow.objects.filter(
                    subscriber=user, subscribed_to=follow_to
                ).delete()
                return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        if self.request.user.is_authenticated:
            follow_data = FollowSerializer(
                Follow.objects.all(),
                many=True,
                context={'request': request}
            ).data
            response_data_list = []
            for user_data in follow_data:
                user_recipes = Recipe.objects.filter(author=user_data['id'])
                if 'recipes_limit' in request.GET:
                    user_recipes = Recipe.objects.filter(
                        author=user_data['id']
                    )[:int(request.GET['recipes_limit'])]
                recipe = ShortRecipeForFollowingSerializer(
                    user_recipes,
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
            return Response(
                response_data_list,
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
        name_starts_with = self.request.query_params.get('name', None)
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
