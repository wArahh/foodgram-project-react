from djoser.serializers import UserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import (CharField, EmailField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)

from foodgram.models import (FavoriteRecipe, Follow, Ingredient,
                             IngredientAmountForRecipe, Recipe,
                             RecipeShoppingCart, Tag, User)
from .fields import Base64ImageField
from .mixins import IsSubscriberMixin

FIELD_INGREDIENTS_MUST_BE_SET = (
    'Поле "ingredients обязательно для обновления рецепта')
CANNOT_SENT_NULL_INGREDIENT_LIST = 'Нельзя передать пустой список ингредиентов'
FIELD_TAGS_MUST_BE_SET = "Поле 'tags' обязательно для обновления рецепта"
CANNOT_SENT_NULL_TAG_LIST = 'Нельзя передать пустой список тегов'
CANNOT_ADD_REPETITIVE_INGREDIENTS = (
    'Нельзя добавлять повторяющиеся ингредиенты'
)
CANNOT_ADD_REPETITIVE_TAGS = 'Нельзя добавлять повторяющиеся теги'


class CustomUserSerializer(UserSerializer, IsSubscriberMixin):
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
        return self.is_subscribed(subscribed_to)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class GETIngredientForRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(
        source='ingredient.id'
    )
    name = ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmountForRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientForRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmountForRecipe
        fields = (
            'id',
            'amount'
        )


class GETRecipeSerializer(ModelSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = GETIngredientForRecipeSerializer(
        many=True,
        source='recipe_amount'
    )
    author = CustomUserSerializer(
        read_only=True
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

    def create_ingredients(self, recipe, ingredients):
        IngredientAmountForRecipe.objects.bulk_create(
            IngredientAmountForRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_amount')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def validate(self, recipe_data):
        if 'recipe_amount' not in recipe_data:
            raise ValidationError(FIELD_INGREDIENTS_MUST_BE_SET)
        if not recipe_data['recipe_amount']:
            raise ValidationError(CANNOT_SENT_NULL_INGREDIENT_LIST)
        if 'tags' not in recipe_data:
            raise ValidationError(FIELD_TAGS_MUST_BE_SET)
        elif not recipe_data['tags']:
            raise ValidationError(CANNOT_SENT_NULL_TAG_LIST)
        ingredients_id_list = []
        tags_id_list = []
        for ingredient_object in recipe_data['recipe_amount']:
            ingredient_id = ingredient_object['id']
            if ingredient_id in ingredients_id_list:
                raise ValidationError(CANNOT_ADD_REPETITIVE_INGREDIENTS)
            ingredients_id_list.append(ingredient_id)
        for tag_id in recipe_data['tags']:
            if tag_id in tags_id_list:
                raise ValidationError(CANNOT_ADD_REPETITIVE_TAGS)
            tags_id_list.append(tag_id)
        return recipe_data

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_amount')
        IngredientAmountForRecipe.objects.filter(
            recipe=instance,
        ).delete()
        self.create_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GETRecipeSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(GETRecipeSerializer):
    class Meta(GETRecipeSerializer.Meta):
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(ModelSerializer, IsSubscriberMixin):
    email = EmailField(
        source='subscribed_to.email',
        read_only=True
    )
    id = IntegerField(
        source='subscribed_to.id',
        read_only=True
    )
    username = CharField(
        source='subscribed_to.username',
        read_only=True
    )
    first_name = CharField(
        source='subscribed_to.first_name',
        read_only=True
    )
    last_name = CharField(
        source='subscribed_to.last_name',
        read_only=True
    )
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, follow_obj):
        return self.is_subscribed(follow_obj.subscribed_to)

    def get_recipes(self, follow_object):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(
            author=follow_object.subscribed_to
        )
        if 'recipes_limit' in request.GET:
            recipes = recipes[:int(request.GET['recipes_limit'])]
        return ShortRecipeSerializer(
            recipes,
            many=True
        ).data

    def get_recipes_count(self, follow_object):
        return Recipe.objects.filter(
            author=follow_object.subscribed_to
        ).count()
