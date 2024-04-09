import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers, fields, validators, exceptions

from foodgram.models import Ingredient, Tag, Recipe, User, FavoriteRecipe, RecipeShoppingCart, Follow


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
            'password'
        )
        required_fields = fields


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = fields


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = fields


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = serializers.SlugRelatedField(
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


class RecipeSectionSerializer(serializers.ModelSerializer):
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


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=fields.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    validators = validators.UniqueTogetherValidator(
        queryset=Follow.objects.all(),
        fields=('user', 'following'),
        message='Вы уже подписаны на пользователя'
    ),

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, following):
        if self.context['request'].user == following['following']:
            raise exceptions.ValidationError(
                'Нельзя подписаться на себя'
            )
        return following


class GETFollowListSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(
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


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = fields
