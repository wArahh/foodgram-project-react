from django.shortcuts import get_object_or_404
from rest_framework.fields import IntegerField, ListField
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    PrimaryKeyRelatedField
)
from djoser.serializers import UserSerializer

from foodgram.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeShoppingCart,
    Tag,
    User,
    Follow,
    IngredientAmountForRecipe
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

    def get_is_subscribed(self, subscribed_to):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(
                subscriber=self.context['request'].user,
                subscribed_to=subscribed_to
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


class GETIngredientForRecipeSerializer(ModelSerializer):
    ingredients = IngredientSerializer(
        read_only=True
    )

    class Meta:
        model = IngredientAmountForRecipe
        fields = (
            'ingredients',
            'amount'
        )
        read_only_fields = (fields,)


class IngredientForRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmountForRecipe
        fields = (
            'id',
            'amount'
        )


class GETRecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = GETIngredientForRecipeSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
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


class RecipeSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientForRecipeSerializer(
        many=True,
        source='recipe_amount'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_amount')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_object = ingredient['id']
            IngredientAmountForRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_object,
                amount=ingredient['amount']
            )
        return recipe

    def to_representation(self, instance):
        return GETRecipeSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeSectionSerializer(ModelSerializer):
    # recipe = RecipeSerializer()

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
