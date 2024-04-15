from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ModelSerializer, SlugRelatedField, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer

from foodgram.models import (
    FavoriteRecipe,
    Follow,
    Ingredient,
    Recipe,
    RecipeShoppingCart,
    Tag,
    User
)
from .fields import Base64ImageField


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, another_user):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(
                user=self.context['request'].user, following=another_user
            ).exists()
        return False


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeSerializer(ModelSerializer): #TODO PrimaryKeyRelatedField(get)/ToRepresentasian
    tags = TagSerializer(
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientSerializer(
        many=True,
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, favorited_recipe):
        if self.context['request'].user.is_authenticated:
            return FavoriteRecipe.objects.filter(
                user=self.context['request'].user,
                recipe=favorited_recipe
                ).exists()
        return False

    def get_is_in_shopping_cart(self, shopping_cart_object):
        if self.context['request'].user.is_authenticated:
            return RecipeShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=shopping_cart_object
            ).exists()
        return False


class RecipeSectionSerializer(ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        fields = (
            'id',
            'user',
            'recipe'
        )


class FavoriteRecipeSerializer(RecipeSectionSerializer):
    class Meta:
        Model = FavoriteRecipe


class RecipeShoppingCartSerializer(RecipeSectionSerializer):
    class Meta:
        Model = RecipeShoppingCart


class FollowSerializer(ModelSerializer):
    user = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=CurrentUserDefault()
    )
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    validators = UniqueTogetherValidator(
        queryset=Follow.objects.all(),
        fields=('user', 'following'),
        message='Вы уже подписаны на пользователя'
    ),

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, following):
        if self.context['request'].user == following['following']:
            raise ValidationError(
                'Нельзя подписаться на себя'
            )
        return following


class CertainFollowSerializer(ModelSerializer):
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all
    )
    recipes = RecipeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'id',
            'following',
            'recipes'
        )
