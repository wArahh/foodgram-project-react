from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ModelSerializer, SlugRelatedField
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


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name'
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = fields


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = fields


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField()

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
            'cooking_time'
        )


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


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = fields
